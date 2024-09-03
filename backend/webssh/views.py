from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from .models import TerminalServer
from .serializers import (
    TerminalServerSerializer,
    TerminalCreateServerSerializer,
    TerminalUpdateServerSerializer
)


# 列表视图
@api_view(["GET"])
def list_terminal_servers(request):
    """
    列出和搜索终端服务器
    """
    search_query = request.GET.get('search')
    queryset = TerminalServer.objects.all().order_by('-created_time')

    # 如果存在search查询参数，进一步过滤
    if search_query:
        search_fields = ('host',)  # 替换为你实际想要搜索的字段
        search_conditions = {f"{field}__icontains": search_query for field in search_fields}
        queryset = queryset.filter(**search_conditions)

    # 分页功能
    page_number = request.GET.get('page', 1)
    items_per_page = request.GET.get('page_size', 10)
    paginator = Paginator(queryset, items_per_page)

    try:
        page = paginator.page(page_number)
    except EmptyPage:
        return Response({'detail': 'Page not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = TerminalServerSerializer(page, many=True)
    return Response({
        "code": 200,
        "message": "获取成功",
        "result": {
            "data": serializer.data,
            "totalCount": paginator.count
        }
    })


# 创建视图
@api_view(["POST"])
def create_terminal_server(request):
    serializer = TerminalCreateServerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "code": 200,
            "message": "新增成功",
            "result": serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 检索单个终端服务器
@api_view(["GET"])
def retrieve_terminal_server(request, pk):
    try:
        instance = TerminalServer.objects.get(pk=pk)
    except TerminalServer.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = TerminalServerSerializer(instance)
    return Response({
        "code": 200,
        "message": "获取成功",
        "result": serializer.data
    })


# 更新视图
@api_view(["PUT"])
def update_terminal_server(request, pk):
    try:
        instance = TerminalServer.objects.get(pk=pk)
    except TerminalServer.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = TerminalUpdateServerSerializer(instance, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "code": 200,
            "message": "更新成功",
            "result": serializer.data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 删除视图
@api_view(["DELETE"])
def delete_terminal_server(request, pk):
    try:
        instance = TerminalServer.objects.get(pk=pk)
    except TerminalServer.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    instance.delete()
    return Response({
        "code": 200,
        "message": "删除成功",
        "result": []
    })


# 批量删除视图
@api_view(["DELETE"])
def multiple_delete_terminal_servers(request):
    keys = request.data.get('keys', None)
    if not keys:
        return Response({"detail": "No keys provided."}, status=status.HTTP_400_BAD_REQUEST)

    TerminalServer.objects.filter(id__in=keys).delete()
    return Response({
        "code": 200,
        "message": "删除成功",
        "result": []
    })
