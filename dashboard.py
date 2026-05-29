import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="Nigeria Weather",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }
.stApp { background: #f5f7fa; }
.block-container { padding: 3rem 4rem 5rem !important; max-width: 1440px; }

.pg-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 36px;
}
.pg-title { font-size: 28px; font-weight: 600; color: #0f172a; letter-spacing: -0.03em; }
.pg-updated { font-size: 12px; color: #94a3b8; font-family: 'DM Mono', monospace; }

.section-heading {
    font-size: 11px;
    font-weight: 600;
    color: #94a3b8;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 40px 0 16px;
}

/* City current cards */
.city-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 22px 20px;
    border: 1px solid #e8edf3;
    position: relative;
    height: 100%;
}
.city-card-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 14px;
}
.city-label {
    font-size: 11px;
    font-weight: 600;
    color: #94a3b8;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.city-icon { font-size: 26px; line-height: 1; }
.city-temp {
    font-size: 38px;
    font-weight: 300;
    color: #0f172a;
    font-family: 'DM Mono', monospace;
    letter-spacing: -0.04em;
    line-height: 1;
    margin-bottom: 4px;
}
.city-cond { font-size: 12px; color: #64748b; margin-bottom: 14px; }
.city-tip {
    font-size: 11px;
    color: #3b82f6;
    background: #eff6ff;
    border-radius: 8px;
    padding: 7px 10px;
    line-height: 1.5;
}

/* Forecast cards */
.fc-wrap {
    background: #ffffff;
    border-radius: 16px;
    border: 1px solid #e8edf3;
    padding: 20px 18px;
    text-align: center;
    height: 100%;
}
.fc-wrap.fc-today {
    background: #0f172a;
    border-color: #0f172a;
}
.fc-day {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    color: #94a3b8;
    margin-bottom: 2px;
}
.fc-today .fc-day { color: #64748b; }
.fc-date {
    font-size: 11px;
    color: #cbd5e1;
    font-family: 'DM Mono', monospace;
    margin-bottom: 14px;
}
.fc-today .fc-date { color: #475569; }
.fc-ico { font-size: 28px; margin-bottom: 8px; }
.fc-cond {
    font-size: 11px;
    color: #64748b;
    min-height: 32px;
    line-height: 1.5;
    margin-bottom: 10px;
}
.fc-today .fc-cond { color: #64748b; }
.fc-temps {
    display: flex;
    justify-content: center;
    gap: 8px;
    font-size: 13px;
    font-family: 'DM Mono', monospace;
    margin-bottom: 10px;
}
.t-hi { color: #f97316; }
.t-lo { color: #3b82f6; }
.fc-today .t-hi { color: #fb923c; }
.fc-today .t-lo { color: #60a5fa; }
.fc-tip {
    font-size: 10px;
    line-height: 1.5;
    color: #3b82f6;
    background: #eff6ff;
    border-radius: 6px;
    padding: 5px 8px;
}
.fc-today .fc-tip {
    background: #1e293b;
    color: #7dd3fc;
}

div[data-baseweb="select"] > div {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    color: #0f172a !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
.stSelectbox label { display: none !important; }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def load_data():
    return pd.read_csv("weather_current.csv"), pd.read_csv("weather_forecast.csv")

try:
    current_df, forecast_df = load_data()
except FileNotFoundError:
    st.error("Weather data not found. Run fetch_weather.py first.")
    st.stop()


def simplify(condition: str):
    c = condition.lower()
    if "thunder" in c:   return ("⛈", "Thunderstorm")
    if "heavy rain" in c or "violent" in c or "dense" in c: return ("🌧", "Heavy Rain")
    if "rain" in c or "shower" in c or "drizzle" in c: return ("🌦", "Light Rain")
    if "fog" in c:       return ("🌫", "Foggy")
    if "overcast" in c:  return ("☁", "Overcast")
    if "cloudy" in c:    return ("⛅", "Partly Cloudy")
    if "clear" in c or "sunshine" in c: return ("☀", "Clear Sky")
    return ("🌤", "Mild")

def tip(condition: str, temp: float) -> str:
    c = condition.lower()
    if "thunder" in c:   return "Stay indoors. Avoid open and elevated areas."
    if "heavy rain" in c or "violent" in c: return "Expect flooding. Carry an umbrella and allow extra travel time."
    if "rain" in c or "shower" in c or "drizzle" in c: return "Light rain likely. Keep an umbrella handy."
    if "fog" in c:       return "Poor visibility. Drive slowly and use your headlights."
    if temp >= 38:       return "Extreme heat. Stay hydrated and avoid direct sun."
    if temp >= 34:       return "Hot day ahead. Drink plenty of water."
    if temp >= 30:       return "Warm conditions. Keep water close."
    if "overcast" in c:  return "Cool and overcast. Great day to be outdoors."
    return "Pleasant conditions today."


# ── Header ────────────────────────────────────────────────
st.markdown(f"""
<div class="pg-header">
    <div class="pg-title">Nigeria Weather</div>
    <div class="pg-updated">Updated {current_df['date'].iloc[0]} · {current_df['time'].iloc[0]}</div>
</div>
""", unsafe_allow_html=True)


# ── Current conditions ────────────────────────────────────
st.markdown("<div class='section-heading'>Current Conditions</div>", unsafe_allow_html=True)

cols = st.columns(6, gap="small")
for i, row in current_df.iterrows():
    icon, label = simplify(row["condition"])
    advice = tip(row["condition"], row["temperature"])
    with cols[i % 6]:
        st.markdown(f"""
        <div class="city-card">
            <div class="city-card-top">
                <div class="city-label">{row['city']}</div>
                <div class="city-icon">{icon}</div>
            </div>
            <div class="city-temp">{row['temperature']}°C</div>
            <div class="city-cond">{label} &nbsp;·&nbsp; {row['humidity']}% humidity</div>
            <div class="city-tip">{advice}</div>
        </div>
        """, unsafe_allow_html=True)


# ── 7-day forecast ────────────────────────────────────────
st.markdown("<div class='section-heading'>7-Day Forecast</div>", unsafe_allow_html=True)

selected_city = st.selectbox("City", options=sorted(current_df["city"].tolist()))

city_fc = forecast_df[forecast_df["city"] == selected_city].copy()
city_fc["forecast_date"] = pd.to_datetime(city_fc["forecast_date"])
city_fc["day_name"] = city_fc["forecast_date"].dt.strftime("%a").str.upper()
city_fc["day_date"] = city_fc["forecast_date"].dt.strftime("%d %b")
today_name = datetime.now().strftime("%a").upper()

# Temperature chart
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=city_fc["day_name"], y=city_fc["temp_max"],
    name="High", mode="lines+markers",
    line=dict(color="#f97316", width=2),
    marker=dict(size=6, color="#f97316", line=dict(width=2, color="#fff")),
))
fig.add_trace(go.Scatter(
    x=city_fc["day_name"], y=city_fc["temp_min"],
    name="Low", mode="lines+markers",
    line=dict(color="#3b82f6", width=2),
    marker=dict(size=6, color="#3b82f6", line=dict(width=2, color="#fff")),
    fill="tonexty",
    fillcolor="rgba(59,130,246,0.06)"
))
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans", color="#94a3b8", size=11),
    margin=dict(l=0, r=0, t=16, b=0),
    height=200,
    legend=dict(
        orientation="h", y=1.15, x=1, xanchor="right",
        font=dict(size=11, color="#94a3b8"),
        bgcolor="rgba(0,0,0,0)"
    ),
    xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color="#94a3b8")),
    yaxis=dict(
        showgrid=True, gridcolor="#f1f5f9",
        zeroline=False, tickfont=dict(color="#94a3b8", family="DM Mono"),
        ticksuffix="°"
    ),
    hovermode="x unified",
)
st.plotly_chart(fig, use_container_width=True)

# Day forecast cards
day_cols = st.columns(7, gap="small")
for i, (_, row) in enumerate(city_fc.iterrows()):
    icon, label = simplify(row["condition"])
    advice = tip(row["condition"], row["temp_max"])
    is_today = row["day_name"] == today_name
    card_cls = "fc-wrap fc-today" if is_today else "fc-wrap"
    with day_cols[i % 7]:
        st.markdown(f"""
        <div class="{card_cls}">
            <div class="fc-day">{row['day_name']}</div>
            <div class="fc-date">{row['day_date']}</div>
            <div class="fc-ico">{icon}</div>
            <div class="fc-cond">{label}</div>
            <div class="fc-temps">
                <span class="t-hi">{row['temp_max']}°</span>
                <span class="t-lo">{row['temp_min']}°</span>
            </div>
            <div class="fc-tip">{advice}</div>
        </div>
        """, unsafe_allow_html=True)


# ── City comparison ───────────────────────────────────────
st.markdown("<div class='section-heading'>Temperature Comparison — Today</div>", unsafe_allow_html=True)

sorted_df = current_df.sort_values("temperature", ascending=True)
fig2 = go.Figure(go.Bar(
    x=sorted_df["temperature"],
    y=sorted_df["city"],
    orientation="h",
    marker=dict(
        color=sorted_df["temperature"],
        colorscale=[[0, "#bfdbfe"], [0.5, "#fdba74"], [1, "#f97316"]],
        showscale=False
    ),
    text=[f"{t}°C" for t in sorted_df["temperature"]],
    textposition="outside",
    textfont=dict(color="#94a3b8", size=11, family="DM Mono"),
))
fig2.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans", color="#94a3b8", size=12),
    margin=dict(l=0, r=60, t=8, b=0),
    height=320,
    xaxis=dict(
        showgrid=True, gridcolor="#f1f5f9",
        zeroline=False, tickfont=dict(color="#94a3b8", family="DM Mono"),
        ticksuffix="°", range=[20, max(sorted_df["temperature"]) + 5]
    ),
    yaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color="#64748b")),
)
st.plotly_chart(fig2, use_container_width=True)
