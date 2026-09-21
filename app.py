import streamlit as st
import snowflake.connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# PAGE
# ============================================================
st.set_page_config(
    page_title="Restaurant Analytics",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# GLOBAL CSS — spacious but still dashboard-friendly
# ============================================================
st.markdown(
    """
    <style>
    #MainMenu, header, footer {visibility: hidden;}
    .stApp {background: #f5f8fc;}
    .block-container {
        max-width: 100% !important;
        padding: 0.45rem 0.65rem 0.35rem 0.65rem !important;
    }
    div[data-testid="stHorizontalBlock"] {gap: 0.70rem !important;}
    div[data-testid="stVerticalBlock"] {gap: 0.62rem !important;}

    /* Header */
    .top-header {
        background: linear-gradient(90deg, #173b5d, #245b86);
        border-radius: 9px;
        padding: 0.48rem 0.80rem 0.52rem 0.80rem;
        margin-bottom: 0.45rem;
        color: white;
        min-height: 58px;
    }
    .title {
        font-size: 1.42rem;
        font-weight: 800;
        line-height: 1.15;
        margin: 0;
    }
    .subtitle {
        font-size: 0.66rem;
        margin-top: 0.18rem;
        color: #dceaf7;
        line-height: 1.25;
    }

    /* Filter controls */
    div[data-testid="stSelectbox"] label,
    div[data-testid="stDateInput"] label {
        color: #244565 !important;
        font-size: 0.67rem !important;
        font-weight: 750 !important;
        margin-bottom: 0.10rem !important;
    }
    div[data-baseweb="select"] {
        border: 1px solid #d2deeb !important;
        border-radius: 7px !important;
        background: white !important;
        min-height: 36px !important;
    }
    div[data-testid="stDateInput"] input {
        border: 1px solid #d2deeb !important;
        border-radius: 7px !important;
        background: white !important;
        min-height: 36px !important;
        font-size: 0.70rem !important;
    }

    /* KPI cards */
    .kpi {
        background: white;
        border: 1px solid #d7e3ef;
        border-radius: 9px;
        padding: 0.48rem 0.62rem;
        min-height: 67px;
        box-shadow: 0 1px 4px rgba(25,55,85,.06);
    }
    .kpi-label {
        color: #63778b;
        font-size: 0.62rem;
        font-weight: 750;
        text-transform: uppercase;
        white-space: nowrap;
    }
    .kpi-value {
        color: #173a5b;
        font-size: 1.08rem;
        font-weight: 800;
        line-height: 1.25;
        margin-top: 0.12rem;
        white-space: nowrap;
    }

    /* Streamlit bordered containers used as chart cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff !important;
        border: 1px solid #d8e4ef !important;
        border-radius: 9px !important;
        box-shadow: 0 1px 4px rgba(25,55,85,.05);
        padding: 0.10rem 0.35rem 0.18rem 0.35rem !important;
    }
    .card-title {
        color: #173a5b;
        font-size: 0.78rem;
        font-weight: 800;
        margin: 0.05rem 0 0.03rem 0.12rem;
        line-height: 1.2;
    }
    .card-subtitle {
        color: #72869a;
        font-size: 0.58rem;
        margin: 0 0 0.05rem 0.12rem;
        line-height: 1.15;
    }

    /* Explorer */
    .explorer-title {
        color: #173a5b;
        font-size: 0.78rem;
        font-weight: 800;
        margin: 0.05rem 0 0.10rem 0.10rem;
        line-height: 1.2;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid #d8e4ef;
        border-radius: 8px;
        overflow: hidden;
    }
    div[data-testid="stDownloadButton"] button {
        background: white !important;
        color: #173a5b !important;
        border: 1px solid #cbd9e7 !important;
        border-radius: 7px !important;
        font-size: 0.67rem !important;
        font-weight: 700 !important;
        padding: 0.25rem 0.55rem !important;
    }
    .footer-note {
        color: #73879b;
        font-size: 0.56rem;
        margin-top: 0.18rem;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# SNOWFLAKE
# ============================================================
@st.cache_resource
def get_connection():
    return snowflake.connector.connect(
        account=st.secrets["snowflake"]["account"],
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"],
        role=st.secrets["snowflake"]["role"],
    )


@st.cache_data(ttl=600)
def load_data():
    query = """
    SELECT
        f.ORDER_ID,
        f.ORDER_LINE_ID,
        d.FULL_DATE,
        d.MONTH_NAME,
        d.QUARTER,
        d.YEAR,
        r.RESTAURANT_ID,
        r.RESTAURANT_NAME,
        r.REGION,
        r.CITY,
        r.STATE,
        m.MENU_ITEM_ID,
        m.ITEM_NAME,
        m.ITEM_TYPE,
        m.CUISINE,
        m.DIET_TYPE,
        c.CUSTOMER_ID,
        c.LOYALTY_TIER,
        f.ORDER_CHANNEL,
        f.QTY,
        f.UNIT_PRICE,
        f.DISCOUNT_PCT,
        f.GROSS_AMOUNT,
        f.DISCOUNT_AMOUNT,
        f.NET_AMOUNT
    FROM RESTAURANT_ANALYTICS.DW.FACT_ORDERS f
    JOIN RESTAURANT_ANALYTICS.DW.DIM_DATE d
      ON f.DATE_KEY = d.DATE_KEY
    JOIN RESTAURANT_ANALYTICS.DW.DIM_RESTAURANT r
      ON f.RESTAURANT_KEY = r.RESTAURANT_KEY
    JOIN RESTAURANT_ANALYTICS.DW.DIM_MENU_ITEM m
      ON f.MENU_ITEM_KEY = m.MENU_ITEM_KEY
    JOIN RESTAURANT_ANALYTICS.DW.DIM_CUSTOMER c
      ON f.CUSTOMER_KEY = c.CUSTOMER_KEY
    """
    cur = get_connection().cursor()
    try:
        cur.execute(query)
        data = pd.DataFrame(cur.fetchall(), columns=[c[0] for c in cur.description])
    finally:
        cur.close()

    data["FULL_DATE"] = pd.to_datetime(data["FULL_DATE"], errors="coerce").dt.normalize()
    for col in [
        "QTY", "UNIT_PRICE", "DISCOUNT_PCT",
        "GROSS_AMOUNT", "DISCOUNT_AMOUNT", "NET_AMOUNT"
    ]:
        data[col] = pd.to_numeric(data[col], errors="coerce").astype(float)

    data["DAY_OF_WEEK"] = data["FULL_DATE"].dt.day_name()
    return data


df = load_data()

# ============================================================
# HEADER
# ============================================================
st.markdown(
    """
    <div class="top-header">
        <div class="title">🍽️ Restaurant Analytics</div>
        <div class="subtitle">Business Intelligence Dashboard • Revenue • Menu • Restaurant • Cuisine • Region • Channel • Loyalty</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# FILTER HELPERS
# ============================================================
min_date = df["FULL_DATE"].min().date()
max_date = df["FULL_DATE"].max().date()


def filtered_for_options(data, selected, exclude):
    """Apply every current filter except the filter whose options are being built."""
    y = data[data["FULL_DATE"].between(
        pd.Timestamp(selected["start"]).normalize(),
        pd.Timestamp(selected["end"]).normalize(),
        inclusive="both",
    )].copy()
    for key, column in [
        ("region", "REGION"),
        ("restaurant", "RESTAURANT_NAME"),
        ("cuisine", "CUISINE"),
        ("loyalty", "LOYALTY_TIER"),
        ("channel", "ORDER_CHANNEL"),
    ]:
        if key != exclude and selected[key] != "All":
            y = y[y[column].astype(str) == selected[key]]
    return y


def safe_options(series):
    vals = sorted(series.dropna().astype(str).unique().tolist())
    return ["All"] + vals

# ============================================================
# FILTERS — cascading so incompatible combinations are avoided
# ============================================================
f1, f2, f3, f4, f5, f6 = st.columns([1.28, 1.00, 1.45, 1.05, 0.95, 1.00])

with f1:
    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="date_range",
    )

# Streamlit returns either a 2-date tuple/list or a single date.
# Normalize both ends so changing the date range never creates a
# timestamp mismatch with the warehouse date dimension.
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start = pd.Timestamp(date_range[0]).normalize()
    end = pd.Timestamp(date_range[1]).normalize()
elif isinstance(date_range, (tuple, list)) and len(date_range) == 1:
    start = end = pd.Timestamp(date_range[0]).normalize()
else:
    start = end = pd.Timestamp(date_range).normalize()

if start > end:
    start, end = end, start

# Use session state so a filter that becomes unavailable is safely reset to All.
for key in ["region", "restaurant", "cuisine", "loyalty", "channel"]:
    if key not in st.session_state:
        st.session_state[key] = "All"

selected = {
    "start": start,
    "end": end,
    "region": st.session_state["region"],
    "restaurant": st.session_state["restaurant"],
    "cuisine": st.session_state["cuisine"],
    "loyalty": st.session_state["loyalty"],
    "channel": st.session_state["channel"],
}

with f2:
    opts = safe_options(filtered_for_options(df, selected, "region")["REGION"])
    if selected["region"] not in opts:
        selected["region"] = "All"
    region = st.selectbox("Region", opts, index=opts.index(selected["region"]), key="region")

selected["region"] = region

with f3:
    opts = safe_options(filtered_for_options(df, selected, "restaurant")["RESTAURANT_NAME"])
    if selected["restaurant"] not in opts:
        selected["restaurant"] = "All"
        st.session_state["restaurant"] = "All"
    restaurant = st.selectbox("Restaurant", opts, index=opts.index(selected["restaurant"]), key="restaurant")

selected["restaurant"] = restaurant

with f4:
    opts = safe_options(filtered_for_options(df, selected, "cuisine")["CUISINE"])
    if selected["cuisine"] not in opts:
        selected["cuisine"] = "All"
        st.session_state["cuisine"] = "All"
    cuisine = st.selectbox("Cuisine", opts, index=opts.index(selected["cuisine"]), key="cuisine")

selected["cuisine"] = cuisine

with f5:
    opts = safe_options(filtered_for_options(df, selected, "loyalty")["LOYALTY_TIER"])
    if selected["loyalty"] not in opts:
        selected["loyalty"] = "All"
        st.session_state["loyalty"] = "All"
    loyalty = st.selectbox("Loyalty Tier", opts, index=opts.index(selected["loyalty"]), key="loyalty")

selected["loyalty"] = loyalty

with f6:
    opts = safe_options(filtered_for_options(df, selected, "channel")["ORDER_CHANNEL"])
    if selected["channel"] not in opts:
        selected["channel"] = "All"
        st.session_state["channel"] = "All"
    channel = st.selectbox("Channel", opts, index=opts.index(selected["channel"]), key="channel")

selected["channel"] = channel

# Final dashboard dataset.
x = df[df["FULL_DATE"].between(start, end, inclusive="both")].copy()
if region != "All":
    x = x[x["REGION"].astype(str) == region]
if restaurant != "All":
    x = x[x["RESTAURANT_NAME"].astype(str) == restaurant]
if cuisine != "All":
    x = x[x["CUISINE"].astype(str) == cuisine]
if loyalty != "All":
    x = x[x["LOYALTY_TIER"].astype(str) == loyalty]
if channel != "All":
    x = x[x["ORDER_CHANNEL"].astype(str) == channel]

# ============================================================
# KPIs
# ============================================================
revenue = float(x["NET_AMOUNT"].sum())
gross = float(x["GROSS_AMOUNT"].sum())
discount = float(x["DISCOUNT_AMOUNT"].sum())
orders = int(x["ORDER_ID"].nunique())
qty = int(x["QTY"].sum())
aov = revenue / orders if orders else 0.0

kpis = [
    ("Net Revenue", f"₹{revenue:,.2f}"),
    ("Gross Revenue", f"₹{gross:,.2f}"),
    ("Total Orders", f"{orders:,}"),
    ("Total Quantity", f"{qty:,}"),
    ("AOV (Avg. Order Value)", f"₹{aov:,.2f}"),
    ("Discount Amount", f"₹{discount:,.2f}"),
]

kc = st.columns(6)
for col, (label, value) in zip(kc, kpis):
    with col:
        st.markdown(
            f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>',
            unsafe_allow_html=True,
        )

# ============================================================
# PLOTLY HELPERS
# ============================================================
PLOT = {
    "displayModeBar": False,
    "responsive": True,
    "scrollZoom": False,
}


def style_fig(fig, height=190, legend=False, title=None):
    # Put the chart heading INSIDE the Plotly canvas.
    # This avoids Streamlit/Plotly title overlap and keeps every card aligned.
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=52, r=42, t=42, b=34),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Arial", size=9, color="#26415d"),
        showlegend=legend,
        hoverlabel=dict(bgcolor="#173a5b", font_color="white", font_size=11),
        title=dict(
            text=title or "",
            x=0.015,
            y=0.98,
            xanchor="left",
            yanchor="top",
            font=dict(family="Arial", size=13, color="#173a5b"),
        ),
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        tickfont=dict(size=8, color="#536b83"),
        title_font=dict(size=8, color="#536b83"),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#e8eef5",
        zeroline=False,
        tickfont=dict(size=8, color="#536b83"),
        title_font=dict(size=8, color="#536b83"),
    )
    return fig


