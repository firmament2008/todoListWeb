#!/bin/bash

# 启动后端服务
echo "正在启动后端服务..."
source venv/bin/activate
python app.py & 

# 等待后端服务启动
sleep 3

# 启动前端服务
echo "正在启动前端服务..."
cd frontend
npm run dev