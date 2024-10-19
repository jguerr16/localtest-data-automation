import os
from csv_processor import process_csv
from config import INPUT_FILE_PATH, OUTPUT_FOLDER

def reformat_single_csv_file():
    # Ensure the output folder exists
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # Process the single input file
    print(f"Processing {INPUT_FILE_PATH}...")
    process_csv(INPUT_FILE_PATH, OUTPUT_FOLDER)

if __name__ == "__main__":
    # Reformat the specified CSV file
    reformat_single_csv_file()
