import asyncio
import base64
import glob
import json
import os
import random
import uuid

import aiomysql
import websockets
from loguru import logger


async def create_table(pool):
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS images (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    city VARCHAR(50) NOT NULL,
                    image_path VARCHAR(255) NOT NULL,
                    caption TEXT NOT NULL,
                    INDEX idx_city (city)
                );
            """)
            await conn.commit()


def get_image_base64(image_path):
    with open(image_path, 'rb') as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
        return "data:image/jpeg;base64," + encoded_image


async def process_image(semaphore, image_path, city, pool):
    MAX_RETRIES = 3
    for attempt in range(MAX_RETRIES):
        try:
            async with semaphore:
                session_hash = uuid.uuid4().hex
                uri = 'ws://llama-adapter.opengvlab.com/queue/join'
                async with websockets.connect(uri) as websocket:
                    msg1 = {"fn_index": 1, "session_hash": session_hash}
                    await websocket.send(json.dumps(msg1))
                    while True:
                        response = json.loads(await websocket.recv())
                        if response["msg"] == "estimation":
                            logger.info(f"First responses: {session_hash}, {response}")
                            break

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

                    description = response["output"]["data"][0]
                    sentences = description.split('. ')
                    logger.info(f"Processed image: {image_path}")

                    async with pool.acquire() as conn:
                        async with conn.cursor() as cursor:
                            for sentence in sentences:
                                if sentence:
                                    await cursor.execute(
                                        "INSERT INTO images (city, image_path, caption) VALUES (%s, %s, %s)",
                                        (city, os.path.basename(image_path), sentence.strip())
                                    )
                                    await conn.commit()
        except Exception as e:
            wait_time = random.uniform(1, 3)
            logger.warning(f"Exception on attempt {attempt + 1}: {str(e)}. Retrying...")
            await asyncio.sleep(wait_time)

    logger.error(f"Failed to process image after {MAX_RETRIES} attempts: {image_path}")
    return


BATCH_SIZE = 100


async def main():
    DB_INFO = {
        'user': 'root',
        'password': '0^1PdBxuH316',
        'host': '111.230.109.230',
        'port': 3306,
        'db': 'satellite-image-text-pair'
    }

    pool = await aiomysql.create_pool(**DB_INFO)
    await create_table(pool)

    base_directory = '../tiles'
    cities = ['Beijing', 'Guangzhou', 'Shanghai', 'Shenzhen']
    semaphore = asyncio.Semaphore(100)

    for city in cities:
        directory_path = os.path.join(base_directory, city)
        logger.info(f"Processing directory: {directory_path}")

        pattern = os.path.join(directory_path, '*.jpg')
        image_paths = glob.glob(pattern)

        for i in range(0, len(image_paths), BATCH_SIZE):
            batch_paths = image_paths[i:i + BATCH_SIZE]
            tasks = [process_image(semaphore, image_path, city, pool) for image_path in batch_paths]
            await asyncio.gather(*tasks)

            logger.info(f"Saved batch {i // BATCH_SIZE + 1} for {city}")

        logger.info(f"Processed all images for {city}")

    pool.close()
    await pool.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
