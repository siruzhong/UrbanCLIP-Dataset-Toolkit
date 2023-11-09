import rasterio
from pyproj import Transformer


def get_gdp_at_location(tif_path, lon, lat):
    with rasterio.open(tif_path) as src:
        # 创建坐标转换器
        transformer = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)

        # 将经纬度坐标转换为投影坐标
        x, y = transformer.transform(lon, lat)

        # 将投影坐标转换为行列坐标
        row, col = src.index(x, y)

        # 检查索引是否在有效范围内
        if 0 <= row < src.height and 0 <= col < src.width:
            # 读取该位置的数据
            gdp_value = src.read(1)[row, col]
        else:
            return None  # 或者返回其他默认值，如0

    return gdp_value


# 使用示例
tif_path = "/Users/zhongsiru/project/src/dataset/gdp/2010/cngdp2010.tif"
lon, lat = 116.4074, 39.9042  # 例如：北京的经纬度
gdp_value = get_gdp_at_location(tif_path, lon, lat)
print(f"GDP value at ({lon}, {lat}) is: {gdp_value}")
