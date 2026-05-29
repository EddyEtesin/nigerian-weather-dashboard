import requests
import pandas as pd
from datetime import datetime

CITIES = {
    "Lagos":         {"lat": 6.5244,  "lon": 3.3792},
    "Abuja":         {"lat": 9.0579,  "lon": 7.4951},
    "Kano":          {"lat": 12.0022, "lon": 8.5920},
    "Port Harcourt": {"lat": 4.8156,  "lon": 7.0498},
    "Ibadan":        {"lat": 7.3775,  "lon": 3.9470},
    "Enugu":         {"lat": 6.4584,  "lon": 7.5464},
    "Kaduna":        {"lat": 10.5222, "lon": 7.4383},
    "Benin City":    {"lat": 6.3350,  "lon": 5.6270},
    "Jos":           {"lat": 9.8965,  "lon": 8.8583},
    "Maiduguri":     {"lat": 11.8333, "lon": 13.1500},
    "Uyo":           {"lat": 5.0377, "lon": 7.9128},
}

# Maps Open-Meteo weather codes to human-readable descriptions
WEATHER_DESCRIPTIONS = {
    0: "Clear Sky ☀️",
    1: "Mainly Clear 🌤️",
    2: "Partly Cloudy ⛅",
    3: "Overcast ☁️",
    45: "Foggy 🌫️",
    48: "Icy Fog 🌫️",
    51: "Light Drizzle 🌦️",
    53: "Moderate Drizzle 🌦️",
    55: "Dense Drizzle 🌧️",
    61: "Slight Rain 🌧️",
    63: "Moderate Rain 🌧️",
    65: "Heavy Rain 🌧️",
    80: "Slight Showers 🌦️",
    81: "Moderate Showers 🌧️",
    82: "Violent Showers ⛈️",
    95: "Thunderstorm ⛈️",
}

def get_weather_description(code):
    return WEATHER_DESCRIPTIONS.get(code, "Unknown 🌡️")


def fetch_weather():
    current_records = []
    forecast_records = []

    for city, coords in CITIES.items():
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={coords['lat']}"
            f"&longitude={coords['lon']}"
            f"&current=temperature_2m,relative_humidity_2m,"
            f"wind_speed_10m,precipitation,weathercode"
            f"&daily=temperature_2m_max,temperature_2m_min,"
            f"precipitation_sum,weathercode,windspeed_10m_max"
            f"&timezone=Africa%2FLagos"
        )

        response = requests.get(url)
        data = response.json()

        # ── Current weather ───────────────────────────────
        current = data["current"]
        current_records.append({
            "city":          city,
            "date":          datetime.now().strftime("%Y-%m-%d"),
            "time":          datetime.now().strftime("%H:%M"),
            "temperature":   current["temperature_2m"],
            "humidity":      current["relative_humidity_2m"],
            "wind_speed":    current["wind_speed_10m"],
            "precipitation": current["precipitation"],
            "condition":     get_weather_description(current["weathercode"]),
        })

        # ── 7-day forecast ────────────────────────────────
        daily = data["daily"]
        for i in range(len(daily["time"])):
            forecast_records.append({
                "city":          city,
                "forecast_date": daily["time"][i],
                "temp_max":      daily["temperature_2m_max"][i],
                "temp_min":      daily["temperature_2m_min"][i],
                "precipitation": daily["precipitation_sum"][i],
                "wind_speed":    daily["windspeed_10m_max"][i],
                "condition":     get_weather_description(daily["weathercode"][i]),
            })

        print(f"✅ Fetched: {city}")

    # Save both datasets as separate CSVs
    pd.DataFrame(current_records).to_csv("weather_current.csv", index=False)
    pd.DataFrame(forecast_records).to_csv("weather_forecast.csv", index=False)

    print("\n📁 Saved: weather_current.csv and weather_forecast.csv")


fetch_weather()
