import asyncio
import base64
import glob
import json
import os
import random
import uuid

import websockets
from loguru import logger


def get_image_base64(image_path):
    """
    Encodes the given image as a Base64 string.

    :param image_path: Path to the image file.
    :return: Base64 encoded string of the image.
    """
    with open(image_path, 'rb') as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
        return "data:image/jpeg;base64," + encoded_image


async def process_image(semaphore, image_path):
    """
    Processes a single image and returns the description split into sentences.

    :param semaphore: Limit the number of tasks running simultaneously
    :param image_path: Path to the image file.
    :return: List of description sentences.
    """
    MAX_RETRIES = 3
    for attempt in range(MAX_RETRIES):
        try:
            async with semaphore:
                session_hash = uuid.uuid4().hex
                uri = 'ws://llama-adapter.opengvlab.com/queue/join'
                async with websockets.connect(uri) as websocket:
                    # Sending first message to the server
                    msg1 = {"fn_index": 1, "session_hash": session_hash}
                    await websocket.send(json.dumps(msg1))
                    while True:
                        response = json.loads(await websocket.recv())
                        if response["msg"] == "estimation":
                            logger.info(f"First responses: {session_hash}, {response}")
                            break

                    # Sending second message containing the image
                    image_base64 = get_image_base64(image_path)
                    msg2 = {
                        "fn_index": 1,
                        "data": [image_base64, "", 128, 0.1, 0.75],
                        "event_data": None,
                        "session_hash": session_hash
                    }
                    await websocket.send(json.dumps(msg2))
                    while True:
                        response = json.loads(await websocket.recv())
                        if response["msg"] == "process_completed":
                            logger.info(f"Second responses: {session_hash}, {response}")
                            break

                    # Splitting the description into sentences
                    description = response["output"]["data"][0]
                    sentences = description.split('. ')
                    logger.info(f"Processed image: {image_path}")
                    return sentences
        except Exception as e:
            wait_time = random.uniform(1, 3)  # Random wait time between 1 and 3 seconds
            logger.warning(f"Exception on attempt {attempt + 1}: {str(e)}. Retrying...")
            await asyncio.sleep(wait_time)  # wait a second and try again

    logger.error(f"Failed to process image after {MAX_RETRIES} attempts: {image_path}")
    return []


BATCH_SIZE = 1000


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
    semaphore = asyncio.Semaphore(100)

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

        if not new_image_paths:
            logger.info(f"All images for {city} have already been processed.")
            continue

        # Process new images and generate new data
        new_data = []
        for i in range(0, len(new_image_paths), BATCH_SIZE):
            batch_paths = new_image_paths[i:i + BATCH_SIZE]
            tasks = [process_image(semaphore, image_path) for image_path in batch_paths]
            descriptions = await asyncio.gather(*tasks)

            batch_results = []
            for image_path, description_sentences in zip(batch_paths, descriptions):
                image_name = os.path.basename(image_path)
                image_results = [{"caption": sentence.strip(), "image": os.path.join(city, image_name)} for sentence in
                                 description_sentences if sentence]
                batch_results.extend(image_results)

            new_data.extend(batch_results)
            logger.info(f"Processed batch {i // BATCH_SIZE + 1} for {city}")

        # Flatten existing_data list if it's nested
        existing_data_flat = [item for sublist in existing_data for item in sublist]

        # Combine existing and new data, then write to the JSON file
        existing_data_flat.extend(new_data)

        # Wrap the entire existing_data_flat list in an additional list
        combined_data = [existing_data_flat]

        with open(city_json_filename, 'w') as file:
            json.dump(combined_data, file, indent=2)
        logger.info(f"Saved {len(new_data)} results to {city_json_filename}")


# Running the main function
if __name__ == "__main__":
    asyncio.run(main())
