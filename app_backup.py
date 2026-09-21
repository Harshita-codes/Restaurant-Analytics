import streamlit as st
import snowflake.connector
import pandas as pd
import altair as alt


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Restaurant Analytics",
    page_icon="🍽️",
    layout="wide"
)


# ============================================================
# SNOWFLAKE CONNECTION
# ============================================================

def get_connection():
    return snowflake.connector.connect(
        account=st.secrets["snowflake"]["account"],
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"],
        role=st.secrets["snowflake"]["role"]
    )


def run_query(query):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query)

        columns = [column[0] for column in cursor.description]
        data = cursor.fetchall()

        return pd.DataFrame(data, columns=columns)

    finally:
        cursor.close()
        conn.close()


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    revenue_df = run_query("""
        SELECT *
        FROM V_REVENUE_DAILY
        ORDER BY FULL_DATE
    """)

    menu_df = run_query("""
        SELECT *
        FROM V_ITEM_PERFORMANCE
    """)

    restaurant_df = run_query("""
        SELECT *
        FROM V_RESTAURANT_PERFORMANCE
    """)

    channel_df = run_query("""
        SELECT *
        FROM V_CHANNEL_PERFORMANCE
    """)

    cuisine_df = run_query("""
        SELECT *
        FROM V_CUISINE_PERFORMANCE
    """)

    return (
        revenue_df,
        menu_df,
        restaurant_df,
        channel_df,
        cuisine_df
    )


revenue_df, menu_df, restaurant_df, channel_df, cuisine_df = load_data()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🍽️ Restaurant Analytics")

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    [
        "Executive Summary",
        "Menu Performance",
        "Restaurant Performance",
        "Explorer"
    ]
)


# ============================================================
# EXECUTIVE SUMMARY
# ============================================================

