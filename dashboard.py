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
@st.cache_data(ttl=3600)
def load_data():
    current  = pd.read_csv("weather_current.csv")
    forecast = pd.read_csv("weather_forecast.csv")
    return current, forecast

try:
    current_df, forecast_df = load_data()
except FileNotFoundError:
    st.error("⚠️ Weather data not found. Please run fetch_weather.py first.")
    st.stop()

# ── Map weather conditions to simple human labels ─────────
def simplify_condition(condition: str) -> str:
    condition = condition.lower()
    if "thunder" in condition:
        return "⛈️ Thunderstorm"
    elif "heavy rain" in condition or "violent" in condition or "dense" in condition:
        return "🌧️ Heavy Rain"
    elif "rain" in condition or "shower" in condition or "drizzle" in condition:
        return "🌦️ Light Rain"
    elif "fog" in condition:
        return "🌫️ Foggy"
    elif "overcast" in condition or "cloudy" in condition:
        return "☁️ Cloudy"
    elif "partly" in condition:
        return "⛅ Partly Cloudy"
    elif "clear" in condition or "sunshine" in condition or "sunny" in condition:
        return "☀️ Sunshine"
    else:
        return "🌡️ Mild"

# ── Header ─────────────────────────────────────────────────
st.title("🇳🇬 Nigeria Weather Dashboard")
st.caption(f"Last updated: {current_df['date'].iloc[0]} at {current_df['time'].iloc[0]}")
st.divider()

# ── Section 1: Current weather cards ──────────────────────
st.subheader("Current Weather Conditions Across Nigerian Cities")

cols = st.columns(5) # 5 per row, 2 rows for 10 cities + Uyo

for i, row in current_df.iterrows():
    with cols[i % 5]:
        st.metric(
            label=row["city"],
            value=f"{row['temperature']}°C",
            delta=simplify_condition(row["condition"])
        )
        st.caption(f"💧 {row['humidity']}% humidity")
        st.caption(f"💨 {row['wind_speed']} km/h wind")

st.divider()

# ── Section 2: 7-day forecast by city ─────────────────────
st.subheader("7-Day Forecast by City")

selected_city = st.selectbox(
    "Choose a city:",
    options=sorted(current_df["city"].tolist())
)

city_forecast = forecast_df[forecast_df["city"] == selected_city].copy()
city_forecast["forecast_date"] = pd.to_datetime(city_forecast["forecast_date"])
city_forecast["simple_condition"] = city_forecast["condition"].apply(simplify_condition)
city_forecast["day"] = city_forecast["forecast_date"].dt.strftime("%A")  # Monday, Tuesday...

# Temperature chart
fig = px.line(
    city_forecast,
    x="day",
    y=["temp_max", "temp_min"],
    markers=True,
    title=f"Temperature This Week — {selected_city}",
    labels={"day": "", "value": "Temperature (°C)", "variable": ""},
    color_discrete_map={"temp_max": "#FF6B35", "temp_min": "#4A90D9"}
)
fig.update_layout(hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

# ── Daily condition cards instead of rainfall chart ───────
st.markdown("**Daily Conditions**")
day_cols = st.columns(7)

for i, (_, row) in enumerate(city_forecast.iterrows()):
    with day_cols[i % 7]:
        st.markdown(f"""
        <div style="
            background: #1e2130;
            border-radius: 10px;
            padding: 12px 8px;
            text-align: center;
            margin: 4px 0;
        ">
            <div style="font-size:11px; color:#aaa;">{row['day']}</div>
            <div style="font-size:22px; margin: 6px 0;">{row['simple_condition'].split()[0]}</div>
            <div style="font-size:11px; color:#eee;">{' '.join(row['simple_condition'].split()[1:])}</div>
            <div style="font-size:12px; color:#FF6B35; margin-top:4px;">↑ {row['temp_max']}°C</div>
            <div style="font-size:12px; color:#4A90D9;">↓ {row['temp_min']}°C</div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Section 3: Compare cities today ───────────────────────
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
