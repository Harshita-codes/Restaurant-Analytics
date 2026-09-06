{{ config(
    materialized='table'
) }}

SELECT
    MD5(RESTAURANT_ID) AS RESTAURANT_KEY,
    RESTAURANT_ID,
    RESTAURANT_NAME,
    REGION,
    CITY,
    STATE,
    COUNTRY,
    OPEN_DATE,
    SERVICE_MODES,
    STATUS
FROM {{ ref('stg_restaurants') }}