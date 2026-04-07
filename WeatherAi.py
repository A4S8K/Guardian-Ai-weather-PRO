import streamlit as st
import pandas as pd
import requests
from openai import OpenAI
import plotly.express as px
from datetime import datetime
import json

st.set_page_config(page_title="Guardian AI Weather PRO", page_icon="🌍", layout="wide")

st.title("🌍 Guardian AI Weather PRO")
st.subheader("Жер бетіндегі табиғи апаттарды ЖИ арқылы болжап, адамзатқа көмек беру")
st.markdown("**Арслан Өмен, Иманғали Құрбанбек** • Төлеби ауданының мамандандырылған мектеп-интернаты, 9-сынып")

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("⚙️ Параметрлер")
    openai_key = st.text_input("OpenAI API Key (GPT-4o-mini)", type="password", value="")
    if not openai_key:
        st.warning("OpenAI API кілтін енгізіңіз!")
        st.stop()
    
    client = OpenAI(api_key=openai_key)
    
    st.info("Дерек көздері: Open-Meteo + OpenAI GPT-4o-mini")

# ====================== ҚАЛА ІЗДЕУ ======================
st.header("📍 Қала немесе елді мекенді енгізіңіз")
city_input = st.text_input("Қала аты", placeholder="Алматы / Astana / Shymkent", value="Almaty")

def geocode_city(city_name: str):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=10&language=kk&format=json"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json().get("results", [])
    except Exception as e:
        st.error(f"Геокодтау қатесі: {e}")
        return []

if city_input:
    results = geocode_city(city_input)
    
    if results:
        options = []
        for r in results:
            label = f"{r.get('name', '')}, {r.get('admin1', '')} {r.get('country', '')} (lat: {r['latitude']:.4f}, lon: {r['longitude']:.4f})"
            options.append((label, r['latitude'], r['longitude']))
        
        selected_label = st.selectbox("Нәтижелер (10 нұсқаға дейін)", [opt[0] for opt in options])
        idx = [opt[0] for opt in options].index(selected_label)
        lat, lon = options[idx][1], options[idx][2]
        
        st.success(f"Таңдалды: {selected_label}")
    else:
        st.warning("Қала табылмады. Басқа атаумен көріңіз.")
        st.stop()
else:
    st.stop()

# ====================== ДЕРЕКТЕРДІ АЛУ ======================
@st.cache_data(ttl=1800)  # 30 минут
def fetch_weather(lat: float, lon: float):
    url = (f"https://api.open-meteo.com/v1/forecast?"
           f"latitude={lat}&longitude={lon}&"
           f"current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,"
           f"rain,showers,snowfall,weather_code,cloud_cover,wind_speed_10m,wind_gusts_10m,uv_index&"
           f"hourly=temperature_2m,relative_humidity_2m,precipitation_probability,precipitation,"
           f"cloud_cover,wind_speed_10m,uv_index&"
           f"daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,"
           f"wind_speed_10m_max,uv_index_max&timezone=auto")
    resp = requests.get(url)
    return resp.json()

@st.cache_data(ttl=1800)
def fetch_air_quality(lat: float, lon: float):
    url = (f"https://air-quality-api.open-meteo.com/v1/air-quality?"
           f"latitude={lat}&longitude={lon}&"
           f"current=european_aqi,pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone")
    resp = requests.get(url)
    return resp.json()

weather_data = fetch_weather(lat, lon)
aq_data = fetch_air_quality(lat, lon)

# ====================== ҚАЗІРГІ ЖАҒДАЙ ======================
current = weather_data["current"]
st.header(f"📊 Қазіргі жағдай — {datetime.fromtimestamp(current['time']).strftime('%d.%m.%Y %H:%M')}")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("🌡️ Температура", f"{current['temperature_2m']}°C")
with col2:
    st.metric("💧 Ылғалдылық", f"{current['relative_humidity_2m']}%")
with col3:
    st.metric("🌬️ Жел", f"{current['wind_speed_10m']} км/сағ")
with col4:
    st.metric("☀️ UV индексі", f"{current.get('uv_index', 'N/A')}")
with col5:
    st.metric("🌧️ Жаңбыр", f"{current.get('precipitation', 0)} мм")

# AQI
aqi = aq_data["current"].get("european_aqi", 0)
if aqi < 50:
    aqi_status = "✅ Жақсы"
elif aqi < 100:
    aqi_status = "🟡 Орташа"
else:
    aqi_status = "🔴 Зиянды"
st.metric("🌫️ AQI (Еуропалық индекс)", f"{aqi} — {aqi_status}")