def chart_card(title, fig, height=190, subtitle=None):
    with st.container(border=True):
        # Heading is rendered by Plotly, not as a separate HTML element.
        if subtitle:
            fig.add_annotation(
                text=subtitle, x=0.015, y=1.0, xref="paper", yref="paper",
                xanchor="left", yanchor="bottom", showarrow=False,
                font=dict(size=8, color="#72869a")
            )
        st.plotly_chart(style_fig(fig, height=height, title=title), use_container_width=True, config=PLOT)


def empty_card(title, message="No data available for the selected filters."):
    with st.container(border=True):
        st.markdown(
            f'<div style="color:#173a5b;font-size:13px;font-weight:800;padding:7px 5px 4px 5px;">{title}</div>',
            unsafe_allow_html=True,
        )
        st.info(message)

# ============================================================
# ROW 1 — Revenue / Cuisine / Channel
# ============================================================
r1a, r1b, r1c = st.columns([1.55, 1.05, 1.10])

with r1a:
    trend = x.groupby("FULL_DATE", as_index=False).agg(
        Revenue=("NET_AMOUNT", "sum"),
        Orders=("ORDER_ID", "nunique"),
    )
    fig = go.Figure()
    if not trend.empty:
        fig.add_trace(go.Bar(
            x=trend["FULL_DATE"], y=trend["Revenue"], name="Net Revenue",
            marker_color="#55a9ee",
            hovertemplate="<b>%{x|%d %b %Y}</b><br>Net Revenue: ₹%{y:,.2f}<br>Orders: %{customdata}<extra></extra>",
            customdata=trend["Orders"],
        ))
        fig.add_trace(go.Scatter(
            x=trend["FULL_DATE"], y=trend["Orders"], name="Orders",
            mode="lines+markers", yaxis="y2", line=dict(color="#a84be2", width=2),
            marker=dict(size=5), customdata=trend["Revenue"],
            hovertemplate="<b>%{x|%d %b %Y}</b><br>Orders: %{y}<br>Revenue: ₹%{customdata:,.2f}<extra></extra>",
        ))
    fig.update_layout(
        yaxis=dict(title="Revenue (₹)", tickformat="~s"),
        yaxis2=dict(title="Orders", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", y=1.04, x=0.60, font=dict(size=8)),
    )
    chart_card("Revenue Trend", fig, 195)

with r1b:
    cm = x.groupby("CUISINE", as_index=False)["NET_AMOUNT"].sum().sort_values("NET_AMOUNT", ascending=False)
    if cm.empty:
        empty_card("Cuisine Mix")
    else:
        fig = px.pie(cm, names="CUISINE", values="NET_AMOUNT", hole=0.60)
        fig.update_traces(
            textinfo="percent", textfont=dict(size=9),
            hovertemplate="<b>%{label}</b><br>Revenue: ₹%{value:,.2f}<br>Share: %{percent}<extra></extra>",
        )
        fig.update_layout(legend=dict(font=dict(size=8), x=0.98, xanchor="left", y=0.5))
        chart_card("Cuisine Mix", fig, 195)

with r1c:
    ch = x.groupby("ORDER_CHANNEL", as_index=False).agg(
        Revenue=("NET_AMOUNT", "sum"), Orders=("ORDER_ID", "nunique")
    ).sort_values("Revenue", ascending=True)
    if ch.empty:
        empty_card("Revenue by Order Channel")
    else:
        fig = px.bar(ch, x="Revenue", y="ORDER_CHANNEL", orientation="h", custom_data=["Orders"])
        fig.update_traces(
            marker_color="#55a9ee",
            hovertemplate="<b>%{y}</b><br>Revenue: ₹%{x:,.2f}<br>Orders: %{customdata[0]}<extra></extra>",
        )
        fig.update_xaxes(tickformat="~s")
        chart_card("Revenue by Order Channel", fig, 195)

# ============================================================
# ROW 2 — Menu / Restaurant / Region / Peak Days
# ============================================================
r2a, r2b, r2c, r2d = st.columns([1.12, 1.15, 0.92, 1.08])

with r2a:
    mp = x.groupby(["ITEM_NAME", "CUISINE"], as_index=False).agg(
        Revenue=("NET_AMOUNT", "sum"), Qty=("QTY", "sum"), Orders=("ORDER_ID", "nunique")
    ).sort_values("Revenue", ascending=False).head(5).sort_values("Revenue", ascending=True)
    if mp.empty:
        empty_card("Top 5 Menu Items by Revenue")
    else:
        mp["Revenue"] = pd.to_numeric(mp["Revenue"], errors="coerce").astype(float)
        mp["Contribution"] = (mp["Revenue"] / revenue * 100) if revenue else 0.0
        fig = px.bar(mp, x="Revenue", y="ITEM_NAME", orientation="h", custom_data=["CUISINE", "Qty", "Orders", "Contribution"])
        fig.update_traces(
            marker_color="#55a9ee",
            hovertemplate="<b>%{y}</b><br>Revenue: ₹%{x:,.2f}<br>Contribution: %{customdata[3]:.2f}%<br>Qty: %{customdata[1]}<br>Orders: %{customdata[2]}<br>Cuisine: %{customdata[0]}<extra></extra>",
        )
        fig.update_xaxes(tickformat="~s")
        chart_card("Top 5 Menu Items by Revenue", fig, 180)

with r2b:
    rp = x.groupby(["RESTAURANT_NAME", "REGION"], as_index=False).agg(
        Revenue=("NET_AMOUNT", "sum"), Orders=("ORDER_ID", "nunique")
    ).sort_values("Revenue", ascending=False).head(6).sort_values("Revenue", ascending=True)
    if rp.empty:
        empty_card("Restaurant Revenue")
    else:
        fig = px.bar(rp, x="Revenue", y="RESTAURANT_NAME", orientation="h", custom_data=["REGION", "Orders"])
        fig.update_traces(
            marker_color="#55a9ee",
            hovertemplate="<b>%{y}</b><br>Revenue: ₹%{x:,.2f}<br>Region: %{customdata[0]}<br>Orders: %{customdata[1]}<extra></extra>",
        )
        fig.update_xaxes(tickformat="~s")
        chart_card("Restaurant Revenue", fig, 180)

with r2c:
    rg = x.groupby("REGION", as_index=False).agg(
        Revenue=("NET_AMOUNT", "sum"), Orders=("ORDER_ID", "nunique")
    ).sort_values("Revenue", ascending=False)
    if rg.empty:
        empty_card("Region Comparison")
    else:
        fig = px.bar(rg, x="REGION", y="Revenue", custom_data=["Orders"])
        fig.update_traces(
            marker_color="#7f6be8",
            hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,.2f}<br>Orders: %{customdata[0]}<extra></extra>",
        )
        fig.update_yaxes(tickformat="~s")
        chart_card("Region Comparison", fig, 180)

