import json
import os
import shutil


def find_and_extract_images_with_keyword(json_file, keyword):
    """
    在给定的JSON文件中查找包含关键词的图片，并返回它们。
    :param json_file: 要查询的JSON文件路径。
    :param keyword: 要在标题中查找的关键词。
    :return: 与关键词匹配的条目的列表，以及与这些条目关联的图片的列表。
    """
    with open(json_file, 'r') as f:
        data = json.load(f)

    images_with_keyword = set()  # 使用集合确保图片是唯一的
    extracted_data = []

    for entry_group in data:  # data是一个外部列表
        for entry in entry_group:  # entry_group是内部列表
            if keyword in entry['caption']:
                images_with_keyword.add(entry['image'])
                extracted_data.append(entry)

    return extracted_data, list(images_with_keyword)


def remove_images_from_data(json_file, images_to_remove):
    """
    从JSON文件中删除指定的图片条目。
    :param json_file: 要修改的JSON文件路径。
    :param images_to_remove: 要从文件中删除的图片列表。
    """
    with open(json_file, 'r') as f:
        data = json.load(f)

    # 删除与指定图片匹配的条目
    for entry_group in data:
        entry_group[:] = [entry for entry in entry_group if entry['image'] not in images_to_remove]

    # 删除空的entry_groups
    data[:] = [entry_group for entry_group in data if entry_group]

    # 重新写入到JSON文件
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)


def save_to_new_json(data, new_json_file):
    """
    将数据保存到新的JSON文件中。如果文件已存在，此函数将追加数据，而不是覆盖它。
    :param data: 要保存的数据。
    :param new_json_file: 数据要保存的文件的路径。
    """
    existing_data = []

    # 如果文件已存在，读取其内容
    if os.path.exists(new_json_file):
        with open(new_json_file, 'r') as f:
            existing_data = json.load(f)

    # 添加新的数据
    existing_data.extend(data)

    # 写回数据
    with open(new_json_file, 'w') as f:
        json.dump(existing_data, f, indent=4)


def move_images_to_folder(images, source_folder, destination_folder):
    """
    将图片从一个文件夹移动到另一个文件夹。
    :param images: 要移动的图片的列表。
    :param source_folder: 图片当前的文件夹。
    :param destination_folder: 图片要移动到的目标文件夹。
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


img_base_dir = "../tiles-extended"
img_filter_base_dir = img_base_dir + '/ocean'
json_dir = './pairs-extended'
city_list = ['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen']

if __name__ == "__main__":
    # 指定多个JSON文件的路径
    for city in city_list:
        json_file = os.path.join(json_dir, city + "_captions.json")

        # 根据关键词找到图片
        extracted_data, images_to_remove = find_and_extract_images_with_keyword(json_file, 'ocean')

        # 移动找到的图片到指定文件夹
        move_images_to_folder(images_to_remove, os.path.join(img_base_dir, city),
                              os.path.join(img_filter_base_dir, city))

        # 从原始数据中删除找到的图片
        remove_images_from_data(json_file, images_to_remove)

        # 将提取的数据保存到新的JSON文件中
        save_to_new_json(extracted_data, os.path.join(img_filter_base_dir, 'ocean.json'))

        # 打印已删除的图片列表
        print("Removed images:")
        for img in images_to_remove:
            print(img)
