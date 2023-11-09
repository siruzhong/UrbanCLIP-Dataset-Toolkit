# Data Augmentation Tool

This tool is designed to perform data augmentation on image and associated text data for four cities. It aims to enrich
the dataset, providing more varied samples for training machine learning models.

## Main Features

- **Image Augmentation**: Linearly blends two images to create a new, augmented image.
- **Text Augmentation**: Concatenates two text segments to produce augmented textual content.
- **ID Generation**: For each pair of augmented data, generates a new ID for identification purposes.

## Usage Steps

1. **Set Paths**:

    - `DATA_PATHS`: Paths to the input raw data JSON files.
    - `OUTPUT_DIRECTORIES`: Directories for storing augmented images.
    - `OUTPUT_JSON_PATHS`: Paths for the output augmented data JSON files.

2. **Run the Script**: Execute the script to process data for each city. It will output the augmented images and JSON
   files.

3. **Check Outputs**:

    - Augmented images are saved in the specified directories.
    - Augmented data for each city, including image paths, text, and new IDs, is saved in corresponding JSON files.

## Precautions

- Ensure that the input JSON files are in the correct format, containing image paths, text descriptions, and IDs.
- For successful data augmentation, the dataset size for each city should be an even number.
- Images are normalized to the [0, 1] range during processing.

## Additional Information

This augmentation process is a valuable step in preprocessing for machine learning tasks. By combining images and texts
from the same city, the tool effectively doubles the dataset's size while maintaining relevant contextual information.
The generated IDs preserve the linkage between the original data and its augmented counterpart, facilitating
traceability and further analysis.

### System Requirements

- Python 3.6 or later.
- Required packages: `numpy`, `Pillow`.

### Installation

Before running the script, ensure all required packages are installed using the following command:

```bash
pip install numpy Pillow
```

### Execution

Run the script from the terminal or command prompt with:

```bash
python augment.py
```

After running the script, verify the augmented data by inspecting the generated images and JSON files in the output
directories. The augmentation should reflect realistic variations of the original images and coherent concatenation of
the text data.


---
*Note: This project and script are intended solely for educational and personal use. Ensure compliance with the terms
and conditions of any interacted API.*