with r2d:
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pk = x.groupby("DAY_OF_WEEK", as_index=False).agg(
        Revenue=("NET_AMOUNT", "sum"), Orders=("ORDER_ID", "nunique")
    )
    if pk.empty:
        empty_card("Peak Days")
    else:
        pk["DAY_OF_WEEK"] = pd.Categorical(pk["DAY_OF_WEEK"], categories=days, ordered=True)
        pk = pk.sort_values("DAY_OF_WEEK")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=pk["DAY_OF_WEEK"], y=pk["Revenue"], name="Revenue", marker_color="#55a9ee",
            hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,.2f}<br>Orders: %{customdata}<extra></extra>", customdata=pk["Orders"]
        ))
        fig.add_trace(go.Scatter(
            x=pk["DAY_OF_WEEK"], y=pk["Orders"], name="Orders", yaxis="y2",
            mode="lines+markers", line=dict(color="#e35ba6", width=2), marker=dict(size=5),
            hovertemplate="<b>%{x}</b><br>Orders: %{y}<br>Revenue: ₹%{customdata:,.2f}<extra></extra>", customdata=pk["Revenue"]
        ))
        fig.update_layout(
            yaxis=dict(title="Revenue", tickformat="~s"),
            yaxis2=dict(title="Orders", overlaying="y", side="right", showgrid=False),
            legend=dict(orientation="h", y=1.04, x=0.52, font=dict(size=8)),
        )
        chart_card("Peak Days", fig, 180)