if page == "Executive Summary":

    st.title("🍽️ Restaurant Analytics")
    st.caption("Executive Summary | Snowflake + dbt + Streamlit")

    # --------------------------------------------------------
    # DATE FILTER
    # --------------------------------------------------------

    st.sidebar.markdown("---")
    st.sidebar.header("📅 Date Filter")

    revenue_df["FULL_DATE"] = pd.to_datetime(
        revenue_df["FULL_DATE"]
    )

    min_date = revenue_df["FULL_DATE"].min()
    max_date = revenue_df["FULL_DATE"].max()

    start_date = st.sidebar.date_input(
        "Start Date",
        value=min_date.date(),
        min_value=min_date.date(),
        max_value=max_date.date()
    )

    end_date = st.sidebar.date_input(
        "End Date",
        value=max_date.date(),
        min_value=min_date.date(),
        max_value=max_date.date()
    )

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    filtered = revenue_df[
        (revenue_df["FULL_DATE"] >= start_date)
        & (revenue_df["FULL_DATE"] <= end_date)
    ].copy()

    # --------------------------------------------------------
    # KPI CALCULATIONS
    # --------------------------------------------------------

    gross_revenue = filtered["GROSS_REVENUE"].sum()
    net_revenue = filtered["NET_REVENUE"].sum()
    discount_amount = filtered["DISCOUNT_AMOUNT"].sum()
    total_orders = filtered["TOTAL_ORDERS"].sum()
    total_quantity = filtered["TOTAL_QTY"].sum()

    average_order_value = (
        net_revenue / total_orders
        if total_orders > 0
        else 0
    )

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    st.subheader("📊 Executive Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Gross Revenue",
        f"₹{gross_revenue:,.2f}"
    )

    col2.metric(
        "Net Revenue",
        f"₹{net_revenue:,.2f}"
    )

    col3.metric(
        "Total Orders",
        f"{total_orders:,.0f}"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Quantity",
        f"{total_quantity:,.0f}"
    )

    col2.metric(
        "Average Order Value",
        f"₹{average_order_value:,.2f}"
    )

    col3.metric(
        "Discount Amount",
        f"₹{discount_amount:,.2f}"
    )

    st.markdown("---")

    # ========================================================
    # MONTHLY NET REVENUE
    # ========================================================

    st.subheader("📈 Monthly Net Revenue Trend")

    monthly = (
        filtered
        .groupby(
            ["YEAR", "MONTH", "MONTH_NAME"],
            as_index=False
        )["NET_REVENUE"]
        .sum()
    )

    monthly["MONTH_LABEL"] = (
        monthly["MONTH_NAME"]
        + " "
        + monthly["YEAR"].astype(str)
    )

    monthly = monthly.sort_values(
        ["YEAR", "MONTH"]
    )

    monthly_chart = alt.Chart(monthly).mark_bar().encode(

        x=alt.X(
            "MONTH_LABEL:N",
            sort=monthly["MONTH_LABEL"].tolist(),
            title="Month",
            axis=alt.Axis(labelAngle=0)
        ),

        y=alt.Y(
            "NET_REVENUE:Q",
            title="Net Revenue (₹)",
            axis=alt.Axis(format=",.0f")
        ),

        tooltip=[
            alt.Tooltip(
                "MONTH_LABEL:N",
                title="Month"
            ),
            alt.Tooltip(
                "NET_REVENUE:Q",
                title="Net Revenue",
                format=",.2f"
            )
        ]
    ).properties(
        height=350
    )

    st.altair_chart(
        monthly_chart,
        use_container_width=True
    )

    st.markdown("---")

    # ========================================================
    # TOP RESTAURANTS + MENU ITEMS
    # ========================================================

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # TOP RESTAURANTS
    # --------------------------------------------------------

    with col1:

        st.subheader("🏆 Top 5 Restaurants by Revenue")

        top_restaurants = (
            restaurant_df
            .sort_values(
                "NET_REVENUE",
                ascending=False
            )
            .head(5)
            .copy()
        )

        top_restaurants = top_restaurants.sort_values(
            "NET_REVENUE"
        )

        restaurant_chart = alt.Chart(
            top_restaurants
        ).mark_bar().encode(

            x=alt.X(
                "NET_REVENUE:Q",
                title="Net Revenue (₹)",
                axis=alt.Axis(format=",.0f")
            ),

            y=alt.Y(
                "RESTAURANT_NAME:N",
                sort=None,
                title=None
            ),

            tooltip=[
                alt.Tooltip(
                    "RESTAURANT_NAME:N",
                    title="Restaurant"
                ),
                alt.Tooltip(
                    "NET_REVENUE:Q",
                    title="Net Revenue",
                    format=",.2f"
                ),
                alt.Tooltip(
                    "TOTAL_ORDERS:Q",
                    title="Orders",
                    format=",.0f"
                )
            ]
        ).properties(
            height=300
        )

        st.altair_chart(
            restaurant_chart,
            use_container_width=True
        )

    # --------------------------------------------------------
    # TOP MENU ITEMS
    # --------------------------------------------------------

    with col2:

        st.subheader("🍔 Top 5 Menu Items by Revenue")

        top_items = (
            menu_df
            .sort_values(
                "NET_REVENUE",
                ascending=False
            )
            .head(5)
            .copy()
        )

        top_items = top_items.sort_values(
            "NET_REVENUE"
        )

        item_chart = alt.Chart(
            top_items
        ).mark_bar().encode(

            x=alt.X(
                "NET_REVENUE:Q",
                title="Net Revenue (₹)",
                axis=alt.Axis(format=",.0f")
            ),

            y=alt.Y(
                "ITEM_NAME:N",
                sort=None,
                title=None
            ),

            tooltip=[
                alt.Tooltip(
                    "ITEM_NAME:N",
                    title="Menu Item"
                ),
                alt.Tooltip(
                    "NET_REVENUE:Q",
                    title="Net Revenue",
                    format=",.2f"
                ),
                alt.Tooltip(
                    "TOTAL_QTY:Q",
                    title="Quantity",
                    format=",.0f"
                )
            ]
        ).properties(
            height=300
        )

        st.altair_chart(
            item_chart,
            use_container_width=True
        )

    st.markdown("---")

    # ========================================================
    # CHANNEL + CUISINE
    # ========================================================

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # CHANNEL
    # --------------------------------------------------------

    with col1:

        st.subheader("📊 Revenue by Order Channel")

        channel_chart = alt.Chart(
            channel_df
        ).mark_bar().encode(

            x=alt.X(
                "NET_REVENUE:Q",
                title="Net Revenue (₹)",
                axis=alt.Axis(format=",.0f")
            ),

            y=alt.Y(
                "ORDER_CHANNEL:N",
                sort="-x",
                title=None
            ),

            tooltip=[
                alt.Tooltip(
                    "ORDER_CHANNEL:N",
                    title="Channel"
                ),
                alt.Tooltip(
                    "NET_REVENUE:Q",
                    title="Net Revenue",
                    format=",.2f"
                ),
                alt.Tooltip(
                    "TOTAL_ORDERS:Q",
                    title="Orders",
                    format=",.0f"
                )
            ]
        ).properties(
            height=300
        )

        st.altair_chart(
            channel_chart,
            use_container_width=True
        )

    # --------------------------------------------------------
    # CUISINE
    # --------------------------------------------------------

    with col2:

        st.subheader("🍛 Revenue by Cuisine")

        cuisine_chart = alt.Chart(
            cuisine_df
        ).mark_bar().encode(

            x=alt.X(
                "NET_REVENUE:Q",
                title="Net Revenue (₹)",
                axis=alt.Axis(format=",.0f")
            ),

            y=alt.Y(
                "CUISINE:N",
                sort="-x",
                title=None
            ),

            tooltip=[
                alt.Tooltip(
                    "CUISINE:N",
                    title="Cuisine"
                ),
                alt.Tooltip(
                    "NET_REVENUE:Q",
                    title="Net Revenue",
                    format=",.2f"
                ),
                alt.Tooltip(
                    "TOTAL_QTY:Q",
                    title="Quantity",
                    format=",.0f"
                )
            ]
        ).properties(
            height=300
        )

        st.altair_chart(
            cuisine_chart,
            use_container_width=True
        )


