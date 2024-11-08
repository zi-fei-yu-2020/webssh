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

# 设置日志路径
SSH_LOG_PATH = os.path.join(settings.BASE_DIR, 'logs', 'terminal.log')
logging.basicConfig(filename=SSH_LOG_PATH, level=logging.WARNING,
                    format='%(asctime)s %(levelname)s %(message)s')

def get_host_info(id):
    """获取终端服务器信息"""
    instance = TerminalServer.objects.filter(id=id).first()
    return instance if instance else None

class TerminalConsumer(WebsocketConsumer):
    """WebSocket消费者，用于处理终端连接"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ssh_client = None
        self.chan = None
        self.id = None
        self.ssh_info = None

    def connect(self):
        """WebSocket连接处理"""
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

        logging.info(f"连接的终端信息：{self.ssh_info}")  # 记录终端信息，方便调试

        self.accept()
        self.initssh()

    def get_client(self):
        """获取SSH客户端连接"""
        paramiko.util.log_to_file(SSH_LOG_PATH)  # 将SSH日志记录到指定文件
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            if self.ssh_info.type == 0:
                # 使用密码连接
                logging.info(f"尝试使用密码连接：{self.ssh_info.host}:{self.ssh_info.port}")
                ssh.connect(
                    hostname=self.ssh_info.host,
                    port=self.ssh_info.port,
                    username=self.ssh_info.username,
                    password=self.ssh_info.password
                )
            else:
                # 使用私钥连接
                logging.info(f"尝试使用私钥连接：{self.ssh_info.host}:{self.ssh_info.port}")
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
            logging.warning("SSH认证失败")
            self.send(text_data='SSH 认证失败，请检查凭证。\r\n')
            self.close()
        except paramiko.SSHException as e:
            logging.warning(f"SSH异常: {str(e)}")
            self.send(text_data=f"SSH 异常: {str(e)}\r\n")  # 发送详细的异常信息
            self.close()
        except TimeoutError:
            logging.warning("SSH连接超时")
            self.send(text_data='SSH 连接超时，请检查网络或终端。\r\n')
            self.close()
        except Exception as e:
            logging.error(f"SSH未知错误: {str(e)}")
            self.send(text_data=f"SSH 连接时发生未知错误: {str(e)}\r\n")
            self.close()
        return ssh

    def loop_read(self):
        """循环读取SSH通道数据并发送到WebSocket客户端"""
        while True:
            data = self.chan.recv(1024)
            if not data:
                self.close()
                break
            self.send(bytes_data=data)

    def initssh(self):
        """初始化SSH连接"""
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
            self.send(text_data=f'SSH 初始化失败: {str(e)}\r\n')  # 发送详细错误信息到前端
            self.close()

    def disconnect(self, close_code):
        """WebSocket连接关闭时的处理"""
        try:
            if self.chan:
                self.chan.close()
            if self.ssh_client:
                self.ssh_client.close()
        except Exception as e:
            logging.error(f"断开连接时出错: {str(e)}")

    def receive(self, text_data=None, bytes_data=None):
        """接收来自前端的消息"""
        data = text_data or bytes_data
        if len(data) > 10 and data.find('"resize":1') != -1:
            self.resize(data)
        else:
            if self.chan:
                self.chan.send(data)
            else:
                self.close()

    def resize(self, data):
        """处理终端大小调整"""
        try:
            data = json.loads(data)
            self.chan.resize_pty(width=data['cols'], height=data['rows'])
        except Exception as e:
            logging.error(f"调整终端大小时出错: {str(e)}")
