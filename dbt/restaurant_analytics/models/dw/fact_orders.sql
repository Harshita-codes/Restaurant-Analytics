{{ config(
    materialized='table'
) }}

SELECT
    o.ORDER_ID,
    o.ORDER_LINE_ID,

    d.DATE_KEY,
    c.CUSTOMER_KEY,
    r.RESTAURANT_KEY,
    m.MENU_ITEM_KEY,

    o.ORDER_CHANNEL,
    o.QTY,
    o.UNIT_PRICE,
    o.DISCOUNT_PCT,
    o.PAYMENT_TYPE,
    o.ORDER_STATUS,

    o.QTY * o.UNIT_PRICE AS GROSS_AMOUNT,

    (o.QTY * o.UNIT_PRICE)
        * (o.DISCOUNT_PCT / 100) AS DISCOUNT_AMOUNT,

    (o.QTY * o.UNIT_PRICE)
        - ((o.QTY * o.UNIT_PRICE)
        * (o.DISCOUNT_PCT / 100)) AS NET_AMOUNT,

    o.ORDER_DATE

FROM {{ ref('stg_orders') }} o

LEFT JOIN {{ ref('dim_date') }} d
    ON o.ORDER_DATE = d.FULL_DATE

LEFT JOIN {{ ref('dim_customer') }} c
    ON o.CUSTOMER_ID = c.CUSTOMER_ID
    AND o.ORDER_DATE >= CAST(c.EFF_START_TS AS DATE)
    AND o.ORDER_DATE < COALESCE(
        CAST(c.EFF_END_TS AS DATE),
        '9999-12-31'
    )

LEFT JOIN {{ ref('dim_restaurant') }} r
    ON o.RESTAURANT_ID = r.RESTAURANT_ID

LEFT JOIN {{ ref('dim_menu_item') }} m
    ON o.MENU_ITEM_ID = m.MENU_ITEM_ID
    AND o.ORDER_DATE >= CAST(m.EFF_START_TS AS DATE)
    AND o.ORDER_DATE < COALESCE(
        CAST(m.EFF_END_TS AS DATE),
        '9999-12-31'
    )