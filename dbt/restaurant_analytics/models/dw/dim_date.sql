{{ config(
    materialized='table'
) }}

WITH date_bounds AS (

    SELECT
        MIN(ORDER_DATE) AS MIN_DATE,
        MAX(ORDER_DATE) AS MAX_DATE
    FROM {{ ref('stg_orders') }}

),

date_series AS (

    SELECT
        DATEADD(
            DAY,
            SEQ4(),
            MIN_DATE
        ) AS FULL_DATE

    FROM date_bounds,
         TABLE(GENERATOR(ROWCOUNT => 5000))

)

SELECT
    TO_NUMBER(TO_CHAR(FULL_DATE, 'YYYYMMDD')) AS DATE_KEY,
    FULL_DATE,
    DAY(FULL_DATE) AS DAY_OF_MONTH,
    DAYNAME(FULL_DATE) AS DAY_NAME,
    WEEKOFYEAR(FULL_DATE) AS WEEK_OF_YEAR,
    MONTH(FULL_DATE) AS MONTH,
    MONTHNAME(FULL_DATE) AS MONTH_NAME,
    QUARTER(FULL_DATE) AS QUARTER,
    YEAR(FULL_DATE) AS YEAR

FROM date_series

WHERE FULL_DATE <= (
    SELECT MAX_DATE
    FROM date_bounds
)

ORDER BY FULL_DATE