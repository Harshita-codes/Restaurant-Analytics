# Snowflake SQL

This folder contains the Snowflake setup, ingestion, Snowpipe, and validation SQL
used in the Restaurant Analytics project.

## Files

- `01_database_and_stage.sql` — database/schema selection, CSV file format, and internal stage.
- `02_raw_tables.sql` — RAW layer tables for customers, restaurants, menu items, and orders.
- `03_load_raw_data.sql` — loading CSV files from the internal stage into RAW using `COPY INTO`.
- `04_snowpipes.sql` — Snowpipe definitions and pipe-status checks.
- `05_validation_queries.sql` — ingestion reconciliation, duplicate checks, NULL checks, fact checks, and semantic-view checks.

> Credentials and passwords are intentionally not included.
