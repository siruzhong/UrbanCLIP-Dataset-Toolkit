import json
import os
import random

import numpy as np
from PIL import Image

# Define paths and directories
data_paths = ["data/BJ_data.json", "data/SH_data.json", "data/GZ_data.json", "data/SZ_data.json"]
output_directories = ["data_aug/Beijing", "data_aug/Shanghai", "data_aug/Guangzhou", "data_aug/Shenzhen"]
output_json_paths = ["data_aug/BJ_data.json", "data_aug/SH_data.json", "data_aug/GZ_data.json", "data_aug/SZ_data.json"]


# Define mixgen function
def mixgen(image, text, ids, lam=0.5):
    num_samples = image.shape[0]
    pairs = list(zip(image, text, ids))  # Combine image and text into pairs
    random.shuffle(pairs)  # Shuffle the pairs randomly

    mixed_images = []
    mixed_texts = []
    new_ids = []

    for i in range(0, num_samples, 2):
        img1, txt1, id1 = pairs[i]
        img2, txt2, id2 = pairs[i + 1]

        mixed_img = lam * img1 + (1 - lam) * img2
        mixed_text = txt1 + " " + txt2
        new_id = f"19_{id1}_{id2}_s"  # Concatenate ids for the mixed pair

        mixed_images.append(mixed_img)
        mixed_texts.append(mixed_text)
        new_ids.append(new_id)

    mixed_images = np.array(mixed_images)
    mixed_texts = np.array(mixed_texts)
    new_ids = np.array(new_ids)

    return mixed_images, mixed_texts, new_ids


# Iterate over each city's data
for city_index, data_path in enumerate(data_paths):
    output_directory = output_directories[city_index]
    output_json_path = output_json_paths[city_index]

    # Load JSON data
    with open(data_path, "r") as json_file:
        data = json.load(json_file)

    # Extract data
    image_paths = [item["image"] for item in data]
    captions = [item["caption"] for item in data]
    ids = [item["image_id"].split('_')[1:3] for item in data]
    ids = ['_'.join(parts) for parts in ids]


    # Load and preprocess images
    def load_and_preprocess_image(image_path):
        img = Image.open(image_path)
        img = np.array(img) / 255.0  # Normalize pixel values to [0, 1]
        return img


    # Load images and preprocess them
    images = [load_and_preprocess_image(path) for path in image_paths]
    images_np = np.array(images)
    captions_np = np.array(captions)
    ids_np = np.array(ids)

    # Data augmentation
    mixed_images, mixed_texts, new_ids = mixgen(images_np, captions_np, ids_np, lam=0.5)

    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Prepare data entries
    data_entries = []

    # Iterate over the data and create entries
    for i in range(len(new_ids)):
        mixed_image_path = os.path.join(output_directory, f"{new_ids[i]}.jpg")
        mixed_texts_entry = mixed_texts[i]
        ids_entry = new_ids[i]

        # Create entry for the augmented data
        entry = {
            "mixed_texts": mixed_texts_entry,
            "mixed_images": mixed_image_path,
            "ids": ids_entry
        }
        data_entries.append(entry)

        # Save the mixed image
        mixed_image = Image.fromarray((mixed_images[i] * 255).astype(np.uint8))
        mixed_image.save(mixed_image_path)
        print(f"Saved mixed image {mixed_image_path}")

    # Save the JSON file
    with open(output_json_path, "w") as json_file:
        json.dump(data_entries, json_file, indent=4)

    print(f"Data augmentation and saving for {data_path} completed.")
