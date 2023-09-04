import os

import rasterio
import requests

# Baidu Map's access key
# Configuration visible at: https://lbsyun.baidu.com/apiconsole/center#/home
ak = '1ZtwxRT5sUDd6jaj0c7sCpjy9zXTl10O'
# Path of the tif file to read
tif_path = "/Users/zhongsiru/project/src/dataset/odiac/2021/odiac2022_1km_excl_intl_2112.tif"


def bd_xy2latlng(zoom, x, y):
    """
    Convert BD09 pixel coordinates to WGS84 lat/lng for a given zoom level.
    """
    res = 2 ** (18 - zoom)  # Calculate the zoom scale
    bd_x = x * 256 * res
    bd_y = y * 256 * res

    url = "https://api.map.baidu.com/geoconv/v1/"
    params = {
        "coords": f"{bd_x},{bd_y}",
        "from": "6",  # This is BD09
        "to": "5",  # This is WGS84
        "ak": ak
    }
    response = requests.get(url=url, params=params)
    result = response.json()
    loc = result["result"][0]
    return loc['y'], loc['x']  # latitude, longitude


def get_point_carbon_emission(x, y):
    """
    Retrieve carbon emission value for a specific point using its x, y coordinates.
    """
    with rasterio.open(tif_path) as src:
        lat, lon = bd_xy2latlng(19, x, y)
        # Convert the lat, lon to row, col of the raster data
        row, col = src.index(lon, lat)
        # Read the raster data
        co2_data = src.read(1)
        # Use the row and col to get the value from the raster data
        return co2_data[row, col]


def extract_coordinates_from_filename(filename):
    """
    Extracts x, y coordinates from the filename.
    """
    parts = filename.split('_')
    x = int(parts[1])
    y = int(parts[2])
    return x, y


def compute_emission_for_all_images(root_folder):
    """
    Computes the carbon emission for all images in the root folder.
    """
    emissions = {}

    for city_folder in os.listdir(root_folder):
        city_path = os.path.join(root_folder, city_folder)
        # Ensure we're only iterating through directories
        if not os.path.isdir(city_path):
            continue
        for image_file in os.listdir(city_path):
            if image_file.endswith('.jpg'):
                x, y = extract_coordinates_from_filename(image_file)
                emission_value = get_point_carbon_emission(x, y)
                print(f"Emission for {city_folder}/{image_file}: {emission_value}")
                emissions[f"{city_folder}/{image_file}"] = emission_value

    return emissions


# Running the main function
if __name__ == "__main__":
    root_folder = "../../tiles"
    all_emissions = compute_emission_for_all_images(root_folder)
