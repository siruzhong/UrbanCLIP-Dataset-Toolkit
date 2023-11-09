import json


def count_json_entries(json_file):
    """
    Counts the number of entries within a JSON file that is structured with nested lists.

    Args:
        json_file (str): The path to the JSON file to be processed.

    Returns:
        int: The total count of individual entries in the nested lists of the JSON file.
    """
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Initialize a counter for the entries
    length = 0

    # Iterate over the outer list to access nested lists
    for entry_group in data:  # 'data' is expected to be a list of lists
        # Iterate over each group to count the entries
        for _ in entry_group:  # 'entry_group' is an inner list
            length += 1

    return length


if __name__ == "__main__":
    # Prints the number of entries in each specified JSON file.
    json_files = [
        '../pairs/Beijing_captions.json',
        '../pairs/Shanghai_captions.json',
        '../pairs/Guangzhou_captions.json',
        '../pairs/Shenzhen_captions.json',
        '../pairs/ocean/Beijing_captions.json',
        '../pairs/ocean/Shanghai_captions.json',
        '../pairs/ocean/Guangzhou_captions.json',
        '../pairs/ocean/Shenzhen_captions.json'
    ]

    for json_file in json_files:
        print(f"{json_file}: {count_json_entries(json_file)} entries")
