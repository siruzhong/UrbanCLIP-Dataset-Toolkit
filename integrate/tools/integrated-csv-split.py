import csv
import os

# Path to the integrated CSV file containing the satellite data
csv_path = "/Users/zhongsiru/project/src/satellite-image-crawl/integrate/output/integrated_satellite_data.csv"
# Root folder where the city-specific CSV files will be stored
root_folder = "/Users/zhongsiru/project/src/satellite-image-crawl/integrate/output"

# List of cities to categorize the data
cities = ["Beijing", "Guangzhou", "Shanghai", "Shenzhen"]
# Initialize a dictionary to hold the data for each city
city_data = {city: [] for city in cities}

# Read the CSV data and organize it into the respective city categories
with open(csv_path, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        for city in cities:
            # Check if the current row belongs to the city in the iteration
            if city in row['satellite_img_name']:
                city_data[city].append(row)
                break  # Break the loop once the correct city is found

# Write the categorized data into separate CSV files for each city
for city, rows in city_data.items():
    # Create a directory path for the current city
    city_folder = os.path.join(root_folder, city)
    # Ensure that the directory exists, create if necessary
    os.makedirs(city_folder, exist_ok=True)
    # Define the path for the city-specific CSV file
    city_csv_path = os.path.join(city_folder, f"{city}.csv")

    # Open the city CSV file for writing
    with open(city_csv_path, 'w', newline='') as city_csv_file:
        # Define the field names (column headers) for the CSV file
        fieldnames = ['satellite_img_name', 'BD09 coordinate', 'WGS84 coordinate',
                      'carbon_emissions (ton)', 'population (unit)', 'gdp (million yuan)']
        # Create a CSV DictWriter object using the fieldnames
        writer = csv.DictWriter(city_csv_file, fieldnames=fieldnames)
        # Write the header (fieldnames) to the CSV file
        writer.writeheader()
        # Write all the rows of data for the current city to the CSV file
        writer.writerows(rows)
