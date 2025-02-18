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
        "max_days_old": 4,
        "content-type": "application/json"
    }

    for term in search_terms:
        page = 1
        all_jobs = []
        params["what"] = term  # Set the search term

        print(f"Starting search for: {term}")
        
        while True:
            print(f"Fetching page {page} for '{term}'...")
            url = f"{base_url}{page}"

            max_retries = 3
            retry_count = 0
            response = None

            # Attempt to fetch this page with retries
            while retry_count < max_retries:
                response = requests.get(url, params=params)
                
                if response.status_code == 200:
                    # Successful fetch, break out of the retry loop
                    break
                else:
                    retry_count += 1
                    wait_time = 10  # seconds to wait before retry
                    print(f"Failed to fetch page {page} for '{term}'. HTTP Status: {response.status_code}. "
                          f"Retrying {retry_count}/{max_retries} in {wait_time} seconds...")
                    time.sleep(wait_time)

            # After trying up to max_retries, if it's still not 200, break out of pagination
            if not response or response.status_code != 200:
                print(f"Max retries exceeded for page {page} of '{term}'. Stopping pagination.")
                if response is not None:
                    print(response.text)  # Optionally print the error text
                break

            # If we got here, response.status_code == 200
            data = response.json()
            job_listings = data.get('results', [])

            if not job_listings:
                print(f"No more results for '{term}', ending pagination.")
                break

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

            # Sleep between page fetches to avoid hitting rate limits
            time.sleep(15)
            page += 1

        # Convert to DataFrame and save to CSV
        if all_jobs:
            jobs_df = pd.DataFrame(all_jobs)
            jobs_df["timestamp"] = datetime.now()
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            suffix = term.lower().replace(" ", "_")

            csv_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            output_csv_path = os.path.join(csv_dir_path, f"jobs_output_data_{suffix}_{timestamp_str}.csv")

            jobs_df.to_csv(output_csv_path, index=False)
            print(f"Data for '{term}' successfully fetched and saved to '{output_csv_path}'")
        else:
            print(f"No job data was fetched for '{term}'")


# Call the function with the specified terms
fetch_jobs_and_save_to_csv(["Data Scientist", "Data Analyst","Data Engineer"])
