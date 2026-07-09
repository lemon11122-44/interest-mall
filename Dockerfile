FROM python:3.11-slim

WORKDIR /app

# 设置国内 pip 镜像加速
RUN pip config set global.index-url https://mirrors.tencent.com/pypi/simple/

# 先装依赖（利用缓存）
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ /app/

# 微信云托管会注入 PORT 环境变量，默认 80
EXPOSE 80

CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-80}
