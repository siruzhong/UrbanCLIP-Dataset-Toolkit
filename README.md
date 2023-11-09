# UrbanInsight Dataset Toolkit

Welcome to the UrbanInsight Dataset Toolkit, a comprehensive tool chain designed to facilitate the collection, processing, and integration of satellite imagery and associated metadata for urban analysis. This repository encompasses a full pipeline from data acquisition through potential data augmentation modules to the generation of descriptive captions, and the aggregation of key datasets such as Population, GDP, and Carbon Emissions with satellite imagery.

This project is structured into four key directories:
+ `crawl`: For satellite imagery acquisition.
+ `caption`: For generating descriptive captions, including a filtering step to remove ineffective satellite images (like those showing forests, oceans, deserts, etc.).
+ `integrate`: For the integration of datasets.
+ `augment`: For potential data augmentation to enrich the dataset.

## Research and Citation

The work presented in this repository is in conjunction with the research findings published in our paper. For a detailed explanation of the methodologies, results, and implications of our work, please refer to the paper titled [When Urban Region Profiling Meets Large Language Models](https://arxiv.org/abs/2310.18340) available on arXiv. 

If you utilize this dataset, codebase, or methodology in your work, please cite our paper as follows:

```
@misc{yan2023urban,
      title={When Urban Region Profiling Meets Large Language Models}, 
      author={Yibo Yan and Haomin Wen and Siru Zhong and Wei Chen and Haodong Chen and Qingsong Wen and Roger Zimmermann and Yuxuan Liang},
      year={2023},
      eprint={2310.18340},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```


## Directory Overview

### Data Crawl
The `crawl` directory contains scripts and tools for scraping satellite images. It includes the functionality to target specific geographical areas and download images accordingly.

Detailed instructions and information are available at: [crawl/README.md](crawl/README.md).

### Image Caption
In the `caption` directory, you will find the necessary scripts to generate captions for the satellite images. This step involves advanced image processing techniques and the application of machine learning models.

For a deeper understanding, refer to: [caption/README.md](caption/README.md).

### Data Integration
The `integrate` directory is responsible for combining the scraped satellite images with relevant metadata such as Population, GDP, and Carbon Emissions. This provides a rich, multi-dimensional dataset that is more useful for analysis and modeling.

Check out the specifics at: [integrate/README.md](integrate/README.md).

### Data Augmentation
The `augment` directory proposes an optional step to increase the volume and diversity of the dataset through image and text data augmentation techniques.

Learn more by visiting: [augment/README.md](augment/README.md).

## Getting Started

To get started with this project, clone the repository to your local machine. Ensure you have Python installed along with all the necessary libraries specified in the individual README files for each module.

### Prerequisites

Before running any scripts, please install the required dependencies listed in each module's README to ensure smooth execution of the programs.

### Running the Modules

Each module can be run independently by navigating to its respective directory and following the instructions provided in its README file.

## Support

For any questions or issues, please open an issue on the repository, and we'll be glad to help.

By providing a streamlined workflow from image collection to data integration, the UrbanInsight Dataset project aims to empower researchers, data scientists, and urban planners with the tools needed to analyze and interpret the ever-changing landscape of urban environments.
