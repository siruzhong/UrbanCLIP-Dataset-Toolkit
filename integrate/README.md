# Satellite Data Integration Script

## Overview
This script is designed to integrate various geospatial data sources with satellite imagery. It fetches satellite images and extracts valuable information about each image's location, including carbon emissions, population count, and GDP estimates, from corresponding raster datasets. The result is a comprehensive dataset that can be used for various analyses in urban planning, environmental studies, and economic research.

## Features
- Converts BD09 pixel coordinates to WGS84 latitude and longitude coordinates for a given zoom level.
- Retrieves raster values for carbon emissions, population, and GDP from respective `.tif` files using coordinates.
- Generates a CSV file integrating the satellite image metadata with the corresponding geospatial data.
- Processes images in batches to efficiently handle large datasets.
- Logs all actions providing a clear trail of processed data.

## Requirements
To run this script, you need to have the following libraries installed:
- `rasterio`
- `requests`
- `pyproj`
- `concurrent.futures`
- `loguru`
- `csv`
- `os`

You can install these packages using `pip`:
```sh
pip install rasterio requests pyproj loguru csv os
```

## Configuration
Before running the script, make sure to set the following configuration parameters in the script:
- `ak`: The Baidu API access key.
- `ak_list`: A list of Baidu API access keys for rotation.
- Paths to the raster datasets for carbon emissions, population, and GDP.
- `zoom`: The zoom level for the satellite images.
- `root_folder`: The root directory containing satellite images organized in city-specific folders.
- `csv_filename`: The path to the CSV file where the integrated dataset will be saved.

## Usage
To run the script, simply navigate to the directory where the script is located and execute it with Python:
```sh
python satellite_data_integration.py
```

The script will process all the images in the `root_folder`, extract the necessary data, and append it to the CSV file defined in `csv_filename`. If the CSV file does not exist, it will be created automatically.

The process includes the following steps:
1. Initializes the CSV file with the proper headers if it doesn't exist.
2. Fetches all current image names from the `root_folder`.
3. Determines which images have not yet been processed.
4. Processes each new image in batches, extracting the geospatial data and logging the information.
5. Updates the CSV file with the new data.

## Output
The output CSV file will have the following columns:
- `satellite_img_name`: The file name of the satellite image.
- `BD09 coordinate`: The pixel coordinates in the BD09 system.
- `WGS84 coordinate`: The converted WGS84 latitude and longitude coordinates.
- `carbon_emissions (ton)`: The carbon emissions value extracted from the raster data.
- `population (unit)`: The population count extracted from the raster data.
- `gdp (million yuan)`: The GDP estimate extracted from the raster data.

## Note
Please ensure you have the legal right to use the Baidu API and the raster datasets before running the script. The provided API keys should be kept secure and not shared publicly.

---
*Note: This project and script are intended solely for educational and personal use. Ensure compliance with the terms and conditions of any interacted API.*