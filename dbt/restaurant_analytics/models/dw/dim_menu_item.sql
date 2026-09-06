{{ config(
    materialized='table'
) }}

SELECT
    MD5(
        MENU_ITEM_ID || '|' ||
        TO_VARCHAR(DBT_VALID_FROM)
    ) AS MENU_ITEM_KEY,

    MENU_ITEM_ID,
    ITEM_NAME,
    ITEM_TYPE,
    CUISINE,
    DIET_TYPE,
    LIST_PRICE,
    STATUS,

    DBT_VALID_FROM AS EFF_START_TS,
    DBT_VALID_TO AS EFF_END_TS,

    CASE
        WHEN DBT_VALID_TO IS NULL THEN TRUE
        ELSE FALSE
    END AS IS_CURRENT,

    MD5(
        CONCAT_WS(
            '||',
            MENU_ITEM_ID,
            ITEM_NAME,
            ITEM_TYPE,
            CUISINE,
            DIET_TYPE,
            TO_VARCHAR(LIST_PRICE),
            STATUS
        )
    ) AS HASH_DIFF

FROM {{ ref('snap_menu_items') }}