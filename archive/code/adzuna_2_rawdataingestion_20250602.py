import pandas as pd
from sqlalchemy import create_engine
import os
import shutil
from datetime import datetime
from dotenv import load_dotenv

# Directory containing CSV files
csv_dir_path = "C:/Users/brian/Documents/PythonScripts/jobs_api/v2"
archive_dir_path = os.path.join(csv_dir_path, "archive")

load_dotenv()  # Load environment variables from .env

db_details = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'database': os.getenv('DB_NAME')
}

table_name = "adzuna_results_raw"

# Ensure the archive folder exists
os.makedirs(archive_dir_path, exist_ok=True)

# Create the PostgreSQL connection string
conn_str = f"postgresql://{db_details['user']}:{db_details['password']}@{db_details['host']}:{db_details['port']}/{db_details['database']}"
engine = create_engine(conn_str)

# Iterate over all .csv files in the directory
for filename in os.listdir(csv_dir_path):
    if filename.endswith(".csv"):
        file_path = os.path.join(csv_dir_path, filename)
        print(f"Processing file: {filename}")
        
        # Load CSV into a pandas DataFrame
        try:
            df = pd.read_csv(file_path)

            # Drop duplicates based on key columns
            df1 = df.drop_duplicates(subset=["Title", "Company", "Created", "timestamp"])

            # Insert DataFrame into the PostgreSQL table
            df1.to_sql(table_name, engine, index=False, if_exists='append')
            print(f"Data from {filename} inserted successfully.")
            
            # Move the file to the archive folder
            shutil.move(file_path, os.path.join(archive_dir_path, filename))
            print(f"{filename} moved to archive folder.")

        except Exception as e:
            print(f"Error processing {filename}: {e}")
