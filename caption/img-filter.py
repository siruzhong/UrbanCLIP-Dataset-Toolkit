import json
import os
import shutil


def find_and_extract_images_with_keyword(json_file, keyword):
    """
    Searches for images containing the keyword in the given JSON file and returns them.
    :param json_file: Path to the JSON file to be searched.
    :param keyword: The keyword to look for in the captions.
    :return: A list of entries that match the keyword and a list of images associated with those entries.
    """
    with open(json_file, 'r') as f:
        data = json.load(f)

    images_with_keyword = set()  # Use a set to ensure uniqueness of images
    extracted_data = []

    # 'data' is an outer list containing nested lists
    for entry_group in data:
        # 'entry_group' is an inner list
        for entry in entry_group:
            if keyword in entry['caption']:
                images_with_keyword.add(entry['image'])
                extracted_data.append(entry)

    return extracted_data, list(images_with_keyword)


def remove_images_from_data(json_file, images_to_remove):
    """
    Removes specified image entries from a JSON file.
    :param json_file: Path to the JSON file to be modified.
    :param images_to_remove: List of images to be removed from the file.
    """
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Remove entries matching the specified images
    for entry_group in data:
        entry_group[:] = [entry for entry in entry_group if entry['image'] not in images_to_remove]

    # Remove any empty entry groups
    data[:] = [entry_group for entry_group in data if entry_group]

    # Write the updated data back to the JSON file
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)


def save_to_new_json(data, new_json_file):
    """
    Saves the data to a new JSON file. If the file already exists, this function appends data rather than overwriting it.
    :param data: The data to be saved.
    :param new_json_file: Path of the file where data is to be saved.
    """
    existing_data = []

    # If the file already exists, read its content
    if os.path.exists(new_json_file):
        with open(new_json_file, 'r') as f:
            existing_data = json.load(f)

    # Add the new data
    existing_data.extend(data)

    # Write the data back
    with open(new_json_file, 'w') as f:
        json.dump(existing_data, f, indent=4)


def move_images_to_folder(images, source_folder, destination_folder):
    """
    Moves images from one folder to another.
    :param images: A list of images to be moved.
    :param source_folder: The current folder of the images.
    :param destination_folder: The target folder to which the images will be moved.
    """
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    for image in images:
        source_image_path = os.path.join(source_folder, os.path.basename(image))
        destination_image_path = os.path.join(destination_folder, os.path.basename(image))

        if os.path.exists(source_image_path):
            shutil.move(source_image_path, destination_image_path)
        else:
            print(f"Warning: Image {source_image_path} not found!")


img_base_dir = "../tiles"
img_filter_base_dir = img_base_dir + '/ocean'
json_dir = 'pairs'
city_list = ['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen']

if __name__ == "__main__":
    # Specifying paths for multiple JSON files
    for city in city_list:
        json_file = os.path.join(json_dir, city + "_captions.json")

        # Find images based on the keyword
        extracted_data, images_to_remove = find_and_extract_images_with_keyword(json_file, 'ocean')

        # Move found images to a specific folder
        move_images_to_folder(images_to_remove, os.path.join(img_base_dir, city),
                              os.path.join(img_filter_base_dir, city))

        # Remove found images from the original data
        remove_images_from_data(json_file, images_to_remove)

        # Save the extracted data to a new JSON file
        save_to_new_json(extracted_data, os.path.join(img_filter_base_dir, 'ocean.json'))

        # Print the list of removed images
        print("Removed images:")
        for img in images_to_remove:
            print(img)