# ============================================================
# MENU PERFORMANCE
# ============================================================

elif page == "Menu Performance":

    st.title("🍔 Menu Performance")

    st.caption(
        "Menu item analysis from V_ITEM_PERFORMANCE"
    )

    # --------------------------------------------------------
    # FILTERS
    # --------------------------------------------------------

    st.sidebar.markdown("---")
    st.sidebar.header("🔎 Menu Filters")

    item_types = sorted(
        menu_df["ITEM_TYPE"]
        .dropna()
        .unique()
    )

    cuisines = sorted(
        menu_df["CUISINE"]
        .dropna()
        .unique()
    )

    diet_types = sorted(
        menu_df["DIET_TYPE"]
        .dropna()
        .unique()
    )

    selected_item_type = st.sidebar.multiselect(
        "Item Type",
        item_types
    )

    selected_cuisine = st.sidebar.multiselect(
        "Cuisine",
        cuisines
    )

    selected_diet = st.sidebar.multiselect(
        "Diet Type",
        diet_types
    )

    filtered_menu = menu_df.copy()

    if selected_item_type:
        filtered_menu = filtered_menu[
            filtered_menu["ITEM_TYPE"].isin(
                selected_item_type
            )
        ]

    if selected_cuisine:
        filtered_menu = filtered_menu[
            filtered_menu["CUISINE"].isin(
                selected_cuisine
            )
        ]

    if selected_diet:
        filtered_menu = filtered_menu[
            filtered_menu["DIET_TYPE"].isin(
                selected_diet
            )
        ]

    # --------------------------------------------------------
    # KPIs
    # --------------------------------------------------------

    total_qty = filtered_menu["TOTAL_QTY"].sum()
    total_orders = filtered_menu["TOTAL_ORDERS"].sum()
    net_revenue = filtered_menu["NET_REVENUE"].sum()

    avg_unit_price = (
        filtered_menu["AVG_UNIT_PRICE"].mean()
        if len(filtered_menu) > 0
        else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Quantity",
        f"{total_qty:,.0f}"
    )

    col2.metric(
        "Total Orders",
        f"{total_orders:,.0f}"
    )

    col3.metric(
        "Net Revenue",
        f"₹{net_revenue:,.2f}"
    )

    col4.metric(
        "Avg Unit Price",
        f"₹{avg_unit_price:,.2f}"
    )

    st.markdown("---")

    # ========================================================
    # TOP ITEMS
    # ========================================================

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🏆 Top 10 Menu Items by Revenue")

        top_items = (
            filtered_menu
            .sort_values(
                "NET_REVENUE",
                ascending=False
            )
            .head(10)
            .copy()
        )

        top_items = top_items.sort_values(
            "NET_REVENUE"
        )

        chart = alt.Chart(
            top_items
        ).mark_bar().encode(

            x=alt.X(
                "NET_REVENUE:Q",
                title="Net Revenue (₹)",
                axis=alt.Axis(format=",.0f")
            ),

            y=alt.Y(
                "ITEM_NAME:N",
                sort=None,
                title=None
            ),

            tooltip=[
                alt.Tooltip(
                    "ITEM_NAME:N",
                    title="Menu Item"
                ),
                alt.Tooltip(
                    "NET_REVENUE:Q",
                    title="Revenue",
                    format=",.2f"
                ),
                alt.Tooltip(
                    "TOTAL_QTY:Q",
                    title="Quantity",
                    format=",.0f"
                )
            ]
        ).properties(
            height=400
        )

        st.altair_chart(
            chart,
            use_container_width=True
        )

    with col2:

        st.subheader("📦 Top 10 Menu Items by Quantity")

        top_quantity = (
            filtered_menu
            .sort_values(
                "TOTAL_QTY",
                ascending=False
            )
            .head(10)
            .copy()
        )

        top_quantity = top_quantity.sort_values(
            "TOTAL_QTY"
        )

        chart = alt.Chart(
            top_quantity
        ).mark_bar().encode(

            x=alt.X(
                "TOTAL_QTY:Q",
                title="Quantity Sold",
                axis=alt.Axis(format=",.0f")
            ),

            y=alt.Y(
                "ITEM_NAME:N",
                sort=None,
                title=None
            ),

            tooltip=[
                alt.Tooltip(
                    "ITEM_NAME:N",
                    title="Menu Item"
                ),
                alt.Tooltip(
                    "TOTAL_QTY:Q",
                    title="Quantity",
                    format=",.0f"
                ),
                alt.Tooltip(
                    "NET_REVENUE:Q",
                    title="Revenue",
                    format=",.2f"
                )
            ]
        ).properties(
            height=400
        )

        st.altair_chart(
            chart,
            use_container_width=True
        )

    st.markdown("---")

    # ========================================================
    # CUISINE
    # ========================================================

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🍛 Revenue by Cuisine")

        cuisine_summary = (
            filtered_menu
            .groupby(
                "CUISINE",
                as_index=False
            )["NET_REVENUE"]
            .sum()
            .sort_values(
                "NET_REVENUE",
                ascending=False
            )
        )

        cuisine_summary = cuisine_summary.sort_values(
            "NET_REVENUE"
        )

        chart = alt.Chart(
            cuisine_summary
        ).mark_bar().encode(

            x=alt.X(
                "NET_REVENUE:Q",
                title="Net Revenue (₹)",
                axis=alt.Axis(format=",.0f")
            ),

            y=alt.Y(
                "CUISINE:N",
                sort=None,
                title=None
            ),

            tooltip=[
                alt.Tooltip(
                    "CUISINE:N",
                    title="Cuisine"
                ),
                alt.Tooltip(
                    "NET_REVENUE:Q",
                    title="Revenue",
                    format=",.2f"
                )
            ]
        ).properties(
            height=350
        )

        st.altair_chart(
            chart,
            use_container_width=True
        )

    with col2:

        st.subheader("📦 Quantity Sold by Cuisine")

        quantity_summary = (
            filtered_menu
            .groupby(
                "CUISINE",
                as_index=False
            )["TOTAL_QTY"]
            .sum()
            .sort_values(
                "TOTAL_QTY",
                ascending=False
            )
        )

        quantity_summary = quantity_summary.sort_values(
            "TOTAL_QTY"
        )

        chart = alt.Chart(
            quantity_summary
        ).mark_bar().encode(

            x=alt.X(
                "TOTAL_QTY:Q",
                title="Quantity Sold",
                axis=alt.Axis(format=",.0f")
            ),

            y=alt.Y(
                "CUISINE:N",
                sort=None,
                title=None
            ),

            tooltip=[
                alt.Tooltip(
                    "CUISINE:N",
                    title="Cuisine"
                ),
                alt.Tooltip(
                    "TOTAL_QTY:Q",
                    title="Quantity",
                    format=",.0f"
                )
            ]
        ).properties(
            height=350
        )

        st.altair_chart(
            chart,
            use_container_width=True
        )

    st.markdown("---")

    # ========================================================
    # MENU TABLE
    # ========================================================

    st.subheader("📋 Menu Item Details")

    st.dataframe(
        filtered_menu.sort_values(
            "NET_REVENUE",
            ascending=False
        ),
        use_container_width=True
    )


