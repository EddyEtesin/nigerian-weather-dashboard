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
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Sora', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2.5rem 3rem 4rem; max-width: 1400px; }
.stApp { background: #080c14; }

.page-title {
    font-size: 22px;
    font-weight: 600;
    color: #f1f5f9;
    letter-spacing: -0.02em;
}
.page-sub {
    font-size: 12px;
    color: #334155;
    margin-top: 2px;
}
.section-label {
    font-size: 10px;
    font-weight: 600;
    color: #334155;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin: 28px 0 14px;
}
.divider {
    border: none;
    border-top: 1px solid #0f172a;
    margin: 28px 0;
}

/* Current city cards */
.city-card {
    background: #0d1117;
    border: 1px solid #161d2b;
    border-radius: 14px;
    padding: 18px 14px 16px;
    position: relative;
    overflow: hidden;
}
.city-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #1e3a5f, transparent);
}
.city-name {
    font-size: 10px;
    font-weight: 600;
    color: #475569;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.city-temp {
    font-size: 32px;
    font-weight: 500;
    color: #f1f5f9;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1;
    letter-spacing: -0.03em;
}
.city-icon { font-size: 18px; margin-left: 6px; vertical-align: middle; }
.city-condition {
    font-size: 11px;
    color: #64748b;
    margin: 6px 0 10px;
}
.city-tip {
    font-size: 10px;
    color: #1e40af;
    background: #0f172a;
    border-radius: 6px;
    padding: 5px 8px;
    line-height: 1.5;
}

