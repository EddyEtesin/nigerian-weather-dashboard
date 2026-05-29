import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="Nigeria Weather Dashboard",
    page_icon="🌤️",
    layout="wide"
)

# ── Load data ─────────────────────────────────────────────
@st.cache_data(ttl=3600)  # Cache for 1 hour, then auto-refresh
def load_data():
    current  = pd.read_csv("weather_current.csv")
    forecast = pd.read_csv("weather_forecast.csv")
    return current, forecast

try:
    current_df, forecast_df = load_data()
except FileNotFoundError:
    st.error("⚠️ Weather data not found. Please run fetch_weather.py first.")
    st.stop()

# ── Header ─────────────────────────────────────────────────
st.title("🇳🇬 Nigeria Weather Dashboard")
st.caption(f"Last updated: {current_df['date'].iloc[0]} at {current_df['time'].iloc[0]}")
st.divider()

# ── Section 1: Current weather cards for all cities ────────
st.subheader("📍 Current Conditions Across Nigeria")

cols = st.columns(5)  # 5 cards per row = 2 rows for 10 cities

for i, row in current_df.iterrows():
    with cols[i % 5]:
        st.metric(
            label=row["city"],
            value=f"{row['temperature']}°C",
            delta=row["condition"]
        )
        st.caption(f"💧 {row['humidity']}% humidity")
        st.caption(f"💨 {row['wind_speed']} km/h wind")

st.divider()

# ── Section 2: City forecast ───────────────────────────────
st.subheader("📅 7-Day Forecast by City")

selected_city = st.selectbox(
    "Choose a city:",
    options=current_df["city"].tolist()
)

city_forecast = forecast_df[forecast_df["city"] == selected_city].copy()
city_forecast["forecast_date"] = pd.to_datetime(city_forecast["forecast_date"])

# Temperature chart
fig = px.line(
    city_forecast,
    x="forecast_date",
    y=["temp_max", "temp_min"],
    markers=True,
    title=f"Temperature Forecast — {selected_city}",
    labels={
        "forecast_date": "Date",
        "value": "Temperature (°C)",
        "variable": "Reading"
    },
    color_discrete_map={
        "temp_max": "#FF6B35",
        "temp_min": "#4A90D9"
    }
)
fig.update_layout(hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

# Precipitation chart
fig2 = px.bar(
    city_forecast,
    x="forecast_date",
    y="precipitation",
    title=f"Rainfall Forecast — {selected_city}",
    labels={"forecast_date": "Date", "precipitation": "Rainfall (mm)"},
    color_discrete_sequence=["#4A90D9"]
)
st.plotly_chart(fig2, use_container_width=True)

# Forecast table
st.subheader(f"📋 {selected_city} — Full 7-Day Table")
st.dataframe(
    city_forecast[["forecast_date", "condition", "temp_max", "temp_min", "precipitation", "wind_speed"]]
    .rename(columns={
        "forecast_date":  "Date",
        "condition":      "Condition",
        "temp_max":       "Max Temp (°C)",
        "temp_min":       "Min Temp (°C)",
        "precipitation":  "Rainfall (mm)",
        "wind_speed":     "Max Wind (km/h)"
    })
    .reset_index(drop=True),
    use_container_width=True
)

st.divider()

# ── Section 3: Compare cities ──────────────────────────────
st.subheader("🔁 Compare Cities — Today's Temperature")

fig3 = px.bar(
    current_df.sort_values("temperature", ascending=False),
    x="city",
    y="temperature",
    color="temperature",
    color_continuous_scale="RdYlGn_r",
    title="Current Temperature by City",
    labels={"city": "City", "temperature": "Temperature (°C)"}
)
st.plotly_chart(fig3, use_container_width=True)
