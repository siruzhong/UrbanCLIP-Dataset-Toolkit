import asyncio
import base64
import json
import websockets
from loguru import logger


def get_image_base64(image_path):
    with open(image_path, 'rb') as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
        return "data:image/jpeg;base64," + encoded_image


async def connect():
    uri = 'ws://llama-adapter.opengvlab.com/queue/join'
    headers = {}

    async with websockets.connect(uri, extra_headers=headers) as websocket:
        # 第一条消息
        msg1 = {"fn_index": 1, "session_hash": "4k1lrzequpu"}
        await websocket.send(json.dumps(msg1))
        response1 = await websocket.recv()
        logger.info("Response after first message (1): {}", response1)
        response2 = await websocket.recv()
        logger.info("Response after first message (2): {}", response2)

        # 第二条消息
        image_base64 = get_image_base64('disenzhang.jpg')  # 从本地文件获取图片base64编码
        msg2 = {
            "fn_index": 1,
            "data": [image_base64, "", 128, 0.1, 0.75],
            "event_data": None,
            "session_hash": "4k1lrzequpu"
        }
        await websocket.send(json.dumps(msg2))
        response3 = await websocket.recv()
        logger.info("Response after second message (1): {}", response3)
        response4 = await websocket.recv()
        logger.info("Response after second message (2): {}", response4)
        response5 = await websocket.recv()
        logger.info("Response after second message (3): {}", response5)


# 启动连接
asyncio.get_event_loop().run_until_complete(connect())
