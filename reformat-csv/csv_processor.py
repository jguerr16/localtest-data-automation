import pandas as pd
import requests
import os
from config import GOOGLE_MAPS_API_KEY

# Convert coordinates to city using Google Maps API
def get_city_from_coordinates(lat, lng):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={GOOGLE_MAPS_API_KEY}"
    
    try:
        response = requests.get(url, timeout=5)  # Add timeout to avoid long wait times
        print(f"API request URL: {url}")
        print(f"API response status: {response.status_code}")
        response.raise_for_status()  # Raises HTTPError for bad responses (4XX, 5XX)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching city from coordinates ({lat}, {lng}): {e}")
        return "Unknown City"
    
    if response.status_code == 200:
        results = response.json().get("results", [])
        if results:
            for component in results[0]['address_components']:
                if 'locality' in component['types']:  # 'locality' corresponds to city
                    return component['long_name']
        else:
            print(f"No results found for coordinates ({lat}, {lng})")
    return "Unknown City"

# Check if a string is a coordinate pair (latitude, longitude)
def is_coordinates(location_name):
    try:
        lat, lng = map(float, location_name.split(","))
        return lat, lng
    except ValueError:
        return None

# Process the CSV and handle location name (coordinates or place name)
def process_csv(file_path, output_folder):
    print(f"Starting to process the CSV file: {file_path}")

    try:
        df = pd.read_csv(file_path)
        print(f"Successfully read CSV file with {len(df)} rows.")
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    if 'Location Name' not in df.columns:
        print(f"Missing 'Location Name' column in {file_path}")
        return

    print(f"Processing {len(df)} rows...")  # Log how many rows we are processing

    # Add a 'city' column based on the 'Location Name'
    def get_city(location_name):
        coordinates = is_coordinates(location_name)
        if coordinates:
            lat, lng = coordinates
            print(f"Fetching city for coordinates: {lat}, {lng}")
            return get_city_from_coordinates(lat, lng)
        else:
            print(f"Using place name: {location_name}")
            return location_name  # If it's a place name, return as-is

    # Apply the function to the 'Location Name' column
    df['city'] = df['Location Name'].apply(get_city)

    # **Update the 'Location Name' column to replace coordinates with city names**
    df['Location Name'] = df['city']  # Replace the 'Location Name' with the city names

    # Save the processed CSV
    output_file = os.path.join(output_folder, file_path.split('/')[-1].replace('.csv', '_processed.csv'))
    df.to_csv(output_file, index=False)
    print(f"Processed CSV saved as: {output_file}")
    return output_file