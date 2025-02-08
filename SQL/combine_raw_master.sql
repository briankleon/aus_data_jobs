--create a new script to preserve into history first
insert INTO public.adzuna_jobs_master_history
select *, current_date
from public.adzuna_jobs_master;

--clear master table
TRUNCATE TABLE public.adzuna_jobs_master;

--repopulate master table
INSERT INTO public.adzuna_jobs_master

WITH master AS (
    SELECT title,
           company ,
           location,
           category,
           contract_type,
           contract_time,
           salary_min,
           salary_max,
           created,
           description,
           url,
           timestamp	
FROM public.adzuna_jobs_master_history
where snapshot = (select max(snapshot) from public.adzuna_jobs_master_history)
)

, new AS (
	SELECT * 
	FROM public.adzuna_results_raw
    WHERE timestamp = (select max(timestamp) from public.adzuna_results_raw)
),

combined as (
    SELECT COALESCE(b."Title", a.title) as title,
            COALESCE(b."Company", a.company) as company,
            COALESCE(b."Location", a.location) as location,
            COALESCE(b."Category", a.category) as category,
            COALESCE(b."Contract Type", a.contract_type) as contract_type,
            COALESCE(b."Contract Time", a.contract_time) as contract_time,
            COALESCE(b."Salary Min", a.salary_min) as salary_min,
            COALESCE(b."Salary Max", a.salary_max) as salary_max,
            COALESCE(b."Created", a.created) as created,
            COALESCE(b."Description", a.description) as description,
            COALESCE(b."Redirect URL", a.url) as url,
            COALESCE(b."timestamp", a.timestamp) as timestamp,
            ROW_NUMBER()OVER(PARTITION BY COALESCE(b."Title", a.title), COALESCE(b."Company", a.company), COALESCE(b."Created", a.created) ORDER BY COALESCE(b."timestamp", a.timestamp) DESC) ROW
    FROM master a
    FULL OUTER JOIN new b
    ON a.title = b."Title"
    AND a.company = b."Company"
    AND a.created = b."Created"
)

SELECT title,
       company,
       location,
       category,
       contract_type,
       contract_time,
       salary_min,
       salary_max,
       created,
       description,
       url,
       timestamp
FROM combined
where ROW = 1
