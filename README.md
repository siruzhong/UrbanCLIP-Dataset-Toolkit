# UrbanCLIP Dataset

本仓库提供 UrbanCLIP 相关的所有数据工作，包括卫星图的爬取（潜在数据增强模块），图像描述的生成，以及集成Population、GDP、Carbon Emissions数据到卫星图三大模块。

因此整个项目分为三个目录：
+ crawl: 卫星图爬取
+ caption: 图像描述生成，包括对卫星图对过滤，过滤无效卫星图（森林，海洋，沙漠等）
+ integrate: 数据集成

## Data Crawl
详见：[crawl/README.md](crawl/README.md)

## Image Caption
详见：[caption/README.md](caption/README.md)

## Data Integration

