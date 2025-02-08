CREATE TABLE adzuna_jobs_master (
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    category TEXT,
    contract_type TEXT,
    contract_time TEXT,
    salary_min TEXT,
    salary_max TEXT,
    created TIMESTAMPTZ NOT NULL,
    description TEXT,
    url TEXT,
    timestamp TIMESTAMP NOT NULL,
    PRIMARY KEY (title, company, created)
);

