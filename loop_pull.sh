#!/bin/bash

# 设置 PATH，确保 cron/系统能找到 git
#export PATH=/home/ec2-user/.local/bin:/home/ec2-user/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin

# 项目目录
REPO_DIR="."
# LOG_FILE="$REPO_DIR/log2.txt"

# 切换到项目目录

echo "[`date '+%F %T'`] ▶️ 启动循环 git pull ..." # >> "$LOG_FILE"

# 无限循环，每次间隔 30 秒
while true; do
  echo "[`date '+%F %T'`] 🔄 检查更新..." # >> "$LOG_FILE"
  git pull
  
  # 等待 30 秒
  sleep 30
done