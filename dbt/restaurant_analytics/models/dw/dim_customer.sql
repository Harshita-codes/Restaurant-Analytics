{{ config(
    materialized='table'
) }}

SELECT
    MD5(
        CUSTOMER_ID || '|' ||
        TO_VARCHAR(DBT_VALID_FROM)
    ) AS CUSTOMER_KEY,

    CUSTOMER_ID,
    FIRST_NAME,
    LAST_NAME,
    EMAIL,
    PHONE,
    LOYALTY_TIER,
    CITY,
    STATE,
    COUNTRY,

    DBT_VALID_FROM AS EFF_START_TS,
    DBT_VALID_TO AS EFF_END_TS,

    CASE
        WHEN DBT_VALID_TO IS NULL THEN TRUE
        ELSE FALSE
    END AS IS_CURRENT,

    MD5(
        CONCAT_WS(
            '||',
            CUSTOMER_ID,
            FIRST_NAME,
            LAST_NAME,
            EMAIL,
            PHONE,
            LOYALTY_TIER,
            CITY,
            STATE,
            COUNTRY
        )
    ) AS HASH_DIFF

FROM {{ ref('snap_customers') }}