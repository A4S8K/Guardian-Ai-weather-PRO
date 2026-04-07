import streamlit as st
import requests
import pandas as pd
from openai import OpenAI
from datetime import datetime
import time

st.set_page_config(page_title="Guardian AI Weather PRO", page_icon="🌍", layout="wide")

# OpenAI
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    client = None

# Тілдер
LANGUAGES = ["Қазақша", "Русский", "English"]
selected_lang = st.sidebar.selectbox("🌐 Тіл / Язык / Language", LANGUAGES)

t = {
    "Қазақша": {
        "title": "🌍 Guardian AI Weather PRO",
        "enter_city": "📍 Қала атын жазыңыз",
        "search": "🔍 Іздеу",
        "select_location": "🏘 Нақты орны таңдаңыз",
        "current": "Қазіргі ауа райы",
        "forecast_24": "📈 24 сағаттық болжам",
        "forecast_7": "📅 7 күндік болжам",
        "ai_analysis": "🤖 AI Талдау & Апат ескертуі",
        "risk": "🚨 Табиғи апат қаупі",
        "error": "❌ Ауа райы деректерін алу мүмкін болмады. Қайталап көріңіз.",
        "retrying": "🔄 Қайталап көруде...",
        "success": "✅ Деректер сәтті жүктелді!"
    },
    "Русский": {
        "title": "🌍 Guardian AI Weather PRO",
        "enter_city": "📍 Введите название города",
        "search": "🔍 Поиск",
        "select_location": "🏘 Выберите точное место",
        "current": "Текущая погода",
        "forecast_24": "📈 Прогноз на 24 часа",
        "forecast_7": "📅 Прогноз на 7 дней",
        "ai_analysis": "🤖 AI Анализ и предупреждение",
        "risk": "🚨 Риск природных катастроф",
        "error": "❌ Не удалось получить данные. Попробуйте снова.",
        "retrying": "🔄 Повторная попытка...",
        "success": "✅ Данные успешно загружены!"
    },
    "English": {
        "title": "🌍 Guardian AI Weather PRO",
        "enter_city": "📍 Enter city name",
        "search": "🔍 Search",
        "select_location": "🏘 Select exact location",
        "current": "Current Weather",
        "forecast_24": "📈 24-Hour Forecast",
        "forecast_7": "📅 7-Day Forecast",
        "ai_analysis": "🤖 AI Analysis & Alert",
        "risk": "🚨 Natural Disaster Risk",
        "error": "❌ Failed to fetch weather data. Please try again.",
        "retrying": "🔄 Retrying...",
        "success": "✅ Data loaded successfully!"
    }
}[selected_lang]

# =====================================================
# ЖАҚСАРТЫЛҒАН API (5 рет қайталау + User-Agent)
# =====================================================
def fetch_weather(lat, lon, max_retries=5):
    headers = {"User-Agent": "GuardianAI-Weather-PRO/1.0"}
    for attempt in range(max_retries):
        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,wind_direction_10m,uv_index,precipitation"
                f"&hourly=temperature_2m,precipitation"
                f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
                f"&timezone=auto"
            )
            resp = requests.get(url, timeout=25, headers=headers)
            
            if resp.status_code == 200:
                data = resp.json()
                if "current" in data:
                    return data
            st.warning(f"{t['retrying']} ({attempt+1}/{max_retries})")
            time.sleep(1.2)
        except Exception as e:
            st.warning(f"{t['retrying']} ({attempt+1}/{max_retries}) — {str(e)[:80]}")
            time.sleep(1.2)
    return None

@st.cache_data(ttl=600)
def search_location(query):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=10&language=kk&format=json"
    try:
        return requests.get(url, timeout=10).json().get("results", [])
    except:
        return []

def calculate_risk(cur):
    temp = cur.get("temperature_2m", 0)
    wind = cur.get("wind_speed_10m", 0)
    precip = cur.get("precipitation", 0) or 0
    uv = cur.get("uv_index", 0)
    score = 0
    alerts = []
    if temp > 35 or temp < -25: score += 40; alerts.append("🔥 Аптап ыстық / Қатты аяз")
    if wind > 15: score += 35; alerts.append("🌬 Дауыл / Қатты жел")
    if precip > 15: score += 30; alerts.append("🌧 Су тасқыны")
    if uv > 8: score += 25; alerts.append("☀️ UV қаупі")
    return min(score, 100), alerts

# =====================================================
# ИНТЕРФЕЙС
# =====================================================
st.title(t["title"])
st.caption("Жер бетіндегі табиғи апаттарды ЖИ арқылы ерте болжау")

city_input = st.sidebar.text_input(t["enter_city"], placeholder="Алматы, Астана, Шымкент...")

if city_input:
    locations = search_location(city_input)
    if locations:
        options = [f"{l['name']} ({l.get('admin1','')}, {l.get('country','')})" for l in locations]
        selected = st.sidebar.selectbox(t["select_location"], options)
        
        if st.sidebar.button(t["search"], type="primary", use_container_width=True):
            idx = options.index(selected)
            loc = locations[idx]
            weather_data = fetch_weather(loc["latitude"], loc["longitude"])
            
            if weather_data:
                st.session_state.current_data = {
                    "loc": loc,
                    "weather": weather_data,
                    "timestamp": datetime.now()
                }
                st.success(t["success"])
            else:
                st.error(t["error"])

# НӘТИЖЕ
if "current_data" in st.session_state:
    data = st.session_state.current_data
    loc = data["loc"]
    w = data["weather"]
    cur = w["current"]
    
    risk_score, alerts = calculate_risk(cur)

    tab1, tab2, tab3, tab4 = st.tabs([
        "🌡️ " + t["current"],
        "📈 " + t["forecast_24"],
        "📅 " + t["forecast_7"],
        "🚨 " + t["risk"]
    ])

    with tab1:
        st.subheader(f"📍 {loc['name']}, {loc.get('country', '')}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🌡 Температура", f"{cur.get('temperature_2m','—')}°C")
        c2.metric("💧 Ылғалдылық", f"{cur.get('relative_humidity_2m','—')}%")
        c3.metric("🌬 Жел", f"{cur.get('wind_speed_10m','—')} м/с")
        c4.metric("☀️ UV", cur.get("uv_index", "—"))

    with tab2:
        st.subheader(t["forecast_24"])
        st.line_chart(pd.DataFrame({"Температура (°C)": w["hourly"]["temperature_2m"][:24]}))

    with tab3:
        st.subheader(t["forecast_7"])
        daily = w["daily"]
        st.dataframe(pd.DataFrame({
            "Күн": daily["time"],
            "Макс": daily["temperature_2m_max"],
            "Мин": daily["temperature_2m_min"]
        }), use_container_width=True)

    with tab4:
        st.subheader(t["risk"])
        st.progress(risk_score / 100)
        st.write(f"**Жалпы қауіп деңгейі: {risk_score}%**")
        for alert in alerts:
            st.error(alert)
        if risk_score > 60:
            st.error("🔴 ЖОҒАРЫ ҚАУІП! Абай болыңыз!")

    st.divider()
    st.caption(f"🕒 Соңғы жаңарту: {data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")

else:
    st.info("🔍 Қала атын енгізіп, «Іздеу» батырмасын басыңыз")

st.caption("© 2026 Өмен Арслан, Құрбанбек Иманғали • TobeliDarynA&S")