/* Forecast day cards */
.fc-card {
    background: #0d1117;
    border: 1px solid #161d2b;
    border-radius: 12px;
    padding: 16px 10px;
    text-align: center;
}
.fc-card.today {
    border-color: #1e3a5f;
    background: #0a111e;
}
.fc-day {
    font-size: 10px;
    font-weight: 600;
    color: #475569;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.fc-date {
    font-size: 10px;
    color: #1e3a5f;
    margin-bottom: 10px;
    font-family: 'JetBrains Mono', monospace;
}
.fc-icon { font-size: 22px; margin-bottom: 6px; }
.fc-label {
    font-size: 10px;
    color: #64748b;
    margin-bottom: 10px;
    min-height: 30px;
    line-height: 1.5;
}
.fc-temps {
    display: flex;
    justify-content: center;
    gap: 6px;
    font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 8px;
}
.t-hi { color: #f97316; }
.t-lo { color: #3b82f6; }
.fc-tip {
    font-size: 9.5px;
    color: #1e3a5f;
    background: #080c14;
    border-radius: 5px;
    padding: 4px 6px;
    line-height: 1.5;
}

.stSelectbox label { display: none; }
div[data-baseweb="select"] > div {
    background: #0d1117 !important;
    border-color: #161d2b !important;
    color: #94a3b8 !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)


# ── Data ──────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data():
    return pd.read_csv("weather_current.csv"), pd.read_csv("weather_forecast.csv")

try:
    current_df, forecast_df = load_data()
except FileNotFoundError:
    st.error("Weather data not found. Run fetch_weather.py first.")
    st.stop()


# ── Helpers ───────────────────────────────────────────────
def simplify(condition: str):
    c = condition.lower()
    if "thunder" in c:
        return ("⛈", "Thunderstorm")
    elif "heavy rain" in c or "violent" in c or "dense" in c:
        return ("🌧", "Heavy Rain")
    elif "rain" in c or "shower" in c or "drizzle" in c:
        return ("🌦", "Light Rain")
    elif "fog" in c:
        return ("🌫", "Foggy")
    elif "overcast" in c:
        return ("☁", "Overcast")
    elif "cloudy" in c:
        return ("⛅", "Partly Cloudy")
    elif "clear" in c or "sunshine" in c:
        return ("☀", "Clear Sky")
    else:
        return ("🌤", "Mild")

def tip(condition: str, temp: float) -> str:
    c = condition.lower()
    if "thunder" in c:
        return "Stay indoors if possible. Avoid open areas."
    elif "heavy rain" in c or "violent" in c:
        return "Carry an umbrella. Expect flooding on some roads."
    elif "rain" in c or "shower" in c or "drizzle" in c:
        return "Light rain expected. An umbrella won't hurt."
    elif "fog" in c:
        return "Drive carefully. Visibility is low."
    elif temp >= 38:
        return "Extreme heat. Stay hydrated and limit sun exposure."
    elif temp >= 34:
        return "Very hot today. Drink plenty of water."
    elif temp >= 30:
        return "Warm day. Keep water close."
    elif "overcast" in c or "cloudy" in c:
        return "Overcast skies. Good day to be outdoors."
    else:
        return "Pleasant conditions today. Enjoy your day."


# ── Header ────────────────────────────────────────────────
c1, c2 = st.columns([4, 1])
with c1:
    st.markdown("<div class='page-title'>Nigeria Weather</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='page-sub'>Updated {current_df['date'].iloc[0]} at {current_df['time'].iloc[0]}</div>",
        unsafe_allow_html=True
    )

st.markdown("<hr class='divider'>", unsafe_allow_html=True)


# ── Current conditions ────────────────────────────────────
st.markdown("<div class='section-label'>Current Conditions</div>", unsafe_allow_html=True)

cols = st.columns(6)
for i, row in current_df.iterrows():
    icon, label = simplify(row["condition"])
    advice = tip(row["condition"], row["temperature"])
    with cols[i % 6]:
        st.markdown(f"""
        <div class="city-card">
            <div class="city-name">{row['city']}</div>
            <div>
                <span class="city-temp">{row['temperature']}°</span>
                <span class="city-icon">{icon}</span>
            </div>
            <div class="city-condition">{label} &nbsp;·&nbsp; {row['humidity']}% humidity</div>
            <div class="city-tip">{advice}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)


# ── 7-day forecast ────────────────────────────────────────
st.markdown("<div class='section-label'>7-Day Forecast</div>", unsafe_allow_html=True)

selected_city = st.selectbox("City", options=sorted(current_df["city"].tolist()))

city_fc = forecast_df[forecast_df["city"] == selected_city].copy()
city_fc["forecast_date"] = pd.to_datetime(city_fc["forecast_date"])
city_fc["day_name"] = city_fc["forecast_date"].dt.strftime("%a").str.upper()
city_fc["day_date"] = city_fc["forecast_date"].dt.strftime("%d %b")

# Temperature chart
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=city_fc["day_name"], y=city_fc["temp_max"],
    name="High", mode="lines+markers",
    line=dict(color="#f97316", width=2),
    marker=dict(size=5, color="#f97316"),
))
fig.add_trace(go.Scatter(
    x=city_fc["day_name"], y=city_fc["temp_min"],
    name="Low", mode="lines+markers",
    line=dict(color="#3b82f6", width=2),
    marker=dict(size=5, color="#3b82f6"),
    fill="tonexty",
    fillcolor="rgba(59,130,246,0.04)"
))
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Sora", color="#475569", size=11),
    margin=dict(l=0, r=0, t=16, b=0),
    height=220,
    legend=dict(
        orientation="h", y=1.1, x=1, xanchor="right",
        font=dict(size=10, color="#475569"),
        bgcolor="rgba(0,0,0,0)"
    ),
    xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color="#334155")),
    yaxis=dict(
        showgrid=True, gridcolor="#0f172a", zeroline=False,
        tickfont=dict(color="#334155", family="JetBrains Mono"),
        ticksuffix="°"
    ),
    hovermode="x unified",
)
st.plotly_chart(fig, use_container_width=True)

# Day cards
day_cols = st.columns(7)
today = datetime.now().strftime("%a").upper()

for i, (_, row) in enumerate(city_fc.iterrows()):
    icon, label = simplify(row["condition"])
    advice = tip(row["condition"], row["temp_max"])
    is_today = row["day_name"] == today
    card_class = "fc-card today" if is_today else "fc-card"

    with day_cols[i % 7]:
        st.markdown(f"""
        <div class="{card_class}">
            <div class="fc-day">{row['day_name']}</div>
            <div class="fc-date">{row['day_date']}</div>
            <div class="fc-icon">{icon}</div>
            <div class="fc-label">{label}</div>
            <div class="fc-temps">
                <span class="t-hi">{row['temp_max']}°</span>
                <span class="t-lo">{row['temp_min']}°</span>
            </div>
            <div class="fc-tip">{advice}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)


# ── City comparison ───────────────────────────────────────
st.markdown("<div class='section-label'>Temperature Comparison — Today</div>", unsafe_allow_html=True)

sorted_df = current_df.sort_values("temperature", ascending=True)
fig2 = go.Figure(go.Bar(
    x=sorted_df["temperature"],
    y=sorted_df["city"],
    orientation="h",
    marker=dict(
        color=sorted_df["temperature"],
        colorscale=[[0, "#1e3a5f"], [0.5, "#f97316"], [1, "#ef4444"]],
        showscale=False
    ),
    text=[f"{t}°C" for t in sorted_df["temperature"]],
    textposition="outside",
    textfont=dict(color="#475569", size=11, family="JetBrains Mono"),
))
fig2.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Sora", color="#475569", size=12),
    margin=dict(l=0, r=50, t=8, b=0),
    height=300,
    xaxis=dict(
        showgrid=True, gridcolor="#0f172a",
        zeroline=False, tickfont=dict(color="#334155", family="JetBrains Mono"),
        ticksuffix="°"
    ),
    yaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color="#94a3b8")),
)
st.plotly_chart(fig2, use_container_width=True)
