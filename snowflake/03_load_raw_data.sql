--Step-4: Upload CSV Files to Internal stage
--Step-4A: Verify files in Internal stage
LIST @RESTAURANT_STAGE;

--Step-5: Load the CSV Files into RAW layer
-- Load customer data into RAW layer
COPY INTO RAW_CUSTOMERS
(
    CUSTOMER_ID,
    FIRST_NAME,
    LAST_NAME,
    EMAIL,
    PHONE,
    LOYALTY_TIER,
    CITY,
    STATE,
    COUNTRY,
    UPDATED_AT,
    SOURCE_FILE_NAME
)
FROM
(
    SELECT
        $1,
        $2,
        $3,
        $4,
        $5,
        $6,
        $7,
        $8,
        $9,
        TRY_TO_TIMESTAMP_NTZ($10),
        METADATA$FILENAME
    FROM @RESTAURANT_STAGE
)
FILE_FORMAT = (FORMAT_NAME = 'CSV_FORMAT')
PATTERN = '.*restaurant_customers_expanded[.]csv'
ON_ERROR = 'CONTINUE';

SELECT COUNT(*) AS CUSTOMER_COUNT
FROM RAW_CUSTOMERS;

SELECT *
FROM RAW_CUSTOMERS
LIMIT 10;

--LOAD RESTAURANT DATA INTO RAW LAYER
COPY INTO RAW_RESTAURANTS
(
    RESTAURANT_ID,
    RESTAURANT_NAME,
    REGION,
    CITY,
    STATE,
    COUNTRY,
    OPEN_DATE,
    SERVICE_MODES,
    STATUS,
    SOURCE_FILE_NAME
)
FROM
(
    SELECT
        $1,
        $2,
        $3,
        $4,
        $5,
        $6,
        TRY_TO_DATE($7),
        $8,
        $9,
        METADATA$FILENAME
    FROM @RESTAURANT_STAGE
)
FILE_FORMAT = (FORMAT_NAME = 'CSV_FORMAT')
PATTERN = '.*restaurant_locations_expanded[.]csv'
ON_ERROR = 'CONTINUE';

SELECT COUNT(*) AS RESTAURANT_COUNT
FROM RAW_RESTAURANTS;

--LOAD MENU ITEM DATA INTO RAW LAYER
COPY INTO RAW_MENU_ITEMS
(
    MENU_ITEM_ID,
    ITEM_NAME,
    ITEM_TYPE,
    CUISINE,
    DIET_TYPE,
    LIST_PRICE,
    STATUS,
    UPDATED_AT,
    SOURCE_FILE_NAME
)
FROM
(
    SELECT
        $1,
        $2,
        $3,
        $4,
        $5,
        TRY_TO_NUMBER($6, 10, 2),
        $7,
        TRY_TO_TIMESTAMP_NTZ($8),
        METADATA$FILENAME
    FROM @RESTAURANT_STAGE
)
FILE_FORMAT = (FORMAT_NAME = 'CSV_FORMAT')
PATTERN = '.*menu_items_expanded[.]csv'
ON_ERROR = 'CONTINUE';

SELECT COUNT(*) AS MENU_ITEM_COUNT
FROM RAW_MENU_ITEMS;

--LOAD ORDER DATA INTO RAW LAYER
COPY INTO RAW_ORDERS
(
    ORDER_ID,
    ORDER_LINE_ID,
    ORDER_DATE,
    CUSTOMER_ID,
    MENU_ITEM_ID,
    RESTAURANT_ID,
    ORDER_CHANNEL,
    QTY,
    UNIT_PRICE,
    DISCOUNT_PCT,
    PAYMENT_TYPE,
    ORDER_STATUS,
    SOURCE_FILE_NAME
)
FROM
(
    SELECT
        $1,
        $2,
        TRY_TO_DATE($3),
        $4,
        $5,
        $6,
        $7,
        TRY_TO_NUMBER($8),
        TRY_TO_NUMBER($9, 10, 2),
        TRY_TO_NUMBER($10, 5, 2),
        $11,
        $12,
        METADATA$FILENAME
    FROM @RESTAURANT_STAGE
)
FILE_FORMAT = (FORMAT_NAME = 'CSV_FORMAT')
PATTERN = '.*restaurant_orders_expanded[.]csv'
ON_ERROR = 'CONTINUE';

SELECT COUNT(*) AS ORDER_LINE_COUNT
FROM RAW_ORDERS;

SELECT *
FROM RAW_ORDERS
LIMIT 10;
