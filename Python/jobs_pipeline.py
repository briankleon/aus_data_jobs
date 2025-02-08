import subprocess
import os
from dotenv import load_dotenv

# Move up one level from the "Python" folder to the actual project root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PYTHON_DIR = os.path.join(BASE_DIR, "Python")  # Now correctly points to Python/
SQL_DIR = os.path.join(BASE_DIR, "SQL")  # Now correctly points to SQL/

def fetch_jobs():
    """Runs the Adzuna API call script."""
    script_path = os.path.join(PYTHON_DIR, "adzuna_api_call_v2.py")
    print(f"Running API call: {script_path}")
    subprocess.run(["python", script_path], check=True)

def ingest_jobs():
    """Runs the raw data ingestion script."""
    script_path = os.path.join(PYTHON_DIR, "adzuna_2_rawdataingestion.py")
    print(f"Running raw data ingestion: {script_path}")
    subprocess.run(["python", script_path], check=True)

def run_sql():
    """Executes the SQL script to update the database."""
    load_dotenv()  # Load environment variables from the .env file
    
    # Set PGPASSWORD for PostgreSQL authentication
    env = os.environ.copy()
    env["PGPASSWORD"] = os.getenv("DB_PASSWORD")

    sql_path = os.path.join(SQL_DIR, "combine_raw_master.sql")
    print(f"Running SQL script: {sql_path}")

    subprocess.run([
        "psql",
        "-d", os.getenv("DB_NAME"),  # Database name
        "-U", os.getenv("DB_USER"),  # Username
        "-h", os.getenv("DB_HOST"),  # Host
        "-p", os.getenv("DB_PORT"),  # Port
        "-f", sql_path  # Path to the SQL script
    ], env=env, check=True)

if __name__ == "__main__":
    try:
        print("Running job pipeline...")
        fetch_jobs()
        ingest_jobs()
        run_sql()
        print("Pipeline completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Pipeline failed with error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
