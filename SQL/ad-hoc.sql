SELECT title_data_family, title, company, COUNT (*)
FROM adzuna_jobs_streamlit_dashboard
GROUP BY 1,2,3
ORDER BY COUNT(*) DESC