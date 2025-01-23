#!/bin/bash

# 停止后端服务
echo "正在停止后端服务..."
pkill -f "python app.py"

# 停止前端服务
echo "正在停止前端服务..."
pkill -f "vite"

echo "所有服务已停止"