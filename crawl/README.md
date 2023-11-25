# Satellite Image Crawler for Baidu Maps

This directory provides a Python script, [img-crawl.py](img-crawl.py), designed to retrieve satellite images from Baidu
Maps and convert them into map tiles. The script utilizes the Baidu Maps API to acquire satellite imagery, saving it as
map tiles for specific cities. These tiles can be employed in various mapping and visualization projects.

## Cities and Coordinates

The table below lists the cities along with their corresponding bounding coordinates (lower-left and upper-right) and
the number of images that can be obtained at a scale of 16:

| City      | Lower-left Coordinates | Upper-right Coordinates | Image Count at Scale=16 |
|-----------|------------------------|-------------------------|-------------------------|
| Beijing   | (39.7555, 116.0392)    | (40.1536, 116.7914)     | 4,592                   |
| Shanghai  | (30.975, 121.975)      | (31.5149, 121.8044)     | 5,244                   |
| Guangzhou | (22.9391, 113.1016)    | (23.1536, 113.6777)     | 3,402                   |
| Shenzhen  | (22.4486, 113.7516)    | (22.8456, 114.6166)     | 4,324                   |

+ Pixel Dimensions: 256x256

To make the table less visually overwhelming, we can split it into two columns. Here's the revised section with a
shortened table:

---

## How to Use

1. **Clone the Repository**  
   Begin by cloning the repository to your local machine with the following commands:
   ```shell
   git clone https://github.com/siruzhong/satellite-image-crawl.git
   cd satellite-image-crawl
   ```

2. **Install Dependencies**  
   Install all required dependencies specified in the project.

3. **Configure API Key**  
   Update the `ak` variable in the script with your Baidu Map API key, obtainable from
   the [Baidu Maps API Console](https://lbsyun.baidu.com/apiconsole/center#/home).

4. **Set City Parameters**  
   Modify the cities dictionary in the script to include the desired cities. To define the area for image retrieval, use
   the Baidu Maps Point Coordinate tool at https://api.map.baidu.com/lbsapi/getpoint/index.html to determine the
   latitude and longitude range of your region of interest, specifically the coordinates for the lower left (southwest)
   and upper right (northeast) corners.
5. **Adjust Zoom Level**  
   The zoom level in satellite image retrieval dictates the scale represented by each pixel. A correspondence table is
   provided to help you choose the correct zoom level for your needs. In this project, zoom level 16, which corresponds
   to a 256x256 pixel image tile, represents an area of approximately 1km by 1km.

6. **Run the Script**  
   Execute the script to start retrieving satellite images:
   ```shell
   python img-img-crawl.py
   ```

The table below outlines the approximate scales associated with different zoom levels, enabling you to fine-tune the
image resolution as needed:

| Zoom Level | Scale | Zoom Level | Scale   |
|------------|-------|------------|---------|
| 23         | 1m    | 12         | 5km     |
| 22         | 2m    | 11         | 10km    |
| 21         | 5m    | 10         | 20km    |
| 20         | 10m   | 9          | 25km    |
| 19         | 20m   | 8          | 50km    |
| 18         | 50m   | 7          | 100km   |
| 17         | 100m  | 6          | 200km   |
| 16         | 200m  | 5          | 500km   |
| 15         | 500m  | 4          | 1000km  |
| 14         | 1km   | 3          | 2000km  |
| 13         | 2km   | 2          | 5000km  |
|            |       | 1          | 10000km | 

Please adjust the zoom level based on the spatial resolution your research necessitates.

--- 

This revised section is more concise, and the table is split to make it easier to read and visually appealing.

## Important Notes

- The script uses multithreading to download multiple tiles concurrently, which may impose a load on the server. Use
  responsibly to avoid overwhelming the Baidu Maps servers with excessive requests.

- The downloaded tiles are stored in a directory named `tiles`, with separate subdirectories for each city.

- The script supports both satellite and road map imagery. You can toggle between image types by modifying
  the `satellite` variable in the script.

- To reduce server load, the script includes a random sleep interval between downloads.

Contributions to the script are welcome, or you may adjust it according to your needs. Enjoy your use!

---
*Note: This project and script are intended solely for educational and personal use. Ensure compliance with the terms
and conditions of any interacted API.*