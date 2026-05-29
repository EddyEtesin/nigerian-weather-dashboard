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
.stApp { background: #f0f4f8; }
.block-container { padding: 2.5rem 3.5rem 4rem !important; max-width: 100% !important; }

/* ── Header ── */
.pg-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 36px;
}
.pg-title { font-size: 24px; font-weight: 600; color: #0f172a; letter-spacing: -0.03em; }
.pg-updated { font-size: 11px; color: #94a3b8; font-family: 'DM Mono', monospace; }

/* ── Section labels ── */
.section-heading {
    font-size: 10px;
    font-weight: 600;
    color: #94a3b8;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin: 36px 0 14px;
}
.section-note {
    font-size: 10px;
    color: #b0bec5;
    font-style: italic;
    margin-left: 8px;
    font-weight: 400;
    letter-spacing: 0;
    text-transform: none;
}

/* ── City grid — pure CSS, no Streamlit columns ── */
.city-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 14px;
}
.city-card {
    background: #ffffff;
    border-radius: 18px;
    padding: 22px 20px 20px;
    border: 1px solid #e2e8f0;
    display: flex;
    flex-direction: column;
    gap: 0;
}
.city-card-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
}
.city-label {
    font-size: 10px;
    font-weight: 600;
    color: #94a3b8;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.city-icon { font-size: 26px; line-height: 1; }
.city-temp {
    font-size: 36px;
    font-weight: 300;
    color: #0f172a;
    font-family: 'DM Mono', monospace;
    letter-spacing: -0.04em;
    line-height: 1;
    margin-bottom: 6px;
}
.city-cond {
    font-size: 12px;
    color: #64748b;
    margin-bottom: 14px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.city-tip {
    font-size: 11px;
    color: #2563eb;
    background: #eff6ff;
    border-radius: 10px;
    padding: 9px 12px;
    line-height: 1.55;
    margin-top: auto;
}

/* ── Forecast grid — pure CSS ── */
.fc-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 12px;
    margin-top: 4px;
}
.fc-card {
    background: #ffffff;
    border-radius: 16px;
    border: 1px solid #e2e8f0;
    padding: 20px 12px 16px;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.fc-card.fc-today {
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
.fc-today .fc-day { color: #475569; }
.fc-date {
    font-size: 10px;
    color: #cbd5e1;
    font-family: 'DM Mono', monospace;
    margin-bottom: 16px;
}
.fc-today .fc-date { color: #334155; }
.fc-ico { font-size: 28px; margin-bottom: 8px; }
.fc-cond {
    font-size: 11px;
    color: #64748b;
    line-height: 1.5;
    margin-bottom: 10px;
    min-height: 32px;
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
.t-hi { color: #f97316; font-weight: 500; }
.t-lo { color: #3b82f6; font-weight: 500; }
.fc-today .t-hi { color: #fb923c; }
.fc-today .t-lo { color: #60a5fa; }
.fc-tip {
    font-size: 10px;
    line-height: 1.55;
    color: #2563eb;
    background: #eff6ff;
    border-radius: 8px;
    padding: 7px 10px;
    width: 100%;
    box-sizing: border-box;
    margin-top: auto;
}
.fc-today .fc-tip { background: #1e293b; color: #7dd3fc; }

/* ── Selectbox ── */
div[data-baseweb="select"] > div {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    color: #0f172a !important;
    font-size: 14px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    margin-bottom: 16px;
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
    if "heavy rain" in c or "violent" in c: return "Expect flooding. Allow extra travel time."
    if "rain" in c or "shower" in c or "drizzle" in c: return "Light rain likely. Keep an umbrella handy."
    if "fog" in c:       return "Poor visibility. Drive slowly."
    if temp >= 38:       return "Extreme heat. Stay hydrated, avoid direct sun."
    if temp >= 34:       return "Hot day ahead. Drink plenty of water."
    if temp >= 30:       return "Warm conditions. Keep water close."
    if "overcast" in c:  return "Cool and overcast. Good day to be outdoors."
    return "Pleasant conditions today."


# ── Header ────────────────────────────────────────────────
st.markdown(f"""
<div class="pg-header">
    <div class="pg-title">Nigeria Weather</div>
    <div class="pg-updated">Updated {current_df['date'].iloc[0]} · {current_df['time'].iloc[0]}</div>
</div>
""", unsafe_allow_html=True)


# ── Current conditions — pure CSS grid, no st.columns ────
st.markdown(
    "<div class='section-heading'>Current Conditions"
    "<span class='section-note'> — live reading right now</span></div>",
    unsafe_allow_html=True
)

cards_html = '<div class="city-grid">'
for _, row in current_df.iterrows():
    icon, label = simplify(row["condition"])
    advice = tip(row["condition"], row["temperature"])
    cards_html += f"""
    <div class="city-card">
        <div class="city-card-top">
            <div class="city-label">{row['city']}</div>
            <div class="city-icon">{icon}</div>
        </div>
        <div class="city-temp">{row['temperature']}°C</div>
        <div class="city-cond">{label} · {row['humidity']}% humidity</div>
        <div class="city-tip">{advice}</div>
    </div>"""
cards_html += "</div>"
st.markdown(cards_html, unsafe_allow_html=True)


# ── 7-day forecast ────────────────────────────────────────
st.markdown(
    "<div class='section-heading'>7-Day Forecast"
    "<span class='section-note'> — daily high / low range</span></div>",
    unsafe_allow_html=True
)

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
    name="Daily High", mode="lines+markers",
    line=dict(color="#f97316", width=2.5),
    marker=dict(size=7, color="#f97316", line=dict(width=2, color="#fff")),
))
fig.add_trace(go.Scatter(
    x=city_fc["day_name"], y=city_fc["temp_min"],
    name="Daily Low", mode="lines+markers",
    line=dict(color="#3b82f6", width=2.5),
    marker=dict(size=7, color="#3b82f6", line=dict(width=2, color="#fff")),
    fill="tonexty",
    fillcolor="rgba(59,130,246,0.05)"
))
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans", color="#94a3b8", size=12),
    margin=dict(l=0, r=0, t=20, b=0),
    height=220,
    legend=dict(
        orientation="h", y=1.18, x=1, xanchor="right",
        font=dict(size=11, color="#94a3b8"),
        bgcolor="rgba(0,0,0,0)"
    ),
    xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color="#94a3b8", size=11)),
    yaxis=dict(
        showgrid=True, gridcolor="#f1f5f9", gridwidth=1,
        zeroline=False, tickfont=dict(color="#94a3b8", family="DM Mono", size=11),
        ticksuffix="°"
    ),
    hovermode="x unified",
)
st.plotly_chart(fig, use_container_width=True)

# Forecast cards — pure CSS grid
fc_html = '<div class="fc-grid">'
for _, row in city_fc.iterrows():
    icon, label = simplify(row["condition"])
    advice = tip(row["condition"], row["temp_max"])
    is_today = row["day_name"] == today_name
    card_cls = "fc-card fc-today" if is_today else "fc-card"
    fc_html += f"""
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
    </div>"""
fc_html += "</div>"
st.markdown(fc_html, unsafe_allow_html=True)


# ── City comparison ───────────────────────────────────────
st.markdown(
    "<div class='section-heading'>Temperature Comparison — Today</div>",
    unsafe_allow_html=True
)

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
        ticksuffix="°", range=[15, max(sorted_df["temperature"]) + 5]
    ),
    yaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color="#64748b")),
)
st.plotly_chart(fig2, use_container_width=True)
