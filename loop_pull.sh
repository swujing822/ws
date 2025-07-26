#!/bin/bash

# 设置 PATH，确保 cron/系统能找到 git
#export PATH=/home/ec2-user/.local/bin:/home/ec2-user/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin

# 项目目录
REPO_DIR="."
# LOG_FILE="$REPO_DIR/log2.txt"

# 切换到项目目录
cd "$REPO_DIR" || {
  echo "[`date '+%F %T'`] ❌ 目录不存在: $REPO_DIR" # >> "$LOG_FILE"
  exit 1
}

echo "[`date '+%F %T'`] ▶️ 启动循环 git pull ..." # >> "$LOG_FILE"

# 无限循环，每次间隔 30 秒
while true; do
  echo "[`date '+%F %T'`] 🔄 检查更新..." # >> "$LOG_FILE"

  git fetch >> "$LOG_FILE" 2>&1

  # 检查是否有更新（与 origin/main 比较）
  COUNT=$(git rev-list HEAD...origin/main --count)

  if [ "$COUNT" -gt 0 ]; then
    echo "[`date '+%F %T'`] ⬇️ 检测到更新，执行 git pull" #  >> "$LOG_FILE"
    git pull >> "$LOG_FILE" 2>&1
  else
    echo "[`date '+%F %T'`] ✅ 无更新"# #  >> "$LOG_FILE"
  fi

  # 等待 30 秒
  sleep 30
done