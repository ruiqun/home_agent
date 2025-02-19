#!/bin/bash

# 定义 SSH 连接所需的参数
LOCAL_PORT=8889
REMOTE_HOST=127.0.0.1
REMOTE_PORT=8000
SSH_PORT=38810
SSH_USER=root
SSH_SERVER=connect.westc.gpuhub.com

# 构建 SSH 命令
SSH_COMMAND="ssh -L ${LOCAL_PORT}:${REMOTE_HOST}:${REMOTE_PORT} -p ${SSH_PORT} ${SSH_USER}@${SSH_SERVER}"

# 执行 SSH 命令
echo "正在建立 SSH 隧道..."
eval $SSH_COMMAND