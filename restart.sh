#!/bin/bash

# 停止所有服务
./stop.sh

# 等待服务完全停止
sleep 2

# 重新启动所有服务
./start.sh

echo "所有服务已重新启动"