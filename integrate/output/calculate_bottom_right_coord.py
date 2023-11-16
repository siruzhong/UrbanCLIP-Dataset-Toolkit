import pandas as pd
import requests
from loguru import logger

# Replace with your Baidu Map API key (ak)
ak = 'ufbll2CzDR5izZXP3PTt9aWK5Owd4TtG'


# Convert latitude and longitude to Baidu map coordinates
def bd_latlng2xy(zoom, latitude, longitude):
    url = "https://api.map.baidu.com/geoconv/v1/"
    params = {
        "coords": str(longitude) + ',' + str(latitude),
        "from": "5",
        "to": "6",
        "ak": ak,
    }
    response = requests.get(url=url, params=params)
    result = response.json()
    loc = result["result"][0]
    res = 2 ** (18 - zoom)  # Calculate the scaling factor
    x = loc['x'] / res
    y = loc['y'] / res
    return x, y


def bd_xy2latlng(zoom, x, y):
    """Convert BD09 pixel coordinates to WGS84 lat/lng for a given zoom level."""
    res = 2 ** (18 - zoom)
    bd_x = x * 256 * res
    bd_y = y * 256 * res

    params = {
        "coords": f"{bd_x},{bd_y}",
        "from": "6",  # BD09
        "to": "5",  # WGS84
        "ak": ak
    }
    response = requests.get(url="https://api.map.baidu.com/geoconv/v1/", params=params)
    response.raise_for_status()  # Raise an exception for HTTP errors
    loc = response.json()["result"][0]
    return loc['y'], loc['x']  # latitude, longitude


def calculate_bottom_right_coord(top_left_coord, zoom_level):
    top_left_x, top_left_y = bd_latlng2xy(zoom_level, top_left_coord[0], top_left_coord[1])

    # Calculate tile range
    top_left_x = int(top_left_x // 256)
    top_left_y = int(top_left_y // 256)

    # Calculate the bottom-right corner coordinates in Baidu map coordinates
    bottom_right_x = top_left_x + 2
    bottom_right_y = top_left_y - 1

    # Convert the bottom-right coordinates back to latitude and longitude
    bottom_right_latitude, bottom_right_longitude = bd_xy2latlng(zoom_level, bottom_right_x, bottom_right_y)

    return bottom_right_latitude, bottom_right_longitude


# Function to calculate bottom-right coordinates and add them to the DataFrame
def calculate_and_add_bottom_right(row):
    top_left_coord = tuple(map(float, row['WGS84 coordinate'][1:-1].split(', ')))  # Convert to tuple
    zoom_level = 16  # Zoom level 16
    bottom_right_coord = calculate_bottom_right_coord(top_left_coord, zoom_level)
    return bottom_right_coord


# Define a threshold for updating the CSV file
update_threshold = 10  # Update the CSV file every 10 rows

if __name__ == '__main__':
    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv('integrated_satellite_data.csv')

    # Create an empty list to store processed data rows
    processed_rows = []

    # Loop through each row and apply the function
    for index, row in df.iterrows():
        bottom_right_coord = calculate_and_add_bottom_right(row)
        processed_rows.append(row)  # Append the original row
        processed_rows[-1][
            'Bottom Right Coordinate'] = bottom_right_coord  # Update the 'Bottom Right Coordinate' column

        # Check if the threshold is reached and update the CSV file
        if (index + 1) % update_threshold == 0:
            # Create a new DataFrame with processed rows
            updated_df = pd.DataFrame(processed_rows)

            # Save the new DataFrame to a temporary CSV file
            updated_df.to_csv('temp_integrated_satellite_data.csv', index=False)

            logger.info(f"Processed {index + 1} rows. Updating CSV file...")

    # After processing all rows, create a final DataFrame with processed rows
    updated_df = pd.DataFrame(processed_rows)

    # Save the final DataFrame to the CSV file
    updated_df.to_csv('integrated_satellite_data_with_bottom_right.csv', index=False)

    logger.info("CSV file updated with Bottom Right Coordinate.")
