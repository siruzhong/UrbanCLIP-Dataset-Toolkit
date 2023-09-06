import csv
import os
from concurrent.futures import ThreadPoolExecutor

import rasterio
import requests
from loguru import logger
from pyproj import Transformer

# Configuration parameters
ak = '1ZtwxRT5sUDd6jaj0c7sCpjy9zXTl10O'
carbon_emissions_tif_path = "/Users/zhongsiru/project/src/dataset/odiac/2021/odiac2022_1km_excl_intl_2112.tif"
worldtop_population_tif_path = "/Users/zhongsiru/project/src/dataset/worldtop/chn_ppp_2020_1km_Aggregated.tif"
gpp_tif_path = "/Users/zhongsiru/project/src/dataset/gdp/2010/cngdp2010.tif"
zoom = 16
root_folder = "/Users/zhongsiru/project/src/dataset/satellite/baidu_satellite_extended"
csv_filename = "/Users/zhongsiru/project/src/dataset/satellite/baidu_satellite_extended/integrated_satellite_data.csv"


def bd_xy2latlng(zoom, x, y):
    """Convert BD09 pixel coordinates to WGS84 lat/lng for a given zoom level."""
    res = 2 ** (18 - zoom)
    bd_x = x * 256 * res
    bd_y = y * 256 * res

    params = {
        "coords": f"{bd_x},{bd_y}",
        "from": "6",  # BD09
        "to": "5",  # WGS84
        "ak": ak
    }
    response = requests.get(url="https://api.map.baidu.com/geoconv/v1/", params=params)
    response.raise_for_status()  # Raise an exception for HTTP errors
    loc = response.json()["result"][0]
    return loc['y'], loc['x']  # latitude, longitude


def read_raster_value_at_coordinate(tif_path, lat, lon):
    """Retrieve raster value for a specific point using its lat, lon."""
    with rasterio.open(tif_path) as src:
        row, col = src.index(lon, lat)
        data = src.read(1)
        return data[row, col]


def get_point_carbon_emission(lat, lon):
    """Retrieve carbon emission value for a specific point."""
    return read_raster_value_at_coordinate(carbon_emissions_tif_path, lat, lon)


def get_point_population(lat, lon):
    """Retrieve population value for a specific point."""
    return max(0, round(read_raster_value_at_coordinate(worldtop_population_tif_path, lat, lon)))


def get_point_gdp(lat, lon):
    """Retrieve GDP value for a specific point."""
    with rasterio.open(gpp_tif_path) as src:
        transformer = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
        x_transformed, y_transformed = transformer.transform(lon, lat)
        row, col = src.index(x_transformed, y_transformed)
        if 0 <= row < src.height and 0 <= col < src.width:
            gdp_value = src.read(1)[row, col]
            return max(0, gdp_value)
        return 0


def extract_coordinates_from_filename(filename):
    """Extracts x, y coordinates from the filename."""
    _, x, y, _ = filename.split('_')
    return int(x), int(y)


def get_processed_images(csv_filename):
    """Retrieve the list of already processed images."""
    if not os.path.exists(csv_filename):
        return set()
    with open(csv_filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        return {row['satellite_img_name'] for row in reader}


def get_all_images(root_folder):
    """Retrieve all image names from the directory."""
    all_images = set()
    for city_folder in os.listdir(root_folder):
        city_path = os.path.join(root_folder, city_folder)
        if not os.path.isdir(city_path):
            continue
        for image_file in os.listdir(city_path):
            if image_file.endswith('.jpg'):
                all_images.add(f"{city_folder}/{image_file}")
    return all_images


def initialize_csv_file(filename):
    """Initialize a new CSV file with headers if it doesn't exist."""
    if os.path.exists(filename):
        return
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['satellite_img_name', 'BD09 coordinate', 'WGS84 coordinate',
                      'carbon_emissions (ton)', 'population (unit)', 'gdp (million yuan)']
        csv.DictWriter(csvfile, fieldnames=fieldnames).writeheader()


def process_image(image_key):
    city_folder, image_file = image_key.split("/")
    x, y = extract_coordinates_from_filename(image_file)
    lat, lon = bd_xy2latlng(zoom, x, y)

    emission_value = get_point_carbon_emission(lat, lon)
    population = get_point_population(lat, lon)
    gdp = get_point_gdp(lat, lon)

    logger.info(f"Data for {city_folder}/{image_file}: "
                f"Carbon emission: {emission_value}, "
                f"Population: {population}, "
                f"GDP: {gdp}")

    return {
        'satellite_img_name': image_key,
        'BD09 coordinate': f"({x * 256 * 2 ** (18 - zoom)},{y * 256 * 2 ** (18 - zoom)})",
        'WGS84 coordinate': f"({lat}, {lon})",
        'carbon_emissions (ton)': emission_value,
        'population (unit)': population,
        'gdp (million yuan)': gdp,
    }


def update_csv_with_changes(root_folder, csv_filename, batch_size=100):
    initialize_csv_file(csv_filename)

    processed_images = get_processed_images(csv_filename)
    all_current_images = get_all_images(root_folder)
    new_images = list(all_current_images - processed_images)

    num_batches = len(new_images) // batch_size + (1 if len(new_images) % batch_size else 0)
    logger.info(f"Processing {len(new_images)} new images in {num_batches} batches")
    for batch_num in range(num_batches):
        batch_start = batch_num * batch_size
        batch_end = min((batch_num + 1) * batch_size, len(new_images))
        current_batch = new_images[batch_start:batch_end]

        with ThreadPoolExecutor(max_workers=18) as executor:
            new_data = list(executor.map(process_image, current_batch))

        # Append new data to CSV
        with open(csv_filename, 'a', newline='') as csvfile:
            fieldnames = ['satellite_img_name', 'BD09 coordinate', 'WGS84 coordinate',
                          'carbon_emissions (ton)', 'population (unit)', 'gdp (million yuan)']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerows(new_data)

        logger.info(f"Finished processing batch {batch_num + 1}/{num_batches}")


if __name__ == "__main__":
    logger.info("Starting data extraction...")
    update_csv_with_changes(root_folder, csv_filename)
