from rest_framework import serializers
from .models import TerminalServer


class TerminalServerSerializer(serializers.ModelSerializer):
    """
    终端服务器列表后台 简单序列化器
    """
    typename = serializers.SerializerMethodField()

    def get_typename(self, obj: TerminalServer) -> str:
        return obj.get_type_display()

    class Meta:
        model = TerminalServer
        fields = ['id', 'host', 'port', 'remark', 'username', 'password', 'typename', 'type', 'created_time']
        read_only_fields = ['id']


class TerminalCreateServerSerializer(serializers.ModelSerializer):
    """
    终端服务器列表创建序列化器
    """

    class Meta:
        model = TerminalServer
        fields = ['host', 'port', 'remark', 'username', 'password', 'type', 'created_time']


class TerminalUpdateServerSerializer(serializers.ModelSerializer):
    """
    终端服务器列表更新序列化器
    """

    class Meta:
        model = TerminalServer
        fields = ['host', 'port', 'remark', 'username', 'password', 'type']
        read_only_fields = ['id']
