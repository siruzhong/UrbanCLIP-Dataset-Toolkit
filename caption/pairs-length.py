import json


def calculate_json_pairs_length(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)

    length = 0
    for entry_group in data:  # data是一个外部列表
        for entry in entry_group:  # entry_group是内部列表
            length = length + 1

    return length


if __name__ == "__main__":
    print(calculate_json_pairs_length('./pairs-extended/Beijing_captions.json'))
    print(calculate_json_pairs_length('./pairs-extended/Shanghai_captions.json'))
    print(calculate_json_pairs_length('./pairs-extended/Guangzhou_captions.json'))
    print(calculate_json_pairs_length('./pairs-extended/Shenzhen_captions.json'))
    print(calculate_json_pairs_length('./pairs-extended/filtered/Beijing_captions.json'))
    print(calculate_json_pairs_length('./pairs-extended/filtered/Shanghai_captions.json'))
    print(calculate_json_pairs_length('./pairs-extended/filtered/Guangzhou_captions.json'))
    print(calculate_json_pairs_length('./pairs-extended/filtered/Shenzhen_captions.json'))
