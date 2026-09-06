{{ config(materialized='view') }}

SELECT
    m.MENU_ITEM_ID,
    m.ITEM_NAME,
    m.ITEM_TYPE,
    m.CUISINE,
    m.DIET_TYPE,

    SUM(f.QTY) AS TOTAL_QTY,
    COUNT(DISTINCT f.ORDER_ID) AS TOTAL_ORDERS,

    SUM(f.GROSS_AMOUNT) AS GROSS_REVENUE,
    SUM(f.DISCOUNT_AMOUNT) AS DISCOUNT_AMOUNT,
    SUM(f.NET_AMOUNT) AS NET_REVENUE,

    AVG(f.UNIT_PRICE) AS AVG_UNIT_PRICE

FROM {{ ref('fact_orders') }} f

JOIN {{ ref('dim_menu_item') }} m
    ON f.MENU_ITEM_KEY = m.MENU_ITEM_KEY

GROUP BY
    m.MENU_ITEM_ID,
    m.ITEM_NAME,
    m.ITEM_TYPE,
    m.CUISINE,
    m.DIET_TYPE