# ============================================================
# RESTAURANT PERFORMANCE
# ============================================================

elif page == "Restaurant Performance":

    st.title("🏪 Restaurant Performance")

    st.caption(
        "Restaurant analysis from V_RESTAURANT_PERFORMANCE"
    )

    # --------------------------------------------------------
    # FILTERS
    # --------------------------------------------------------

    st.sidebar.markdown("---")
    st.sidebar.header("🔎 Restaurant Filters")

    regions = sorted(
        restaurant_df["REGION"]
        .dropna()
        .unique()
    )

    cities = sorted(
        restaurant_df["CITY"]
        .dropna()
        .unique()
    )

    statuses = sorted(
        restaurant_df["STATUS"]
        .dropna()
        .unique()
    )

    selected_region = st.sidebar.multiselect(
        "Region",
        regions
    )

    selected_city = st.sidebar.multiselect(
        "City",
        cities
    )

    selected_status = st.sidebar.multiselect(
        "Status",
        statuses
    )

    filtered_restaurants = restaurant_df.copy()

    if selected_region:
        filtered_restaurants = filtered_restaurants[
            filtered_restaurants["REGION"].isin(
                selected_region
            )
        ]

    if selected_city:
        filtered_restaurants = filtered_restaurants[
            filtered_restaurants["CITY"].isin(
                selected_city
            )
        ]

    if selected_status:
        filtered_restaurants = filtered_restaurants[
            filtered_restaurants["STATUS"].isin(
                selected_status
            )
        ]

    # --------------------------------------------------------
    # KPIs
    # --------------------------------------------------------

    total_orders = filtered_restaurants["TOTAL_ORDERS"].sum()
    total_qty = filtered_restaurants["TOTAL_QTY"].sum()
    net_revenue = filtered_restaurants["NET_REVENUE"].sum()

    aov = (
        net_revenue / total_orders
        if total_orders > 0
        else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Orders",
        f"{total_orders:,.0f}"
    )

    col2.metric(
        "Total Quantity",
        f"{total_qty:,.0f}"
    )

    col3.metric(
        "Net Revenue",
        f"₹{net_revenue:,.2f}"
    )

    col4.metric(
        "Average Order Value",
        f"₹{aov:,.2f}"
    )

    st.markdown("---")

    # ========================================================
    # TOP RESTAURANTS
    # ========================================================

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🏆 Top 10 Restaurants by Revenue")

        top_restaurants = (
            filtered_restaurants
            .sort_values(
                "NET_REVENUE",
                ascending=False
            )
            .head(10)
            .copy()
        )

        top_restaurants = top_restaurants.sort_values(
            "NET_REVENUE"
        )

        chart = alt.Chart(
            top_restaurants
        ).mark_bar().encode(

            x=alt.X(
                "NET_REVENUE:Q",
                title="Net Revenue (₹)",
                axis=alt.Axis(format=",.0f")
            ),

            y=alt.Y(
                "RESTAURANT_NAME:N",
                sort=None,
                title=None
            ),

            tooltip=[
                alt.Tooltip(
                    "RESTAURANT_NAME:N",
                    title="Restaurant"
                ),
                alt.Tooltip(
                    "NET_REVENUE:Q",
                    title="Revenue",
                    format=",.2f"
                ),
                alt.Tooltip(
                    "TOTAL_ORDERS:Q",
                    title="Orders",
                    format=",.0f"
                )
            ]
        ).properties(
            height=450
        )

        st.altair_chart(
            chart,
            use_container_width=True
        )

    with col2:

        st.subheader("📦 Top 10 Restaurants by Orders")

        top_orders = (
            filtered_restaurants
            .sort_values(
                "TOTAL_ORDERS",
                ascending=False
            )
            .head(10)
            .copy()
        )

        top_orders = top_orders.sort_values(
            "TOTAL_ORDERS"
        )

        chart = alt.Chart(
            top_orders
        ).mark_bar().encode(

            x=alt.X(
                "TOTAL_ORDERS:Q",
                title="Orders",
                axis=alt.Axis(format=",.0f")
            ),

            y=alt.Y(
                "RESTAURANT_NAME:N",
                sort=None,
                title=None
            ),

            tooltip=[
                alt.Tooltip(
                    "RESTAURANT_NAME:N",
                    title="Restaurant"
                ),
                alt.Tooltip(
                    "TOTAL_ORDERS:Q",
                    title="Orders",
                    format=",.0f"
                ),
                alt.Tooltip(
                    "NET_REVENUE:Q",
                    title="Revenue",
                    format=",.2f"
                )
            ]
        ).properties(
            height=450
        )

        st.altair_chart(
            chart,
            use_container_width=True
        )

    st.markdown("---")

    # ========================================================
    # REGION + CITY
    # ========================================================

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🌎 Revenue by Region")

        region_summary = (
            filtered_restaurants
            .groupby(
                "REGION",
                as_index=False
            )["NET_REVENUE"]
            .sum()
            .sort_values(
                "NET_REVENUE",
                ascending=False
            )
        )

        region_summary = region_summary.sort_values(
            "NET_REVENUE"
        )

        chart = alt.Chart(
            region_summary
        ).mark_bar().encode(

            x=alt.X(
                "NET_REVENUE:Q",
                title="Net Revenue (₹)",
                axis=alt.Axis(format=",.0f")
            ),

            y=alt.Y(
                "REGION:N",
                sort=None,
                title=None
            ),

            tooltip=[
                alt.Tooltip(
                    "REGION:N",
                    title="Region"
                ),
                alt.Tooltip(
                    "NET_REVENUE:Q",
                    title="Revenue",
                    format=",.2f"
                )
            ]
        ).properties(
            height=350
        )

        st.altair_chart(
            chart,
            use_container_width=True
        )

    with col2:

        st.subheader("🏙️ Revenue by City")

        city_summary = (
            filtered_restaurants
            .groupby(
                "CITY",
                as_index=False
            )["NET_REVENUE"]
            .sum()
            .sort_values(
                "NET_REVENUE",
                ascending=False
            )
        )

        city_summary = city_summary.sort_values(
            "NET_REVENUE"
        )

        chart = alt.Chart(
            city_summary
        ).mark_bar().encode(

            x=alt.X(
                "NET_REVENUE:Q",
                title="Net Revenue (₹)",
                axis=alt.Axis(format=",.0f")
            ),

            y=alt.Y(
                "CITY:N",
                sort=None,
                title=None
            ),

            tooltip=[
                alt.Tooltip(
                    "CITY:N",
                    title="City"
                ),
                alt.Tooltip(
                    "NET_REVENUE:Q",
                    title="Revenue",
                    format=",.2f"
                )
            ]
        ).properties(
            height=350
        )

        st.altair_chart(
            chart,
            use_container_width=True
        )

    st.markdown("---")

    # ========================================================
    # RESTAURANT TABLE
    # ========================================================

    st.subheader("📋 Restaurant Details")

    st.dataframe(
        filtered_restaurants.sort_values(
            "NET_REVENUE",
            ascending=False
        ),
        use_container_width=True
    )


# ============================================================
# EXPLORER
# ============================================================

elif page == "Explorer":

    st.title("🔎 Explorer")

    st.caption(
        "Explore analytics data from Snowflake semantic views"
    )

    dataset = st.selectbox(
        "Select Dataset",
        [
            "Revenue",
            "Menu Performance",
            "Restaurant Performance",
            "Channel Performance",
            "Cuisine Performance"
        ]
    )

    if dataset == "Revenue":

        st.subheader("📈 Daily Revenue")

        st.dataframe(
            revenue_df,
            use_container_width=True
        )

    elif dataset == "Menu Performance":

        st.subheader("🍔 Menu Performance")

        st.dataframe(
            menu_df,
            use_container_width=True
        )

    elif dataset == "Restaurant Performance":

        st.subheader("🏪 Restaurant Performance")

        st.dataframe(
            restaurant_df,
            use_container_width=True
        )

    elif dataset == "Channel Performance":

        st.subheader("📊 Channel Performance")

        st.dataframe(
            channel_df,
            use_container_width=True
        )

    else:

        st.subheader("🍛 Cuisine Performance")

        st.dataframe(
            cuisine_df,
            use_container_width=True
        )