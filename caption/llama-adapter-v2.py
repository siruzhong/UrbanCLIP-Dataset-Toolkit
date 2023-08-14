import asyncio
import base64
import glob
import json
import os
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
        except websockets.ConnectionClosedError:
            logger.warning(f"Connection reset on attempt {attempt + 1}, retrying...")
            await asyncio.sleep(1)  # wait a second and try again

    logger.error(f"Failed to process image after {MAX_RETRIES} attempts: {image_path}")
    return []


BATCH_SIZE = 100


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

        # Create city JSON file
        city_json_filename = os.path.join(output_directory, f"{city}_captions.json")
        with open(city_json_filename, 'w') as file:
            file.write('[')

        total_results = 0
        for i in range(0, len(image_paths), BATCH_SIZE):
            batch_paths = image_paths[i:i + BATCH_SIZE]
            tasks = [process_image(semaphore, image_path) for image_path in batch_paths]
            descriptions = await asyncio.gather(*tasks)

            batch_results = []
            for image_path, description_sentences in zip(batch_paths, descriptions):
                image_name = os.path.basename(image_path)
                image_results = [{"caption": sentence.strip(), "image":
                    os.path.join(city, image_name)} for sentence in description_sentences if sentence]
                batch_results.extend(image_results)

            with open(city_json_filename, 'a') as file:
                if i != 0:
                    file.write(',')
                json.dump(batch_results, file, indent=2)
                if i + BATCH_SIZE < len(image_paths):
                    file.write(',')

            total_results += len(batch_results)
            logger.info(f"Saved batch {i // BATCH_SIZE + 1} to {city_json_filename}")

        with open(city_json_filename, 'a') as file:
            file.write(']')
        logger.info(f"Saved {total_results} results to {city_json_filename}")


# Running the main function
if __name__ == "__main__":
    asyncio.run(main())
