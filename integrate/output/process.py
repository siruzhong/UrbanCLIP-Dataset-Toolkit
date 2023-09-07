import csv
import os

zoom = 16

csv_path = "/Users/zhongsiru/project/src/satellite-image-crawl/integrate/output/integrated_satellite_data.csv"
temp_path = os.path.join(os.path.dirname(csv_path), "temp.csv")

with open(csv_path, 'r') as csvfile, open(temp_path, 'w', newline='') as temp_file:
    reader = csv.DictReader(csvfile)
    writer = csv.DictWriter(temp_file, fieldnames=reader.fieldnames)
    writer.writeheader()

    for row in reader:
        coords = row['BD09 coordinate']
        # 提取坐标值
        x, y = coords.replace("(", "").replace(")", "").split(',')
        # 移除多余的转换，并只保存原始的x和y值
        new_coords = f"({int(float(x) / (256 * 2 ** (18 - zoom)))},{int(float(y) / (256 * 2 ** (18 - zoom)))})"
        row['BD09 coordinate'] = new_coords
        writer.writerow(row)

# 替换原始文件
os.replace(temp_path, csv_path)
