FROM python:3.8

# 设置apt源为阿里云镜像
RUN echo "deb http://deb.debian.org/debian buster main" > /etc/apt/sources.list \
    && echo "deb-src http://deb.debian.org/debian buster main" >> /etc/apt/sources.list \
    && echo "deb http://security.debian.org/debian-security buster/updates main" >> /etc/apt/sources.list \
    && echo "deb-src http://security.debian.org/debian-security buster/updates main" >> /etc/apt/sources.list

RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list \
    && sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list

# 创建工作目录
RUN mkdir -p /usr/src/backend

# 复制项目文件和pip配置
COPY . /usr/src/backend/
COPY ./pip.conf /root/.pip/pip.conf

# 安装依赖
RUN pip install uwsgi \
    && pip install -r /usr/src/backend/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

WORKDIR /usr/src/backend

# 数据库迁移
RUN python manage.py makemigrations \
    && python manage.py migrate

# 安装 supervisord
RUN apt-get update && apt-get install -y supervisor

# 复制 supervisord 配置文件
COPY ./supervisord.conf /etc/supervisor/supervisord.conf

# 启动 supervisord 来管理多个进程
CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]
