import csv
import os

# Set the path to the integrated satellite data CSV file
csv_path = "/Users/zhongsiru/project/src/satellite-image-crawl/integrate/output/integrated_satellite_data.csv"
# Create a temporary file path in the same directory as the CSV file
temp_path = os.path.join(os.path.dirname(csv_path), "temp.csv")

# Open the original CSV to read data and a temporary CSV to write filtered data
with open(csv_path, 'r') as csvfile, open(temp_path, 'w', newline='') as temp_file:
    # Create a CSV DictReader to read the rows as dictionaries
    reader = csv.DictReader(csvfile)
    # Create a CSV DictWriter to write dictionaries as rows
    writer = csv.DictWriter(temp_file, fieldnames=reader.fieldnames)
    # Write the header to the temporary file
    writer.writeheader()

    # Iterate through each row in the original CSV
    for row in reader:
        # Check if the values for carbon emissions, population, and GDP are all not zero
        if not (float(row['carbon_emissions (ton)']) == 0 and
                float(row['population (unit)']) == 0 and
                float(row['gdp (million yuan)']) == 0):
            # If not all values are zero, write the row to the temporary file
            writer.writerow(row)

# Replace the original CSV file with the temporary file
os.replace(temp_path, csv_path)
