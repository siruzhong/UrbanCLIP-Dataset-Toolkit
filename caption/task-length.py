import asyncio
import glob
import json
import os

from loguru import logger


async def main():
    """
    Main function to process all images in the specified directories and save
    the captions as JSON objects.
    """
    # Create 'pairs' directory if it does not exist
    output_directory = 'pairs'
    os.makedirs(output_directory, exist_ok=True)

    base_directory = '../tiles'
    cities = ['Beijing', 'Guangzhou', 'Shanghai', 'Shenzhen']
    semaphore = asyncio.Semaphore(1000)

    for city in cities:
        directory_path = os.path.join(base_directory, city)
        logger.info(f"Processing directory: {directory_path}")

        # Finding all image files in the directory
        pattern = os.path.join(directory_path, '*.jpg')
        image_paths = glob.glob(pattern)

        # Load existing data if the file exists
        city_json_filename = os.path.join(output_directory, f"{city}_captions.json")
        existing_data = []
        if os.path.exists(city_json_filename):
            with open(city_json_filename, 'r') as file:
                existing_data = json.load(file)

        # Convert existing data into a set for easy lookup
        existing_images = set(item["image"] for sublist in existing_data for item in sublist)

        new_image_paths = []
        for image_path in image_paths:
            base_name = '/'.join(image_path.split('/')[-2:])
            if base_name not in existing_images:
                new_image_paths.append(image_path)

        logger.info(f"Processing {len(new_image_paths)} new images for {city}.")


# Running the main function
if __name__ == "__main__":
    asyncio.run(main())
