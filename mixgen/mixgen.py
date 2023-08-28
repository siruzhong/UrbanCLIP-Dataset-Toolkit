import json
import os
import random

import numpy as np
from PIL import Image

# 定义路径和目录
DATA_PATHS = ["data/BJ_data.json", "data/SH_data.json", "data/GZ_data.json", "data/SZ_data.json"]
OUTPUT_DIRECTORIES = ["data_aug/Beijing", "data_aug/Shanghai", "data_aug/Guangzhou", "data_aug/Shenzhen"]
OUTPUT_JSON_PATHS = ["data_aug/BJ_data.json", "data_aug/SH_data.json", "data_aug/GZ_data.json", "data_aug/SZ_data.json"]


def mixgen(image, text, ids, lam=0.5):
    """
    混合图像和文本来生成新的增强数据。
    """
    num_samples = image.shape[0]
    pairs = list(zip(image, text, ids))
    random.shuffle(pairs)

    mixed_images, mixed_texts, new_ids = [], [], []

    for i in range(0, num_samples, 2):
        img1, txt1, id1 = pairs[i]
        img2, txt2, id2 = pairs[i + 1]

        mixed_images.append(lam * img1 + (1 - lam) * img2)
        mixed_texts.append(txt1 + " " + txt2)
        new_ids.append(f"19_{id1}_{id2}_s")

    return np.array(mixed_images), np.array(mixed_texts), np.array(new_ids)


def load_and_preprocess_image(image_path):
    """
    加载和预处理图像。
    """
    img = Image.open(image_path)
    return np.array(img) / 255.0


def main():
    for city_index, data_path in enumerate(DATA_PATHS):
        output_directory = OUTPUT_DIRECTORIES[city_index]
        output_json_path = OUTPUT_JSON_PATHS[city_index]

        # 加载JSON数据
        with open(data_path, "r") as json_file:
            data = json.load(json_file)

        # 提取图像路径、标题和ID
        image_paths = [item["image"] for item in data]
        captions = [item["caption"] for item in data]
        ids = ['_'.join(item["image_id"].split('_')[1:3]) for item in data]

        # 加载和预处理图像
        images = np.array([load_and_preprocess_image(path) for path in image_paths])
        captions_np = np.array(captions)
        ids_np = np.array(ids)

        # 数据增强
        mixed_images, mixed_texts, new_ids = mixgen(images, captions_np, ids_np)

        # 检查输出目录是否存在
        os.makedirs(output_directory, exist_ok=True)

        # 为增强数据准备条目
        data_entries = [{
            "mixed_texts": mixed_texts[i],
            "mixed_images": os.path.join(output_directory, f"{new_ids[i]}.jpg"),
            "ids": new_ids[i]
        } for i in range(len(new_ids))]

        # 保存混合图像和JSON数据
        for i, entry in enumerate(data_entries):
            Image.fromarray((mixed_images[i] * 255).astype(np.uint8)).save(entry["mixed_images"])
            print(f"Saved mixed image {entry['mixed_images']}")

        with open(output_json_path, "w") as json_file:
            json.dump(data_entries, json_file, indent=4)

        print(f"Data augmentation and saving for {data_path} completed.")


if __name__ == "__main__":
    main()
