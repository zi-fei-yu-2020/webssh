import json
import sys
import os
import logging
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from io import BytesIO, StringIO
import paramiko
from threading import Thread
from .models import TerminalServer
from django.http.request import QueryDict
from django.conf import settings

SSH_LOG_PATH = os.path.join(settings.BASE_DIR, 'logs', 'terminal.log')
logging.basicConfig(filename=SSH_LOG_PATH, level=logging.WARNING,
                    format='%(asctime)s %(levelname)s %(message)s')

def get_host_info(id):
    instance = TerminalServer.objects.filter(id=id).first()
    return instance if instance else None


class TerminalConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ssh_client = None
        self.chan = None
        self.id = None
        self.ssh_info = None

    def connect(self):
        params = self.scope["query_string"].decode()
        dict_params = QueryDict(query_string=params, encoding='utf-8')
        self.id = dict_params.get('id', None)
        if not self.id:
            self.close()
            return

        self.ssh_info = get_host_info(self.id)
        if not self.ssh_info:
            self.close()
            return

        self.accept()
        self.initssh()

    def get_client(self):
        paramiko.util.log_to_file(SSH_LOG_PATH)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            if self.ssh_info.type == 0:
                ssh.connect(
                    hostname=self.ssh_info.host,
                    port=self.ssh_info.port,
                    username=self.ssh_info.username,
                    password=self.ssh_info.password
                )
            else:
                tmppkey = self.ssh_info.pkey.encode('utf-8')
                p_file = BytesIO(tmppkey) if sys.version_info[0] == 2 else StringIO(tmppkey)
                pkey = paramiko.RSAKey.from_private_key(p_file)
                ssh.connect(
                    hostname=self.ssh_info.host,
                    port=self.ssh_info.port,
                    username=self.ssh_info.username,
                    pkey=pkey
                )
        except paramiko.AuthenticationException:
            logging.warning("SSH 认证失败")
            self.send(text_data='SSH 认证失败，请检查凭证。\r\n')
            self.close()
        except paramiko.SSHException as e:
            logging.warning(f"SSH 异常: {str(e)}")
            self.send(text_data='SSH 连接失败，请稍后重试。\r\n')
            self.close()
        except TimeoutError:
            logging.warning("SSH 连接超时")
            self.send(text_data='SSH 连接超时，请检查网络或终端。\r\n')
            self.close()
        except Exception as e:
            logging.error(f"SSH 未知错误: {str(e)}")
            self.send(text_data='SSH 连接时发生未知错误。\r\n')
            self.close()
        return ssh

    def loop_read(self):
        while True:
            data = self.chan.recv(1024)
            if not data:
                self.close()
                break
            self.send(bytes_data=data)

    def initssh(self):
        self.send(bytes_data=b'Connecting ...\r\n')
        try:
            self.ssh_client = self.get_client()
            if self.ssh_client is None:
                return

            self.chan = self.ssh_client.invoke_shell(term='xterm')
            self.chan.transport.set_keepalive(30)
            rv = Thread(target=self.loop_read)
            rv.start()

        except Exception as e:
            logging.error(f"SSH 初始化失败: {str(e)}")
            self.send(text_data='SSH 初始化失败。\r\n')
            self.close()

    def disconnect(self, close_code):
        try:
            if self.chan:
                self.chan.close()
            if self.ssh_client:
                self.ssh_client.close()
        except Exception as e:
            logging.error(f"断开连接时出错: {str(e)}")

    def receive(self, text_data=None, bytes_data=None):
        data = text_data or bytes_data
        if len(data) > 10 and data.find('"resize":1') != -1:
            self.resize(data)
        else:
            if self.chan:
                self.chan.send(data)
            else:
                self.close()

    def resize(self, data):
        try:
            data = json.loads(data)
            self.chan.resize_pty(width=data['cols'], height=data['rows'])
        except Exception as e:
            logging.error(f"调整终端大小时出错: {str(e)}")
