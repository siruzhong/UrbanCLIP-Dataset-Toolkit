import csv
import os

# 输入CSV文件路径
csv_path = "/Users/zhongsiru/project/src/satellite-image-crawl/integrate/output/integrated_satellite_data.csv"
root_folder = "/Users/zhongsiru/project/src/satellite-image-crawl/integrate/output"

cities = ["Beijing", "Guangzhou", "Shanghai", "Shenzhen"]
city_data = {city: [] for city in cities}

# 读取CSV数据并分类到对应的城市
with open(csv_path, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        for city in cities:
            if city in row['satellite_img_name']:
                city_data[city].append(row)
                break

# 将每个城市的数据写入对应的CSV文件
for city, rows in city_data.items():
    city_folder = os.path.join(root_folder, city)
    os.makedirs(city_folder, exist_ok=True)  # 确保目录存在
    city_csv_path = os.path.join(city_folder, f"{city}.csv")

    with open(city_csv_path, 'w', newline='') as city_csv_file:
        fieldnames = ['satellite_img_name', 'BD09 coordinate', 'WGS84 coordinate',
                      'carbon_emissions (ton)', 'population (unit)', 'gdp (million yuan)']
        writer = csv.DictWriter(city_csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
