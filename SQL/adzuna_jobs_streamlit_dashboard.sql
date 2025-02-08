drop view public.adzuna_jobs_streamlit_dashboard;

create view public.adzuna_jobs_streamlit_dashboard AS

WITH master_data as (

select case when lower(title) like '%data scientist%' THEN 'Data Scientist'
            when lower(title) like '%data analyst%' THEN 'Data Analyst'
            when lower(title) like '%data engineer%' THEN 'Data Engineer'
       end as title_data_family,
       title,
       company,
       date(created) as created,
       contract_type,
       salary_min,
       ROUND(CAST(salary_min AS float)) AS salary_min_new,
       salary_max,
       ROUND(CAST(salary_max AS float)) AS salary_max_new,
       location,
       url,
       description
from public.adzuna_jobs_master
where lower(title) like '%data analyst%'
or lower(title) like '%data engineer%'
or lower(title) like '%data scientist%'
) ,

transformation as (
SELECT * 
     ,CASE WHEN LENGTH(salary_min) >= 7 THEN (salary_min_new + salary_max_new) / 2  
           WHEN LENGTH(salary_min) IN (4,5) AND salary_min_new < 300 THEN ((salary_min_new * 1000) + (salary_max_new * 1000)) / 2 
           WHEN contract_type = 'contract' and salary_min_new > 300 and LENGTH(salary_min) IN (5,6) THEN ((salary_min_new * 260) + (salary_max_new * 260)) / 2 
      end annualized_salary
FROM master_data
order by salary_min_new
)

SELECT title_data_family,
       title,
       company,
       created,
       salary_min_new,
       salary_max_new,
       annualized_salary,       
       location,
       url,
       description
from transformation