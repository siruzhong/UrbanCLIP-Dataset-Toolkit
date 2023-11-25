# Satellite Image Crawler V2

## Description

This project is a Python-based tool for crawling satellite images. It allows users to download satellite map tiles from
specific geographical regions defined by Area of Interest (AOI) polygons. The tool calculates the bounding square for
each AOI and downloads all satellite image tiles that fall within this square. Additionally, it includes functionality
to stitch these tiles together into a single large image.

## Features

- Read AOI data from a CSV file.
- Convert GPS coordinates to Baidu map coordinates.
- Download satellite image tiles from Baidu Maps.
- Stitch multiple tiles together to form a large single image.
- Log information for monitoring and debugging.

## Usage

1. Update the `aoi.csv` file with your AOI data. The CSV format should include `aoi_address`, `centroid`, and `wkt` (
   Well-Known Text) for the polygon.

2. Ensure you have a valid Baidu Maps Access Key (replace `'Your_Baidu_AK'` in the script with your actual access key).

3. Run the script:
   ```
   python crawl.py
   ```

## Configuration

- You can adjust the zoom level and other settings within the script to suit your specific requirements.
- Modify the `download_tiles` function to change the region of interest or satellite image properties.

## Output

- Downloaded tiles are saved in the `tiles` directory, organized by city names.
- Stitched images are saved in the `stitched_images` directory.