import pandas as pd
import requests
import os
from config import GOOGLE_MAPS_API_KEY

# Convert coordinates to city and country using Google Maps API
def get_city_and_country_from_coordinates(lat, lng):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={GOOGLE_MAPS_API_KEY}"
    
    try:
        # Make a request to the Google Maps API
        response = requests.get(url, timeout=5)
        print(f"API request URL: {url}")
        response.raise_for_status()  # Raises HTTPError for bad responses (4XX, 5XX)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching city and country from coordinates ({lat}, {lng}): {e}")
        return "Unknown City", "Unknown Country"
    
    if response.status_code == 200:
        results = response.json().get("results", [])
        city = "Unknown City"
        country = "Unknown Country"
        
        if results:
            # Extract city and country from the response
            for component in results[0]['address_components']:
                if 'locality' in component['types']:  # City name
                    city = component['long_name']
                if 'country' in component['types']:  # Country name
                    country = component['long_name']
        else:
            print(f"No results found for coordinates ({lat}, {lng})")
            
        return city, country
    return "Unknown City", "Unknown Country"


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

    # Add a 'city' and 'country' column based on the 'Location Name'
    def get_city_and_country(location_name):
        coordinates = is_coordinates(location_name)
        if coordinates:
            lat, lng = coordinates
            print(f"Fetching city and country for coordinates: {lat}, {lng}")
            return get_city_and_country_from_coordinates(lat, lng)
        else:
            print(f"Using place name: {location_name}")
            # If it's a place name, return it as both city and country (or perform an API call if desired)
            return location_name, "Unknown Country"

    # Apply the function to the 'Location Name' column and unpack the city and country
    df[['city', 'country']] = df['Location Name'].apply(lambda loc: pd.Series(get_city_and_country(loc)))

    # Replace the 'Location Name' with the city names
    df['Location Name'] = df['city']

    # Save the processed CSV with both city and country
    output_file = os.path.join(output_folder, file_path.split('/')[-1].replace('.csv', '_processed.csv'))
    df.to_csv(output_file, index=False)
    print(f"Processed CSV saved as: {output_file}")
    return output_file