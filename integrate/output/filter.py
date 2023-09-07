import csv
import os

csv_path = "/Users/zhongsiru/project/src/satellite-image-crawl/integrate/output/integrated_satellite_data.csv"
temp_path = os.path.join(os.path.dirname(csv_path), "temp.csv")

with open(csv_path, 'r') as csvfile, open(temp_path, 'w', newline='') as temp_file:
    reader = csv.DictReader(csvfile)
    writer = csv.DictWriter(temp_file, fieldnames=reader.fieldnames)
    writer.writeheader()

    for row in reader:
        # 检查这三个字段的值是否都为0
        if not (float(row['carbon_emissions (ton)']) == 0 and
                float(row['population (unit)']) == 0 and
                float(row['gdp (million yuan)']) == 0):
            writer.writerow(row)

# 替换原始文件
os.replace(temp_path, csv_path)
