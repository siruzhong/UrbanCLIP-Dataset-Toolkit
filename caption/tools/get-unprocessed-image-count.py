import glob
import json
import os

from loguru import logger


def get_unprocessed_image_count():
    """
    Calculate the number of images pending for description generation.
    This function checks against already processed images to avoid duplication.
    """

    # Ensures the output directory exists; creates it if not.
    output_directory = 'pairs'
    os.makedirs(output_directory, exist_ok=True)

    # The base directory where the city image folders are located.
    base_directory = '../tiles'
    cities = ['Beijing', 'Guangzhou', 'Shanghai', 'Shenzhen']

    for city in cities:
        directory_path = os.path.join(base_directory, city)
        logger.info(f"Processing directory: {directory_path}")

        # Glob pattern to match all jpg images within the city's directory.
        pattern = os.path.join(directory_path, '*.jpg')
        image_paths = glob.glob(pattern)

        # Attempt to load existing caption JSON data if available.
        city_json_filename = os.path.join(output_directory, f"{city}_captions.json")
        existing_data = []
        if os.path.exists(city_json_filename):
            with open(city_json_filename, 'r') as file:
                existing_data = json.load(file)

        # Creates a set of already processed images for quick lookup.
        existing_images = set(item["image"] for sublist in existing_data for item in sublist)

        # Filters out images that have already been processed.
        new_image_paths = [image_path for image_path in image_paths
                           if '/'.join(image_path.split('/')[-2:]) not in existing_images]

        logger.info(f"{len(new_image_paths)} new images to process for {city}.")
        logger.info(f"{len(image_paths)} total images for {city}.")
