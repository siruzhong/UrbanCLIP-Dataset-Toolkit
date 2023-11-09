import os
import random
import time
from concurrent.futures import ThreadPoolExecutor

import requests
from loguru import logger

"""
Define three main coordinate systems
    - WGS84: The coordinate system used by the GPS global satellite positioning system.
    - GCJ02: Mars coordinate system, the coordinate system formulated by the State Bureau of Surveying and Mapping of China.
    - BD09: The coordinate system used by Baidu Maps.
"""

# Access key for Baidu Maps
# Configuration viewable at: https://lbsyun.baidu.com/apiconsole/center#/home
ak = 'Replace with your own Baidu ak'


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


# Download map tiles
def download_tiles(city, zoom, latitude_start, latitude_stop, longitude_start, longitude_stop, satellite=True):
    # Create a save directory with a separate subdirectory for each city
    root_save = os.path.join("tiles", city)
    os.makedirs(root_save, exist_ok=True)

    # Perform coordinate conversion
    start_x, start_y = bd_latlng2xy(zoom, latitude_start, longitude_start)
    stop_x, stop_y = bd_latlng2xy(zoom, latitude_stop, longitude_stop)

    # Calculate tile range
    start_x = int(start_x // 256)
    start_y = int(start_y // 256)
    stop_x = int(stop_x // 256)
    stop_y = int(stop_y // 256)

    if start_x >= stop_x or start_y >= stop_y:
        logger.info("Invalid coordinates range")
        return

    logger.info(f'x range: {start_x} to {stop_x}')
    logger.info(f'y range: {start_y} to {stop_y}')

    # Loop to download each tile, using a thread pool of custom size, e.g., max_workers=666
    with ThreadPoolExecutor(max_workers=666) as executor:
        futures = []
        for x in range(start_x, stop_x):
            for y in range(start_y, stop_y):
                futures.append(executor.submit(download_tile, x, y, zoom, satellite, root_save))
        # Wait for all threads to complete
        for future in futures:
            future.result()


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


def main():
    # Define the latitude and longitude range of cities
    # Coordinate picker viewable at: https://api.map.baidu.com/lbsapi/getpoint/index.html
    cities = {
        'Beijing': (39.7555, 40.1536, 116.0392, 116.7914),
        'Shanghai': (30.975, 31.5149, 121.1016, 121.8044),
        'Guangzhou': (22.9391, 23.3967, 113.1016, 113.6777),
        'Shenzhen': (22.4486, 22.8456, 113.7516, 114.6166)
    }

    zoom = 16  # Coarse zoom level
    # zoom = 19  # Fine zoom level
    satellite = True  # Satellite image (if False, download road images)

    # Loop through the cities and download the corresponding satellite images
    for city, coordinates in cities.items():
        logger.info(f"Downloading tiles for {city}...")
        lat_start, lat_stop, lon_start, lon_stop = coordinates
        download_tiles(city, zoom, lat_start, lat_stop, lon_start, lon_stop, satellite)


if __name__ == "__main__":
    main()
