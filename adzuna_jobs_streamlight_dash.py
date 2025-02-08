import streamlit as st
import pandas as pd
import psycopg2
import altair as alt
from dotenv import load_dotenv
import os

# Set up the page with a wide layout and custom title.
st.set_page_config(page_title="Australian Data Jobs", layout="wide")

st.markdown("""
    <style>
    body {
        background-color: #f5f5f5;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .main-header {
        text-align: center;
        font-size: 2.5em;  /* Adjusted for responsiveness */
        color: #333;
    }
    .kpi-container {
        display: flex;
        justify-content: space-between;
        margin-bottom: 100px;
    }
    .container {
        background-color: #fff;
        border-radius: 8px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
    }
    .stMetric {
        text-align: left !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --------------------------
# Data Loading Function
# --------------------------

@st.cache_data
def load_data():

    load_dotenv()  # Load environment variables from .env

    conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)

    query = "SELECT * FROM adzuna_jobs_streamlit_dashboard;"  # Replace with your actual view name.
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Load the data.
df = load_data()

# Convert the "created" field to datetime.
if "created" in df.columns:
    df["created"] = pd.to_datetime(df["created"])

    # Extract year and month from the created column
    #df["created_year_month"] = df["created"].dt.to_period("M")

    # Drop duplicates based on title, company, and created_year_month
    #df = df.drop_duplicates(subset=["title", "company", "created_year_month"])

    # Get current date (without time)
    current_date = pd.Timestamp.today().normalize()

    # Filter out future dates
    df = df[df['created'] <= current_date]

###########################################################
# Function to create binary fields for predefined skills
###########################################################

def add_skill_columns(df, skills):
    for skill in skills:
        df[skill] = df['description'].str.contains(skill, case=False, na=False).astype(int)
    return df

# Predefined list of skills
skills_list = [
    "Python", "SQL", "Excel", "Power BI", "Tableau", "AWS", "Azure","GCP","Spark","Snowflake",
    "Databricks","dbt","Mage"
]

# Add binary skill columns
if "description" in df.columns:
    df = add_skill_columns(df, skills_list)
###########################################################

# --------------------------
# Sidebar: Enhanced Filters
# --------------------------
st.sidebar.header("Filters")

# 🎚️ Date Range Slider
if "created" in df.columns:
    min_date = df["created"].min().date()
    max_date = df["created"].max().date()
    
    # Convert dates to ordinal format for Streamlit slider
    date_range = st.sidebar.slider(
        "Select Date Range", 
        min_value=min_date, 
        max_value=max_date, 
        value=(min_date, max_date),
        format="YYYY-MM-DD"
    )
    
    # Apply date filter
    df = df[(df["created"].dt.date >= date_range[0]) & (df["created"].dt.date <= date_range[1])]

# 📂 Job Family Filter (Dropdown)
if "title_data_family" in df.columns:
    job_families = df["title_data_family"].unique().tolist()
    selected_families = st.sidebar.multiselect(
        "Select Job Families", 
        options=job_families, 
        default=job_families  # Default: Show all
    )
    
    # Apply filter
    df = df[df["title_data_family"].isin(selected_families)]

# --------------------------
# Last Updated Timestamp (Top Right Corner)
# --------------------------

if "created" in df.columns:
    last_updated = df["created"].max().strftime("%Y-%m-%d %H:%M:%S")  # Format as 'YYYY-MM-DD HH:MM:SS'
    
    # Display in the top right corner
    kpi_col1, kpi_col2, kpi_col3 = st.columns([2, 1, 1])  # Adjust spacing
    with kpi_col3:
        st.markdown(f"""
            <div style="text-align: right; font-size: 16px; color: #666;">
                <b>Last Updated:</b> {last_updated}
            </div>
        """, unsafe_allow_html=True)

# --------------------------
# Main Dashboard Header
# --------------------------
st.markdown('<div class="main-header">Australian Data Jobs</div>', unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# --------------------------
# KPI: Total Job Listings for Last Two Complete Weeks
# --------------------------

# Ensure "created" field exists
if "created" in df.columns:
    latest_week_start = (df["created"].max().to_period("W").start_time) - pd.Timedelta(weeks=1)  # Last complete week's Monday
    previous_week_start = latest_week_start - pd.Timedelta(weeks=1)  # Two weeks ago Monday
    
    # Filter jobs for the last two complete weeks
    df_latest_week = df[(df["created"] >= latest_week_start) & (df["created"] < latest_week_start + pd.Timedelta(weeks=1))]
    df_previous_week = df[(df["created"] >= previous_week_start) & (df["created"] < latest_week_start)]
    
    # Calculate job counts
    latest_week_job_count = len(df_latest_week)
    previous_week_job_count = len(df_previous_week)
    
    # Calculate % change
    if previous_week_job_count > 0:
        percent_change = ((latest_week_job_count - previous_week_job_count) / previous_week_job_count) * 100
    else:
        percent_change = 0  # Avoid division by zero

    # Determine color (green for increase, red for decrease, grey for no change)
    if percent_change > 0:
        delta_color = "🟢"
    elif percent_change < 0:
        delta_color = "🔴"
    else:
        delta_color = "⚪"

# --------------------------
# KPI: Total Job Listings for Last Two Complete Months
# --------------------------
if "created" in df.columns:
    latest_month_start = (df["created"].max().to_period("M").start_time) - pd.DateOffset(months=1)  # Last complete month's start
    previous_month_start = latest_month_start - pd.DateOffset(months=1)  # Two months ago start
    
    # Filter jobs for the last two complete months
    df_latest_month = df[(df["created"] >= latest_month_start) & (df["created"] < latest_month_start + pd.DateOffset(months=1))]
    df_previous_month = df[(df["created"] >= previous_month_start) & (df["created"] < latest_month_start)]
    
    # Calculate job counts
    latest_month_job_count = len(df_latest_month)
    previous_month_job_count = len(df_previous_month)
    
    # Calculate % change
    if previous_month_job_count > 0:
        month_percent_change = ((latest_month_job_count - previous_month_job_count) / previous_month_job_count) * 100
    else:
        month_percent_change = 0  # Avoid division by zero

    # Determine color for the KPI
    if month_percent_change > 0:
        month_delta_color = "🟢"
    elif month_percent_change < 0:
        month_delta_color = "🔴"
    else:
        month_delta_color = "⚪"

# --------------------------
# KPI: Weekly Change in Average Salary (Last Two Complete Weeks)
# --------------------------
if "created" in df.columns and "annualized_salary" in df.columns:
    latest_week_avg_salary = df_latest_week["annualized_salary"].mean()
    previous_week_avg_salary = df_previous_week["annualized_salary"].mean()

    # Calculate percentage change
    if previous_week_avg_salary > 0:
        weekly_salary_percent_change = ((latest_week_avg_salary - previous_week_avg_salary) / previous_week_avg_salary) * 100
    else:
        weekly_salary_percent_change = 0  # Avoid division by zero

    # Determine color for weekly salary change
    if weekly_salary_percent_change > 0:
        weekly_salary_delta_color = "🟢"
    elif weekly_salary_percent_change < 0:
        weekly_salary_delta_color = "🔴"
    else:
        weekly_salary_delta_color = "⚪"

# --------------------------
# KPI: Monthly Change in Average Salary (Last Two Complete Months)
# --------------------------
if "created" in df.columns and "annualized_salary" in df.columns:
    latest_month_avg_salary = df_latest_month["annualized_salary"].mean()
    previous_month_avg_salary = df_previous_month["annualized_salary"].mean()

    # Calculate percentage change
    if previous_month_avg_salary > 0:
        monthly_salary_percent_change = ((latest_month_avg_salary - previous_month_avg_salary) / previous_month_avg_salary) * 100
    else:
        monthly_salary_percent_change = 0  # Avoid division by zero

    # Determine color for monthly salary change
    if monthly_salary_percent_change > 0:
        monthly_salary_delta_color = "🟢"
    elif monthly_salary_percent_change < 0:
        monthly_salary_delta_color = "🔴"
    else:
        monthly_salary_delta_color = "⚪"


# --------------------------
# KPI Row: Job Listing and Salary Changes
# --------------------------

if "created" in df.columns:
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

    # Job Listing Change (Weekly)
    with kpi_col1:
        st.metric(
            label="Job Listing Change (Weekly)", 
            value=f"{latest_week_job_count:,}", 
            delta=f"{percent_change:.1f}% {delta_color}"
        )

    # Job Listing Change (Monthly)
    with kpi_col2:
        st.metric(
            label="Job Listing Change (Monthly)", 
            value=f"{latest_month_job_count:,}", 
            delta=f"{month_percent_change:.1f}% {month_delta_color}"
        )

    # Weekly Salary Change
    if "annualized_salary" in df.columns:
        with kpi_col3:
            st.metric(
                label="Salary Change (Weekly)", 
                value=f"${latest_week_avg_salary:,.0f}", 
                delta=f"{weekly_salary_percent_change:.1f}% {weekly_salary_delta_color}"
            )

    # Monthly Salary Change
    if "annualized_salary" in df.columns:
        with kpi_col4:
            st.metric(
                label="Salary Change (Monthly)", 
                value=f"${latest_month_avg_salary:,.0f}", 
                delta=f"{monthly_salary_percent_change:.1f}% {monthly_salary_delta_color}"
            )        


# --------------------------
# Dashboard Layout: 2 Rows x 2 Columns
# --------------------------
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

# Top Left: Weekly Job Listings by Job Family
with col1:
    st.markdown("### Job Listings Weekly")
    if "created" in df.columns and "title_data_family" in df.columns:
        # Group data by week and job family
        df_weekly = df.groupby([pd.Grouper(key="created", freq="W-MON"), "title_data_family"]).size().reset_index(name="job_count")
        df_weekly.rename(columns={"created": "week_begin"}, inplace=True)
        df_weekly["week_begin"] = df_weekly["week_begin"].dt.strftime("%b %d")  # Format as 'Month Day' (e.g., Jan 3)

        # Create the line chart
        line_chart = alt.Chart(df_weekly).mark_line(point=True).encode(
            x=alt.X("week_begin:N", title="Week Beginning"),
            y=alt.Y("job_count:Q", title="Job Listing Count"),
            color=alt.Color("title_data_family:N", title="Job Family"),
        ).configure_legend(
            orient='bottom',  # Move legend to the bottom
            direction='horizontal'  # Arrange legend items horizontally
        ).properties(
            height=400,
            width=600
        )

        st.altair_chart(line_chart, use_container_width=True)
    else:
        st.write("Required fields ('created' or 'title_data_family') are not available.")

# Visual 2: Sideways Bar Chart of Skills Count (Top Right)
with col2:
    st.markdown("### # Most common Skills")
    st.markdown('<div class="container">', unsafe_allow_html=True)

    # Ensure skill columns exist in the dataframe
    if any(skill in df.columns for skill in skills_list):
        # Calculate the sum for each skill column with exact match
        skill_counts = {skill: df[skill].sum() for skill in skills_list if skill in df.columns}

        # Convert the counts to a dataframe
        skills_df = pd.DataFrame(list(skill_counts.items()), columns=["Skill", "Count"])
        skills_df.sort_values("Count", ascending=False, inplace=True)

        # Create a sideways bar chart using Altair
        bar_chart = alt.Chart(skills_df).mark_bar().encode(
            x=alt.X("Count:Q", title="Count"),
            y=alt.Y("Skill:N", sort="-x", title="Skill"),
            tooltip=["Skill", "Count"]
        ).properties(height=400)

        st.altair_chart(bar_chart, use_container_width=True)
    else:
        st.write("No skill columns available.")
    st.markdown('</div>', unsafe_allow_html=True)

# Visual 3: Horizontal Box-and-Whisker Plot for Annualized Salary by Job Family (Bottom Left)
with col3:
    st.markdown("### Salary Distribution by Title")
    st.markdown('<div class="container">', unsafe_allow_html=True)

    # Ensure required fields exist
    if "annualized_salary" in df.columns and "title_data_family" in df.columns:
        # Remove rows with missing salary values
        df_filtered = df.dropna(subset=["annualized_salary", "title_data_family"])

        # Create the horizontal box-and-whisker plot using Altair
        box_plot = alt.Chart(df_filtered).mark_boxplot(extent="min-max").encode(
            y=alt.Y("title_data_family:N", title="Job Family"),  # Job Family on Y-axis
            x=alt.X("annualized_salary:Q", title="Annualized Salary (AUD)"),  # Salary on X-axis
            color=alt.Color("title_data_family:N", legend=None)  # Color by job family
        ).properties(height=400)

        st.altair_chart(box_plot, use_container_width=True)
    else:
        st.write("Required fields ('annualized_salary' or 'title_data_family') are not available.")
    st.markdown('</div>', unsafe_allow_html=True)

# Visual 4: Scrollable Sample Dataframe (Bottom Right)
with col4:
    st.markdown("### Data Sample Job Listings")
    st.markdown('<div class="container">', unsafe_allow_html=True)

    # Define the columns to display
    selected_columns = [
        "title", "company","created", "location", "url"
    ]

    # Check if the required columns exist in the dataframe
    if all(col in df.columns for col in selected_columns):
        # Prepare a subset of the dataframe
        sample_df = df[selected_columns].head(50)  # Limit rows for scrolling

        # # Format the annualized_salary column (remove decimals and add commas)
        # sample_df["annualized_salary"] = sample_df["annualized_salary"].apply(
        #     lambda x: f"${int(x):,}" if pd.notna(x) else "N/A"
        # )

        # Format the created column (remove time, show only date)
        sample_df["created"] = sample_df["created"].dt.strftime("%Y-%m-%d")

        # Convert the URL column to clickable links
        sample_df["url"] = sample_df["url"].apply(
            lambda x: f'<a href="{x}" target="_blank">Link</a>' if pd.notna(x) else "N/A"
        )

        # Render the formatted dataframe with Streamlit's markdown
        st.markdown(
            sample_df.to_html(escape=False, index=False), 
            unsafe_allow_html=True
        )
    else:
        st.write("Required columns are not available in the data.")
    st.markdown('</div>', unsafe_allow_html=True)
