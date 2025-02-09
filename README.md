# Project Title

This project is a data pipeline to better understand the latest trends in Data jobs in Australia. Data is sourced from Adzuna's API before it is ingested into a postgres database.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)
- [Contact](#contact)

## Installation

Instructions on how to get your project up and running:

### bash/terminal

```bash
# Navigate to the project directory
cd <your root directory>

# Clone the repo
git clone https://github.com/briankleon/aus_data_jobs.git
```

### Software to install

Python
PostgreSQL

### Python packages required

Install dependencies
all packages from the requirements.txt file

### Other set up

Create an account with Adzuna API and note the API_key

### Create .env file in root directory with the below contents

Any fields with "DB_" are from your local instance of PostgreSQL. Fields with "API_" come from Adzuna API account creation.

```bash
DB_USER=<xx>
DB_PASSWORD=<xx>
DB_HOST=<xx>
DB_PORT=<xx>
DB_NAME=<xx>

API_APP_ID=<xx>
API_APP_KEY=<xx>
```

### PostgreSQL

run all SQL statements ending in _DDL to ensure creation of tables used in the pipeline

## Usage

Run the jobs_pipeline.py file to execute the pipeline eg,

```bash
C:/anaconda3/python.exe c:/<root directory>/Python/jobs_pipeline.py
```

## License

Distributed under the MIT License. See LICENSE for more information.