from osgeo import gdal


def get_value_at_coords(file_path, lon, lat):
    # 打开数据集
    dataset = gdal.Open(file_path)

    # 获取地理转换参数
    transform = dataset.GetGeoTransform()

    # 计算像素位置
    col = int((lon - transform[0]) / transform[1])
    row = int((lat - transform[3]) / transform[5])

    # 获取数据
    band = dataset.GetRasterBand(1)
    data = band.ReadAsArray(col, row, 1, 1)

    return data[0, 0]


# 使用示例
file_path = "/Users/zhongsiru/project/src/dataset/gdp2019/gdp2019/w001001.adf"  # 这是主数据文件的路径
lon, lat = 120.5, 30.5  # 你想查询的经纬度
value = get_value_at_coords(file_path, lon, lat)
print(f"Value at ({lon}, {lat}): {value}")

