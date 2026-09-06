{% snapshot snap_customers %}

{{
    config(
        target_schema='DW',
        unique_key='CUSTOMER_ID',
        strategy='timestamp',
        updated_at='UPDATED_AT'
    )
}}

SELECT
    CUSTOMER_ID,
    FIRST_NAME,
    LAST_NAME,
    EMAIL,
    PHONE,
    LOYALTY_TIER,
    CITY,
    STATE,
    COUNTRY,
    UPDATED_AT

FROM {{ ref('stg_customers') }}

{% endsnapshot %}