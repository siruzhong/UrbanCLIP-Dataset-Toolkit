# Satellite Image Description Generator

This directory features two Python scripts tailored for processing satellite images. They leverage a LLaMA-Adapter V2 model through WebSocket to generate textual descriptions and perform data handling tasks.

## Scripts Overview

- [img-caption-generator.py](img-caption-generator.py): This script interfaces with a machine learning model via WebSocket to process satellite images and generate descriptive text. The results are outputted in JSON format, exemplified by [pairs/Beijing_captions.json](pairs/Beijing_captions.json).
- [img-filter.py](img-filter.py): This script filters out images that may not be useful for certain applications, such as pictures of oceans, forests, and deserts. It sifts through JSON data files to locate and extract images based on specified keywords, transfers the identified images to a designated folder, purges these images from the original dataset, and archives the refined data in a new JSON file.

## Dependencies

To ensure the scripts run smoothly, install the following prerequisites:

```bash
pip install websockets loguru
```

## Usage Instructions

### Image Description Generator

1. **Setup**: Organize satellite images in a directory structure set by the `base_directory` parameter, with subfolders named after cities, such as `../pairs`. Modify this to match your image repository.

2. **Execution**: Run the [img-caption-generator.py](img-caption-generator.py) script to initiate image processing:

    ```bash
    python img-caption-generator.py
    ```

3. **Output**: Descriptions are saved in the `pairs` directory, generating one JSON file per city with captions linked to image filenames.

### Keyword Image Extractor

1. **Configuration**: Define img_base_dir as the root directory for the image repository (such as ../tiles) and json_dir as the location of the JSON files containing image descriptions.


2. **Execution**: Invoke the [img-filter.py](img-filter.py) to filter images using a chosen keyword:

    ```bash
    python img-filter.py
    ```

3. **Processing Steps**: The script will:
    - Identify images whose captions include a predefined keyword (default is 'ocean').
    - Relocate these images to a structured folder: [img_base_dir + '/ocean'](pairs/ocean).
    - Excise the image entries from the source JSON dataset.
    - Save the filtered data to a new JSON file within the `ocean` folder.

## Additional Information

- Ensure the WebSocket server is operational and reachable at the designated URI within the scripts.
- Script modifications may be necessary to accommodate your specific directory framework and network configurations.

## Support

If you require assistance with these scripts, please initiate an issue in this repository.

---
*Note: This project and script are intended solely for educational and personal use. Ensure compliance with the terms and conditions of any interacted API.*