# ============================================================
# ROW 3 — Loyalty + Explorer
# ============================================================
r3a, r3b = st.columns([0.82, 2.18])

with r3a:
    lp = x.groupby("LOYALTY_TIER", as_index=False).agg(
        Revenue=("NET_AMOUNT", "sum"), Orders=("ORDER_ID", "nunique")
    )
    if lp.empty:
        empty_card("Loyalty Tier Analysis")
    else:
        fig = px.pie(lp, names="LOYALTY_TIER", values="Revenue", hole=0.60)
        fig.update_traces(
            textinfo="percent", textfont=dict(size=8),
            hovertemplate="<b>%{label}</b><br>Revenue: ₹%{value:,.2f}<br>Share: %{percent}<br>Orders: %{customdata}<extra></extra>",
            customdata=lp["Orders"],
        )
        fig.update_layout(legend=dict(font=dict(size=8), x=0.98, xanchor="left", y=0.5))
        chart_card("Loyalty Tier Analysis", fig, 180)

with r3b:
    with st.container(border=True):
        st.markdown('<div class="explorer-title">🔎 Explorer — Restaurant × Item × Customer Tier</div>', unsafe_allow_html=True)
        explorer = (
            x.groupby(
                ["FULL_DATE", "RESTAURANT_NAME", "ITEM_NAME", "LOYALTY_TIER", "REGION", "CUISINE"],
                as_index=False,
            )
            .agg(Orders=("ORDER_ID", "nunique"), Quantity=("QTY", "sum"), Revenue=("NET_AMOUNT", "sum"))
            .sort_values("Revenue", ascending=False)
            .head(7)
        )
        explorer = explorer.rename(columns={
            "FULL_DATE": "Date",
            "RESTAURANT_NAME": "Restaurant",
            "ITEM_NAME": "Item",
            "LOYALTY_TIER": "Customer Tier",
            "REGION": "Region",
            "CUISINE": "Cuisine",
        })
        if explorer.empty:
            st.info("No explorer records match the selected filters.")
        else:
            explorer["Date"] = pd.to_datetime(explorer["Date"]).dt.strftime("%Y-%m-%d")
            explorer["Revenue"] = explorer["Revenue"].map(lambda v: f"₹{v:,.0f}")
            st.dataframe(explorer, use_container_width=True, hide_index=True, height=155)
            csv_bytes = explorer.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇ Export CSV",
                csv_bytes,
                "restaurant_analytics_explorer.csv",
                "text/csv",
            )

st.markdown(
    '<div class="footer-note">Hover over any chart for detailed values. All filters are linked and update the complete dashboard. KPI definitions: Revenue = SUM(NET_AMOUNT), Orders = COUNT(DISTINCT ORDER_ID), AOV = Revenue / Orders.</div>',
    unsafe_allow_html=True,
)
