import requests
import json
import pandas as pd
import os
import time
from datetime import datetime
from dotenv import load_dotenv

def fetch_jobs_and_save_to_csv(search_terms):
    # API details
    base_url = "https://api.adzuna.com/v1/api/jobs/au/search/"

    load_dotenv()  # Load environment variables from .env

    params = {
        "app_id": os.getenv('API_APP_ID'),
        "app_key": os.getenv('API_APP_KEY'),
        "where": "Australia",
        "results_per_page": 50,
        "max_days_old": 2,
        "content-type": "application/json"
    }

    for term in search_terms:
        page = 1
        all_jobs = []
        params["what"] = term  # Set the search term

        print(f"Starting search for: {term}")
        
        while True:
            print(f"Fetching page {page} for '{term}'...")
            # Update URL with the current page
            url = f"{base_url}{page}"
            response = requests.get(url, params=params)

            if response.status_code == 200:
                # Parse JSON response
                data = response.json()

                # Extract job listings
                job_listings = data.get('results', [])

                if not job_listings:
                    print(f"No more results for '{term}', ending pagination.")
                    break

                # Process the data
                for job in job_listings:
                    all_jobs.append({
                        "Title": job.get("title", ""),
                        "Company": job.get("company", {}).get("display_name", ""),
                        "Location": job.get("location", {}).get("display_name", ""),
                        "Category": job.get("category", {}).get("label", ""),
                        "Contract Type": job.get("contract_type", ""),
                        "Contract Time": job.get("contract_time", ""),
                        "Salary Min": job.get("salary_min", ""),
                        "Salary Max": job.get("salary_max", ""),
                        "Created": job.get("created", ""),
                        "Description": job.get("description", "").replace("\n", " "),
                        "Redirect URL": job.get("redirect_url", ""),
                    })

                # Wait for 5 seconds before the next request
                time.sleep(15)
                page += 1
            else:
                print(f"Failed to fetch page {page} for '{term}'. HTTP Status: {response.status_code}")
                print(response.text)
                break

        # Convert to DataFrame and save to CSV
        if all_jobs:
            jobs_df = pd.DataFrame(all_jobs)

            # Add a timestamp field to the data
            jobs_df["timestamp"] = datetime.now()

            # Generate a timestamp for the filename
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Determine file suffix
            suffix = term.lower().replace(" ", "_")

            csv_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            output_csv_path = os.path.join(csv_dir_path, f"jobs_output_data_{suffix}_{timestamp_str}.csv")

            jobs_df.to_csv(output_csv_path, index=False)
            print(f"Data for '{term}' successfully fetched and saved to '{output_csv_path}'")
        else:
            print(f"No job data was fetched for '{term}'.")

# Call the function with the specified terms
fetch_jobs_and_save_to_csv(["Data Analyst","Data Engineer", "Data Scientist"])
