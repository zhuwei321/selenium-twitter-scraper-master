import os
from datetime import datetime

import pandas as pd
import shutil

# 配置源文件夹和目标文件夹
source_folder = '/home/ubuntu/tweets'
destination_folder = '/home/ubuntu/tweets_combined'


# 检查目标文件夹是否存在，不存在则创建
if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)

# 初始化一个空 DataFrame 用于存放合并后的数据
combined_df = pd.DataFrame()

# 遍历源文件夹中的所有 CSV 文件
for filename in os.listdir(source_folder):
    if filename.endswith('.csv'):
        file_path = os.path.join(source_folder, filename)
        df = pd.read_csv(file_path)
        combined_df = pd.concat([combined_df, df], ignore_index=True)

# 去重
combined_df.drop_duplicates(subset=['Tweet Link'])

now = datetime.now()
current_time = now.strftime("%Y-%m-%d_%H-%M-%S")
combined_csv_name = f"{current_time}_tweets_1-{combined_df.shape[0]}_1.csv"

# 保存去重后的 CSV 文件到目标文件夹
combined_csv_path = os.path.join(destination_folder, combined_csv_name)
combined_df.to_csv(combined_csv_path, index=False)

print(f"合并并去重后的文件已保存到：{combined_csv_path}")
print(f"源文件夹已删除：{source_folder}")


