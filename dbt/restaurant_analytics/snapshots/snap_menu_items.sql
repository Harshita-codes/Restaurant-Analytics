{% snapshot snap_menu_items %}

{{
    config(
        target_schema='DW',
        unique_key='MENU_ITEM_ID',
        strategy='timestamp',
        updated_at='UPDATED_AT'
    )
}}

SELECT
    MENU_ITEM_ID,
    ITEM_NAME,
    ITEM_TYPE,
    CUISINE,
    DIET_TYPE,
    LIST_PRICE,
    STATUS,
    UPDATED_AT

FROM {{ ref('stg_menu_items') }}

{% endsnapshot %}