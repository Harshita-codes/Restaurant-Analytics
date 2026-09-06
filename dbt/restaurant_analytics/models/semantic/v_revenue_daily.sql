{{ config(materialized='view') }}

SELECT
    d.FULL_DATE,
    d.YEAR,
    d.MONTH,
    d.MONTH_NAME,
    d.QUARTER,

    SUM(f.GROSS_AMOUNT) AS GROSS_REVENUE,
    SUM(f.DISCOUNT_AMOUNT) AS DISCOUNT_AMOUNT,
    SUM(f.NET_AMOUNT) AS NET_REVENUE,

    SUM(f.QTY) AS TOTAL_QTY,
    COUNT(DISTINCT f.ORDER_ID) AS TOTAL_ORDERS,
    COUNT(*) AS ORDER_LINES

FROM {{ ref('fact_orders') }} f

JOIN {{ ref('dim_date') }} d
    ON f.DATE_KEY = d.DATE_KEY

GROUP BY
    d.FULL_DATE,
    d.YEAR,
    d.MONTH,
    d.MONTH_NAME,
    d.QUARTER