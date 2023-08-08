import os
import random
import sys
import time

import requests

# 定义三种主要坐标系
# WGS84：GPS全球卫星定位系统使用的坐标系。
# GCJ02：火星坐标系，由中国国家测绘局制订的坐标系统。
# BD09：百度地图所使用的坐标体系。

# 百度地图的访问密钥
ak = '1ZtwxRT5sUDd6jaj0c7sCpjy9zXTl10O'


# 将经纬度转换成百度坐标系
def bd_latlng2xy(zoom, latitude, longitude):
    url = "https://api.map.baidu.com/geoconv/v1/"
    # 详细参数可见 https://lbs.baidu.com/faq/api?title=webapi/guide/changeposition-base
    params = {
        "coords": str(longitude) + ',' + str(latitude),
        "from": "5",
        "to": "6",
        "ak": ak,
    }
    response = requests.get(url=url, params=params)
    result = response.json()
    print('result:', result)
    loc = result["result"][0]
    res = 2 ** (18 - zoom)  # 计算缩放比例
    x = loc['x'] / res
    y = loc['y'] / res
    return x, y


# 下载地图切片
def download_tiles(city, zoom, latitude_start, latitude_stop, longitude_start, longitude_stop, satellite=True):
    # 创建保存目录，每个城市有单独的子目录
    root_save = os.path.join("tiles", city)
    os.makedirs(root_save, exist_ok=True)

    # 获取坐标转换
    start_x, start_y = bd_latlng2xy(zoom, latitude_start, longitude_start)
    stop_x, stop_y = bd_latlng2xy(zoom, latitude_stop, longitude_stop)

    # 计算切片范围
    start_x = int(start_x // 256)
    start_y = int(start_y // 256)
    stop_x = int(stop_x // 256)
    stop_y = int(stop_y // 256)

    if start_x >= stop_x or start_y >= stop_y:
        print("Invalid coordinates range")
        return

    print("x range", start_x, stop_x)
    print("y range", start_y, stop_y)

    # 循环下载每个切片
    for x in range(start_x, stop_x):
        for y in range(start_y, stop_y):
            if satellite:
                # 卫星图像URL
                url = f"http://shangetu0.map.bdimg.com/it/u=x={x};y={y};z={zoom};v=009;type=sate&fm=46&udt=20150504&app=webearth2&v=009&udt=20150601"
                filename = f"{zoom}_{x}_{y}_s.jpg"
            else:
                # 道路图像URL
                url = f'http://online3.map.bdimg.com/tile/?qt=tile&x={x}&y={y}&z={zoom}&styles=pl&scaler=1&udt=20180810'
                filename = f"{zoom}_{x}_{y}_r.png"

            filename = os.path.join(root_save, filename)
            print('filename', filename)

            # 检查文件是否存在，如不存在则下载
            if not os.path.exists(filename):
                try:
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()
                    print("-- saving", filename)
                    with open(filename, 'wb') as f:
                        f.write(response.content)

                    # 休眠以减轻服务器负担
                    time.sleep(1 + random.random())
                except requests.RequestException as e:
                    print("--", filename, "->", e)
                    sys.exit(1)


def main():
    # 定义城市的经纬度范围
    # 坐标拾取可见:https://api.map.baidu.com/lbsapi/getpoint/index.html
    cities = {
        'Beijing': (39.7555, 40.1536, 116.0392, 116.7914),
        'Shanghai': (30.975, 31.5149, 121.1016, 121.8044),
        'Guangzhou': (22.9391, 23.3967, 113.1016, 113.6777),
        'Shenzhen': (22.4486, 22.8456, 113.7516, 114.6166)
    }

    zoom = 19  # 缩放级别
    satellite = True  # 卫星图(如果为False，则下载道路图像)

    # 遍历城市并下载相应的卫星图
    for city, coordinates in cities.items():
        print(f"Downloading tiles for {city}...")
        lat_start, lat_stop, lon_start, lon_stop = coordinates
        download_tiles(city, zoom, lat_start, lat_stop, lon_start, lon_stop, satellite)


if __name__ == "__main__":
    main()