# ====================== Pandas-тағы математикалық талдау ======================
hourly = weather_data["hourly"]
df_hourly = pd.DataFrame({
    "time": pd.to_datetime(hourly["time"]),
    "temp": hourly["temperature_2m"],
    "humidity": hourly["relative_humidity_2m"],
    "precip_prob": hourly["precipitation_probability"],
    "wind": hourly["wind_speed_10m"],
    "uv": hourly["uv_index"]
})

# Қарапайым тренд (соңғы 24 сағат)
st.subheader("📈 Соңғы 24 сағаттағы тренд")
fig_temp = px.line(df_hourly.head(24), x="time", y="temp", title="Температура өзгерісі")
st.plotly_chart(fig_temp, use_container_width=True)

# ====================== ЖИ АРҚЫЛЫ АПАТ ҚАУПІН БАҒАЛАУ ======================
st.header("🧠 ЖИ (GPT-4o-mini) талдауы және апат қаупі")

prompt = f"""
Сіз — метеорологиялық сарапшысыз. Берілген деректер бойынша табиғи апат қаупін бағалаңыз (дауыл, су тасқыны, аптап ыстық, қатты жел, орман өрті).

Қала: {city_input} (lat: {lat}, lon: {lon})
Қазіргі деректер:
- Температура: {current['temperature_2m']}°C
- Ылғалдылық: {current['relative_humidity_2m']}%
- Жел жылдамдығы: {current['wind_speed_10m']} км/сағ (гүлдеу {current.get('wind_gusts_10m', 0)} км/сағ)
- UV: {current.get('uv_index', 'N/A')}
- Бұлттылық: {current.get('cloud_cover', 0)}%
- Жаңбыр ықтималдығы (сағаттық): {df_hourly['precip_prob'].mean():.1f}%
- 24 сағаттық орташа температура: {df_hourly['temp'].mean():.1f}°C

Соңғы 24 сағаттық тренд:
Температура өзгерісі: {df_hourly['temp'].diff().mean():.2f} °C/сағ
Жел тренді: {df_hourly['wind'].diff().mean():.2f} км/сағ

Қауіп деңгейін 0-100% аралығында есептеңіз. Егер 60%-дан жоғары болса — «ЖОҒАРЫ ҚАУІП» деп ескертіңіз.
Әр апат түріне қысқаша түсініктеме және ұсыныс беріңіз. Жауап қазақ тілінде болсын.
"""

with st.spinner("ЖИ талдау жасап жатыр..."):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=800
    )
    ai_analysis = response.choices[0].message.content

st.markdown("### ЖИ-дың толық сараптамасы")
st.write(ai_analysis)

# Қауіп деңгейін анықтау (қарапайым эвристика + ЖИ мәтінінен)
risk_level = 50  # default
if "60%" in ai_analysis or "70%" in ai_analysis or "80%" in ai_analysis or "90%" in ai_analysis or "жоғары қауіп" in ai_analysis.lower():
    risk_level = 75
    st.error("⚠️ ЖОҒАРЫ ҚАУІП! Апаттық жағдай ықтимал. Алдын ала шаралар қабылдаңыз!")
else:
    st.success("Қауіп деңгейі қалыпты.")

# ====================== 7 КҮНДІК БОЛЖАМ ======================
st.header("📅 7 күндік болжам")
daily = weather_data["daily"]
df_daily = pd.DataFrame({
    "date": pd.to_datetime(daily["time"]),
    "max_temp": daily["temperature_2m_max"],
    "min_temp": daily["temperature_2m_min"],
    "precip": daily["precipitation_sum"],
    "wind_max": daily["wind_speed_10m_max"],
    "uv_max": daily["uv_index_max"]
})

st.dataframe(df_daily.style.format({
    "max_temp": "{:.1f}°C",
    "min_temp": "{:.1f}°C",
    "precip": "{:.1f} мм",
    "wind_max": "{:.1f} км/сағ"
}), use_container_width=True)

# ====================== ҚОСЫМША ======================
st.caption("Технологиялық стек: Python + Streamlit + Pandas + Open-Meteo + OpenAI GPT-4o-mini + Plotly")
st.caption("Жоба 2025–2026 оқу жылына арналған. Локальды іске қосу: `streamlit run Guardian_AI_Weather_PRO.py`")

st.markdown("---")
st.markdown("**Қорытынды:** Бұл код сіздің ғылыми жобаңыздың барлық сипаттамасын (MVP, алгоритмдер, ЖИ + математика симбиозы) толық жүзеге асырады.")
