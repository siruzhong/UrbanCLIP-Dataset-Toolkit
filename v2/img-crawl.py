import csv
import math
import os
import random
import time
from concurrent.futures import ThreadPoolExecutor

import requests
from PIL import Image
from PIL import ImageDraw
from loguru import logger
from shapely import Polygon
from shapely.geometry import box
from shapely.wkt import loads

# Access key for Baidu Maps
# Configuration viewable at: https://lbsyun.baidu.com/apiconsole/center#/home
ak = '1ZtwxRT5sUDd6jaj0c7sCpjy9zXTl10O'


def preprocess(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()

    # 将NBSP替换为空格
    file_content = file_content.replace('\xa0', ' ')

    # 将替换后的内容写回文件
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(file_content)


# Convert latitude and longitude to Baidu map coordinates
def bd_latlng2xy(zoom, latitude, longitude):
    url = "https://api.map.baidu.com/geoconv/v1/"
    # For detailed parameters, refer to https://lbs.baidu.com/faq/api?title=webapi/guide/changeposition-base
    params = {
        "coords": str(longitude) + ',' + str(latitude),
        "from": "5",
        "to": "6",
        "ak": ak,
    }
    response = requests.get(url=url, params=params)
    result = response.json()
    logger.info(f'result: {result}')
    loc = result["result"][0]
    res = 2 ** (18 - zoom)  # Calculate the scaling factor
    x = loc['x'] / res
    y = loc['y'] / res
    return x, y


# 高德坐标转百度（传入经度、纬度）
def convert_gd_to_baidu(gg_lng, gg_lat):
    X_PI = math.pi * 3000.0 / 180.0
    x = gg_lng
    y = gg_lat
    z = math.sqrt(x * x + y * y) + 0.00002 * math.sin(y * X_PI)
    theta = math.atan2(y, x) + 0.000003 * math.cos(x * X_PI)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return {
        "bd_lat": bd_lat,
        "bd_lng": bd_lng
    }


# Download map tiles
def download_tiles(city, zoom, latitude_start, latitude_stop, longitude_start, longitude_stop, satellite=True):
    # Create a save directory with a separate subdirectory for each city
    root_save = os.path.join("img/tiles", city)
    os.makedirs(root_save, exist_ok=True)

    # Perform coordinate conversion
    start_x, start_y = bd_latlng2xy(zoom, latitude_start, longitude_start)
    stop_x, stop_y = bd_latlng2xy(zoom, latitude_stop, longitude_stop)

    # Calculate tile range
    start_x = int(start_x // 256)
    start_y = int(start_y // 256)
    stop_x = int(stop_x // 256) + 1  # Make sure it is at least 1 greater than start_x
    stop_y = int(stop_y // 256) + 1  # Make sure it is at least 1 greater than start_y

    logger.info(f'x range: {start_x} to {stop_x}')
    logger.info(f'y range: {start_y} to {stop_y}')

    # Loop to download each tile, using a thread pool of custom size, e.g., max_workers=666
    tile_paths = []
    with ThreadPoolExecutor(max_workers=666) as executor:
        futures = []
        for x in range(start_x, stop_x):
            for y in range(start_y, stop_y):
                tile_path = os.path.join(root_save, f"{zoom}_{x}_{y}_s.jpg")
                tile_paths.append(tile_path)
                futures.append(executor.submit(download_tile, x, y, zoom, satellite, root_save))
        # Wait for all threads to complete
        for future in futures:
            future.result()

    return tile_paths, (stop_x - start_x, stop_y - start_y)


# Download an individual map tile
def download_tile(x, y, zoom, satellite, root_save):
    if satellite:
        # Satellite imagery URL
        url = f"http://shangetu0.map.bdimg.com/it/u=x={x};y={y};z={zoom};v=009;type=sate&fm=46&udt=20150504&app=webearth2&v=009&udt=20150601"
        filename = f"{zoom}_{x}_{y}_s.jpg"
    else:
        # Road map image URL
        url = f'http://online3.map.bdimg.com/tile/?qt=tile&x={x}&y={y}&z={zoom}&styles=pl&scaler=1&udt=20180810'
        filename = f"{zoom}_{x}_{y}_r.png"

    filename = os.path.join(root_save, filename)

    # Check if the file exists, download if it doesn't
    if not os.path.exists(filename):
        try:
            logger.info(f'downloading filename: {filename}')
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            logger.info(f"-- saving {filename}")
            with open(filename, 'wb') as f:
                f.write(response.content)
            time.sleep(random.random())  # Random sleep to reduce server load
        except requests.RequestException as e:
            logger.info(f"-- {filename} -> {e}")
    else:
        logger.info(f"File already exists: {filename}")


def parse_aoi_file(file_path):
    aois = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            wkt = row['wkt']
            # 转换WKT中的坐标点
            polygon = loads(wkt)
            converted_polygon = []
            for point in polygon.exterior.coords:
                lat, lon = point[1], point[0]
                conversion_result = convert_gd_to_baidu(lon, lat)
                converted_lat = conversion_result["bd_lat"]
                converted_lon = conversion_result["bd_lng"]
                converted_polygon.append((converted_lon, converted_lat))
            # 创建转换后的多边形
            converted_polygon = Polygon(converted_polygon)
            aoi = {
                'address': row['aoi_address'],
                'centroid': row['centroid'],
                'polygon': converted_polygon,
                'bounding_square': get_bounding_square(converted_polygon)
            }
            aois.append(aoi)
    return aois


def get_bounding_square(polygon):
    minx, miny, maxx, maxy = polygon.bounds
    return box(minx, miny, maxx, maxy)


def stitch_tiles(tile_paths, grid_size):
    if not tile_paths:
        logger.info("No tiles to stitch")
        return

    tile_width, tile_height = Image.open(tile_paths[0]).size
    total_width = tile_width * grid_size[0]
    total_height = tile_height * grid_size[1]
    stitched_image = Image.new('RGB', (total_width, total_height))

    # 根据文件名中的x和y坐标对瓦片路径进行排序
    # 首先提取 x 和 y 的值，然后按 y 升序、x 升序排列
    tile_paths.sort(key=lambda path: (int(path.split('_')[2]), int(path.split('_')[1])))

    for i, tile_path in enumerate(tile_paths):
        with Image.open(tile_path) as tile:
            # 计算瓦片在拼接图像中的位置
            x_index = i % grid_size[0]
            y_index = i // grid_size[0]
            x = x_index * tile_width
            y = (grid_size[1] - 1 - y_index) * tile_height  # 从底部开始计算 y 坐标
            stitched_image.paste(tile, (x, y))

    return stitched_image


def apply_mask(stitched_image, aoi_polygon, tile_bounds, save_path):
    # 将AOI多边形的地理坐标转换为图像上的像素坐标
    def convert_coords(coords):
        min_lon, min_lat, max_lon, max_lat = tile_bounds
        x_percent = (coords[0] - min_lon) / (max_lon - min_lon)
        y_percent = (max_lat - coords[1]) / (max_lat - min_lat)
        return (x_percent * stitched_image.width, y_percent * stitched_image.height)

    aoi_coords = [convert_coords(point) for point in aoi_polygon.exterior.coords]

    # 创建一个遮罩层，用黑色填充多边形外的区域
    mask = Image.new('L', stitched_image.size, 0)
    draw = ImageDraw.Draw(mask)
    # 多边形内部设置为白色（255），表示不进行遮罩处理
    draw.polygon(aoi_coords, fill=255)
    black_background = Image.new('RGB', stitched_image.size)
    # 应用遮罩，多边形外的部分会变为黑色
    masked_image = Image.composite(stitched_image, black_background, mask)
    masked_image.save(save_path)


def main():
    preprocess('aoi.csv')
    aois = parse_aoi_file('aoi.csv')
    zoom = 16  # Coarse zoom level
    satellite = True  # Satellite image

    for aoi in aois:
        square = aoi['bounding_square']
        lon_start, lat_start, lon_stop, lat_stop = square.bounds
        tile_paths, grid_size = download_tiles(aoi['address'], zoom, lat_start, lat_stop, lon_start, lon_stop, satellite)

        # Stitch tiles and save the stitched image
        stitched_image = stitch_tiles(tile_paths, grid_size)
        if stitched_image:
            stitched_sava_path = os.path.join("img/stitched_images", f"{aoi['address']}.jpg")
            os.makedirs(os.path.dirname(stitched_sava_path), exist_ok=True)
            stitched_image.save(stitched_sava_path)
            logger.info(f"Stitched image saved to {stitched_sava_path}")

            # # Calculate the adjusted tile bounds
            # if grid_size[0] > 1:
            #     tile_lon_delta = (lon_stop - lon_start) / (grid_size[0] - 1)
            #     adjusted_lon_stop = lon_start + tile_lon_delta * grid_size[0]
            # else:
            #     adjusted_lon_stop = lon_stop  # 没有额外的瓦片，保持原始的stop坐标
            #
            # if grid_size[1] > 1:
            #     tile_lat_delta = (lat_stop - lat_start) / (grid_size[1] - 1)
            #     adjusted_lat_stop = lat_start + tile_lat_delta * grid_size[1]
            # else:
            #     adjusted_lat_stop = lat_stop  # 没有额外的瓦片，保持原始的stop坐标

            # Apply the mask based on AOI polygon and save the final image
            tile_bounds = (lon_start, lat_start, lon_stop, lat_stop)
            # tile_bounds = (lon_start, lat_start, adjusted_lon_stop, adjusted_lat_stop)
            masked_sava_path = os.path.join("img/masked_images", f"{aoi['address']}.jpg")
            os.makedirs(os.path.dirname(masked_sava_path), exist_ok=True)
            apply_mask(stitched_image, aoi['polygon'], tile_bounds, masked_sava_path)
            logger.info(f"Masked image saved to {masked_sava_path}")


if __name__ == "__main__":
    main()
