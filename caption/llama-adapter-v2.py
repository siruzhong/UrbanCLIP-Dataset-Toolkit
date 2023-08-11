import asyncio
import base64
import glob
import json
import os

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


async def process_image(image_path):
    """
    Processes a single image and returns the description split into sentences.

    :param image_path: Path to the image file.
    :return: List of description sentences.
    """
    uri = 'ws://llama-adapter.opengvlab.com/queue/join'
    async with websockets.connect(uri) as websocket:
        # Sending first message to the server
        msg1 = {"fn_index": 1, "session_hash": "4k1lrzequpu"}
        await websocket.send(json.dumps(msg1))
        await websocket.recv()
        await websocket.recv()

        # Sending second message containing the image
        image_base64 = get_image_base64(image_path)
        msg2 = {
            "fn_index": 1,
            "data": [image_base64, "", 128, 0.1, 0.75],
            "event_data": None,
            "session_hash": "4k1lrzequpu"
        }
        await websocket.send(json.dumps(msg2))
        await websocket.recv()
        await websocket.recv()
        response = await websocket.recv()
        response_json = json.loads(response)
        description = response_json["output"]["data"][0]

        # Splitting the description into sentences
        sentences = description.split('. ')
        logger.info(f"Processed image: {image_path}")
        return sentences


def handle_image(image_path):
    return asyncio.run(process_image(image_path))


def main():
    """
    Main function to process all images in the specified directories and save
    the captions as JSON objects.
    """
    results = []
    base_directory = 'tiles'
    cities = ['Beijing', 'Guangzhou', 'Shanghai', 'Shenzhen']

    for city in cities:
        directory_path = os.path.join(base_directory, city)
        logger.info(f"Processing directory: {directory_path}")

        # Finding all image files in the directory
        pattern = os.path.join(directory_path, '*.jpg')
        image_paths = glob.glob(pattern)

        # Processing images concurrently
        for image_path in image_paths:
            image_name = os.path.basename(image_path)
            description_sentences = handle_image(image_path)

            # Grouping the JSON for the same image together
            image_results = []
            for sentence in description_sentences:
                if sentence:  # Avoid empty strings
                    result = {"caption": sentence.strip(), "image": os.path.join(city, image_name)}
                    image_results.append(result)

            results.extend(image_results)

    # Saving the results as a JSON file
    with open('captions.json', 'w') as file:
        json.dump(results, file)
    logger.info(f"Saved {len(results)} results to captions.json")


# Running the main function
if __name__ == "__main__":
    main()
