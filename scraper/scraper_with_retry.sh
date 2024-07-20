#!/bin/bash

MAX_RETRIES=999
DELAY=60  # 重试间隔时间（秒）
LOG_DIR="/home/ubuntu/twitter/scraper"
SCRAPER_SCRIPT="$LOG_DIR/old_scraper.py"
DROP_DUPLICATE_SCRIPT="$LOG_DIR/drop_duplicate.py"
SRC_DIR="/home/ubuntu/tweets"

for ((i=1; i<=$MAX_RETRIES; i++))
do
    echo "$(date): 尝试 $i 执行任务。" >> "$LOG_DIR/scraper.log"
    
    cd "$LOG_DIR" && /usr/bin/python "$SCRAPER_SCRIPT" >> "$LOG_DIR/scraper.log" 2>&1
    
    SCRIPT_EXIT_STATUS=$?
    echo "$(date): old_scraper.py 脚本退出状态: $SCRIPT_EXIT_STATUS" >> "$LOG_DIR/scraper.log"
    
    if [ $SCRIPT_EXIT_STATUS -eq 0 ]; then
        echo "$(date): 任务成功执行。" >> "$LOG_DIR/scraper.log"

        # 执行合并去重程序
        echo "$(date): 执行 drop_duplicate.py 脚本。" >> "$LOG_DIR/scraper.log"
        /usr/bin/python "$DROP_DUPLICATE_SCRIPT" >> "$LOG_DIR/drop_duplicate.log" 2>&1

        DROP_DUPLICATE_EXIT_STATUS=$?
        echo "$(date): drop_duplicate.py 脚本退出状态: $DROP_DUPLICATE_EXIT_STATUS" >> "$LOG_DIR/scraper.log"

        if [ $DROP_DUPLICATE_EXIT_STATUS -eq 0 ]; then
            # 删除源文件夹及其内容
            echo "$(date): 删除源文件夹及其内容。" >> "$LOG_DIR/scraper.log"
            rm -rf "$SRC_DIR"
            echo "$(date): 源文件夹已删除。" >> "$LOG_DIR/scraper.log"
        else
            echo "$(date): drop_duplicate.py 执行失败，未删除源文件夹。" >> "$LOG_DIR/scraper.log"
        fi

        exit 0
    else
        echo "$(date): 尝试 $i 执行任务失败，等待 $DELAY 秒后重试。" >> "$LOG_DIR/scraper.log"
        sleep $DELAY
    fi
done

echo "$(date): 已达到最大重试次数 $MAX_RETRIES。" >> "$LOG_DIR/scraper.log"
exit 1