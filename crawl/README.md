# Satellite Image Crawler for Baidu Maps

This directory provides a Python script, [img-crawl.py](img-crawl.py), designed to retrieve satellite images from Baidu Maps and convert them into map tiles. The script utilizes the Baidu Maps API to acquire satellite imagery, saving it as map tiles for specific cities. These tiles can be employed in various mapping and visualization projects.

## Cities and Coordinates

The table below lists the cities along with their corresponding bounding coordinates (lower-left and upper-right) and the number of images that can be obtained at a scale of 16:

| City      | Lower-left Coordinates | Upper-right Coordinates | Image Count at Scale=16 |
|-----------|------------------------|-------------------------|-------------------------|
| Beijing   | (39.7555, 116.0392)    | (40.1536, 116.7914)     | 4,592                   |
| Shanghai  | (30.975, 121.975)      | (31.5149, 121.8044)     | 5,244                   |
| Guangzhou | (22.9391, 113.1016)    | (23.1536, 113.6777)     | 3,402                   |
| Shenzhen  | (22.4486, 113.7516)    | (22.8456, 114.6166)     | 4,324                   |
+ Pixel Dimensions: 256x256

## How to Use

1. Clone this repository to your local machine:

```shell
git clone https://github.com/siruzhong/satellite-image-crawl.git
cd satellite-image-crawl
```

2. Install the required dependencies.

3. Update the `ak` variable in the script with your Baidu Map API key. You can register and obtain an API key from the [Baidu Maps API Console](https://lbsyun.baidu.com/apiconsole/center#/home).

4. Adjust the `cities` dictionary in the script to include the cities from which you want to retrieve images, along with their latitude and longitude ranges.

5. Execute the script:

```shell
python satellite_crawl.py
```

The script will procure satellite imagery of the specified cities and save them as map tiles, organized into subdirectories named after each city.

## Important Notes

- The script uses multithreading to download multiple tiles concurrently, which may impose a load on the server. Use responsibly to avoid overwhelming the Baidu Maps servers with excessive requests.

- The downloaded tiles are stored in a directory named `tiles`, with separate subdirectories for each city.

- The script supports both satellite and road map imagery. You can toggle between image types by modifying the `satellite` variable in the script.

- To reduce server load, the script includes a random sleep interval between downloads.

Contributions to the script are welcome, or you may adjust it according to your needs. Enjoy your use!

---
*Note: This project and script are intended solely for educational and personal use. Ensure compliance with the terms and conditions of any interacted API.*