import csv
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


def already_processed_images(csv_filename):
    processed_images = set()
    if os.path.exists(csv_filename):
        with open(csv_filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                processed_images.add(row['satellite_img_name'])
    return processed_images


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


def csv_file_exists(filename):
    """Check if a CSV file exists."""
    return os.path.exists(filename)


def create_csv_file(filename):
    """Create a new CSV file with headers."""
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['satellite_img_name', 'BD09 coordinate', 'WGS84 coordinate', 'carbon_emissions']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()


def update_csv_with_changes(root_folder, csv_filename):
    if not csv_file_exists(csv_filename):
        create_csv_file(csv_filename)

    processed_images = already_processed_images(csv_filename)
    all_current_images = get_all_images(root_folder)

    # Identify new and removed images
    new_images = all_current_images - processed_images
    removed_images = processed_images - all_current_images

    new_data = []
    for image_key in new_images:
        city_folder, image_file = image_key.split("/")
        x, y = extract_coordinates_from_filename(image_file)
        lat, lon = bd_xy2latlng(16, x, y)
        emission_value = get_point_carbon_emission(x, y)
        print(f"Emission for {city_folder}/{image_file}: {emission_value}")
        new_data.append({
            'satellite_img_name': image_key,
            'BD09 coordinate': f"({x * 256 * 2 ** (18 - 16)}, {y * 256 * 2 ** (18 - 16)})",
            'WGS84 coordinate': f"({lat}, {lon})",
            'carbon_emissions': emission_value
        })

    # Process CSV: Load, Remove old entries, Append new data, and Rewrite
    with open(csv_filename, 'r') as csvfile:
        reader = list(csv.DictReader(csvfile))
        # Filtering out removed images
        reader = [row for row in reader if row['satellite_img_name'] not in removed_images]

    # Append new data and rewrite CSV
    with open(csv_filename, 'w', newline='') as csvfile:
        fieldnames = ['satellite_img_name', 'BD09 coordinate', 'WGS84 coordinate', 'carbon_emissions']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(reader)  # Existing data
        writer.writerows(new_data)  # New data


# Running the main function
if __name__ == "__main__":
    root_folder = "../../tiles"
    csv_filename = "integrated_satellite_data.csv"
    update_csv_with_changes(root_folder, csv_filename)
