import rasterio

# 定义要读取的tif文件路径
tif_path = "/Users/zhongsiru/project/src/dataset/odiac/2021/odiac2022_1km_excl_intl_2112.tif"

# 定义四个城市及其对应的坐标范围
cities = {
    'Beijing': (39.7555, 40.1536, 116.0392, 116.7914),
    'Shanghai': (30.975, 31.5149, 121.1016, 121.8044),
    'Guangzhou': (22.9391, 23.3967, 113.1016, 113.6777),
    'Shenzhen': (22.4486, 22.8456, 113.7516, 114.6166)
}

with rasterio.open(tif_path) as src:
    # 读取tif文件的第一层数据
    co2_data = src.read(1)

    # 打印数据的最小和最大值
    print(co2_data.min(), co2_data.max())

    # 打印tif文件的仿射变换信息
    print(src.transform)

    # 循环处理每个城市
    for city, coordinates in cities.items():
        lat_start, lat_stop, lon_start, lon_stop = coordinates

        # 获取城市坐标范围的起始和结束像素位置
        row_start, col_start = src.index(lon_start, lat_stop)
        row_stop, col_stop = src.index(lon_stop, lat_start)

        # 读取该城市范围内的数据
        city_data = co2_data[row_start:row_stop, col_start:col_stop]

        # 计算并打印城市的平均碳排放值
        avg_emission = city_data.mean()
        print(f"Average emission for {city}: {avg_emission}")
