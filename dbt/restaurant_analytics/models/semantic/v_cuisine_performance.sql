{{ config(materialized='view') }}

SELECT
    m.CUISINE,
    SUM(f.QTY) AS TOTAL_QTY,
    COUNT(DISTINCT f.ORDER_ID) AS TOTAL_ORDERS,
    SUM(f.GROSS_AMOUNT) AS GROSS_REVENUE,
    SUM(f.DISCOUNT_AMOUNT) AS DISCOUNT_AMOUNT,
    SUM(f.NET_AMOUNT) AS NET_REVENUE

FROM {{ ref('fact_orders') }} f

JOIN {{ ref('dim_menu_item') }} m
    ON f.MENU_ITEM_KEY = m.MENU_ITEM_KEY

GROUP BY m.CUISINE