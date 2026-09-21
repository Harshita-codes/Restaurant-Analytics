# Restaurant Analytics

## Project Description

Restaurant Analytics is an end-to-end data engineering and analytics project that transforms restaurant data into business insights.

The project uses four datasets: Customers, Restaurants, Menu Items, and Orders.

Data is ingested into Snowflake, transformed and modeled using dbt, and analyzed through an interactive Streamlit dashboard.

## Technologies Used

- Snowflake
- Snowpipe
- dbt
- SQL
- Python
- Streamlit
- Plotly
- Git & GitHub

## Architecture

CSV Files → Snowflake Internal Stage → Snowpipe → RAW → dbt → Star Schema → Semantic Views → Streamlit

### Data Processing

- Snowflake is used as the centralized data warehouse.
- Snowpipe is used for data ingestion.
- dbt is used for transformation, modeling, testing, and snapshots.
- A Star Schema is created with fact and dimension tables.
- dbt Snapshots implement SCD Type 2 for Customer and Menu Item history.
- Semantic views provide business-ready analytical data.

### Key Analytics

The dashboard provides:

- Revenue and Order KPIs
- Revenue trends
- Top menu items
- Restaurant performance
- Cuisine analysis
- Order channel analysis
- Regional comparison
- Customer loyalty analysis
- Detailed data exploration

## Dashboard Screenshots
<img width="959" height="479" alt="Screenshot 2026-09-22 031113" src="https://github.com/user-attachments/assets/21e08531-072b-4fb2-b5ae-167a72abab68" />

