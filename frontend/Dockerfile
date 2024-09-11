# 设置基础镜像
FROM node:16.20.2 as builder

# 设置工作目录
WORKDIR /frontend

# 复制package.json和package-lock.json文件
COPY ./package*.json ./

# 安装项目依赖
RUN npm config set registry https://registry.npmmirror.com
RUN npm install

# 复制所有源代码到工作目录
COPY . .

# 执行构建命令
RUN npm run build

# 设置基础镜像
FROM nginx:1.21

# 重命名nginx.conf为default.conf
COPY --from=builder /frontend/dist /usr/share/nginx/html
COPY default.conf /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/nginx.conf

# 暴露端口
EXPOSE 80

# 启动nginx服务
CMD ["nginx", "-g", "daemon off;"]
