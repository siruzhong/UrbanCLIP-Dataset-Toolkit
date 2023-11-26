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
    将给定的图像编码为Base64字符串。

    :param image_path: 图像文件的路径。
    :return: 图像的Base64编码字符串。
    """
    with open(image_path, 'rb') as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
        return "data:image/jpeg;base64," + encoded_image


async def process_image(semaphore, image_path):
    """
    处理单个图像并返回分成句子的描述。

    :param semaphore: 限制同时运行的任务数量
    :param image_path: 图像文件的路径。
    :return: 描述句子的列表。
    """
    MAX_RETRIES = 3
    for attempt in range(MAX_RETRIES):
        try:
            async with semaphore:
                session_hash = uuid.uuid4().hex
                uri = 'ws://llama-adapter.opengvlab.com/queue/join'
                async with websockets.connect(uri) as websocket:
                    # 发送第一个消息到服务器
                    msg1 = {"fn_index": 1, "session_hash": session_hash}
                    await websocket.send(json.dumps(msg1))
                    while True:
                        response = json.loads(await websocket.recv())
                        if response["msg"] == "estimation":
                            logger.info(f"First responses: {session_hash}, {response}")
                            break

                    # 发送包含图像的第二个消息
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

                    # 将描述拆分成句子
                    description = response["output"]["data"][0]
                    sentences = description.split('. ')
                    logger.info(f"Processed image: {image_path}")
                    return sentences
        except Exception as e:
            wait_time = random.uniform(1, 3)  # 随机等待时间在1到3秒之间
            logger.warning(f"Exception on attempt {attempt + 1}: {str(e)}. Retrying...")
            await asyncio.sleep(wait_time)  # 等待一秒后重试

    logger.error(f"Failed to process image after {MAX_RETRIES} attempts: {image_path}")
    return []


BATCH_SIZE = 5


async def main():
    """
    主要函数，用于处理指定目录中的所有图像并将描述保存为JSON对象。
    """
    # 如果不存在，创建'pairs'目录
    output_directory = 'pairs'
    os.makedirs(output_directory, exist_ok=True)

    base_directory = 'img/masked_images'
    semaphore = asyncio.Semaphore(1000)

    # 查找目录中的所有图像文件
    pattern = os.path.join(base_directory, '*.jpg')
    image_paths = glob.glob(pattern)

    # 如果文件存在，加载现有数据
    json_filename = os.path.join(output_directory, "captions.json")
    existing_data = []
    if os.path.exists(json_filename):
        with open(json_filename, 'r') as file:
            existing_data = json.load(file)

    # 将现有数据转换为集合以便于查找
    existing_images = set(item["image"] for sublist in existing_data for item in sublist)

    new_image_paths = []
    for image_path in image_paths:
        base_name = '/'.join(image_path.split('/')[-2:])
        if base_name not in existing_images:
            new_image_paths.append(image_path)

    if not new_image_paths:
        logger.info(f"All images have already been processed.")
        return

    # 处理新图像并生成新数据
    new_data = []
    for i in range(0, len(new_image_paths), BATCH_SIZE):
        batch_paths = new_image_paths[i:i + BATCH_SIZE]
        tasks = [process_image(semaphore, image_path) for image_path in batch_paths]
        descriptions = await asyncio.gather(*tasks)

        batch_results = []
        for image_path, description_sentences in zip(batch_paths, descriptions):
            image_name = os.path.basename(image_path)
            image_results = [{"caption": sentence.strip(), "image": os.path.join(image_name)} for sentence in
                             description_sentences if sentence]
            batch_results.extend(image_results)

        new_data.extend(batch_results)
        logger.info(f"Processed batch {i // BATCH_SIZE + 1}")

        # 如果现有数据列表是嵌套的，将其展平
        existing_data_flat = [item for sublist in existing_data for item in sublist]

        # 合并现有数据和新数据，然后写入JSON文件
        existing_data_flat.extend(new_data)

        # 将整个existing_data_flat列表包装在另一个列表中
        combined_data = [existing_data_flat]

        with open(json_filename, 'w', encoding='utf-8') as file:
            json.dump(combined_data, file, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(new_data)} results to {json_filename}")


# 运行主函数
if __name__ == "__main__":
    asyncio.run(main())
