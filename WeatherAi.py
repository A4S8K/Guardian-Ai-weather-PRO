import streamlit as st
import pandas as pd
import requests
from openai import OpenAI
import plotly.express as px
import time

st.set_page_config(page_title="Guardian AI Weather PRO", page_icon="🌍", layout="wide")

st.title("🌍 Guardian AI Weather PRO")
st.subheader("Жер бетіндегі табиғи апаттарды ЖИ арқылы болжап, адамзатқа көмек беру")
st.markdown("**Арслан Өмен, Иманғали Құрбанбек** • Төлеби ауданының мамандандырылған мектеп-интернаты, 9-сынып")

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("⚙️ Параметрлер")
    openai_key = st.text_input("OpenAI API Key (GPT-4o-mini)", type="password", value="")
    weatherapi_key = st.text_input("WeatherAPI.com API Key", type="password", value="")
    
    if not weatherapi_key:
        st.error("⚠️ WeatherAPI.com API кілтін енгізіңіз!")
        st.stop()
    
    if not openai_key:
        st.warning("OpenAI API кілтін енгізбесеңіз, ЖИ талдауы жұмыс істемейді.")
        client = None
    else:
        client = OpenAI(api_key=openai_key)

# ====================== ҚАЛА ІЗДЕУ ======================
st.header("📍 Қала немесе елді мекенді енгізіңіз")
city_input = st.text_input("Қала аты", placeholder="Shymkent / Алматы / Astana", value="Shymkent")

if not city_input.strip():
    st.stop()

# ====================== ДЕРЕКТЕРДІ АЛУ (WeatherAPI) ======================
@st.cache_data(ttl=1800)
def fetch_weather_weatherapi(city: str, api_key: str):
    url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=7&aqi=yes&alerts=yes&lang=kk"
    
    for attempt in range(3):
        try:
            with st.spinner(f"Ауа райы деректері жүктелуде... (әрекет {attempt+1})"):
                resp = requests.get(url, timeout=15)
                if resp.status_code == 429:
                    st.warning("Rate limit! 10 секунд күтеміз...")
                    time.sleep(10)
                    continue
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            if attempt == 2:
                st.error(f"🌩️ WeatherAPI қатесі: {e}")
                st.stop()
            time.sleep(5)
    st.stop()

weather_data = fetch_weather_weatherapi(city_input, weatherapi_key)

# Координаталарды алу (карта үшін)
lat = weather_data["location"]["lat"]
lon = weather_data["location"]["lon"]

# ====================== ҚАЗІРГІ ЖАҒДАЙ ======================
current = weather_data["current"]
location = weather_data["location"]

st.header(f"📊 Қазіргі жағдай — {location['name']}, {location['country']} ({current['last_updated']})")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("🌡️ Температура", f"{current['temp_c']}°C (сезіледі {current['feelslike_c']}°C)")
with col2:
    st.metric("💧 Ылғалдылық", f"{current['humidity']}%")
with col3:
    st.metric("🌬️ Жел", f"{current['wind_kph']} км/сағ ({current['wind_dir']})")
with col4:
    st.metric("☁️ Бұлттылық", f"{current['cloud']}%")
with col5:
    st.metric("🌧️ Жаңбыр", f"{current.get('precip_mm', 0)} мм")

# AQI
aqi = current.get('air_quality', {}).get('us-epa-index', 0)
aqi_status = "✅ Жақсы" if aqi <= 2 else "🟡 Орташа" if aqi <= 4 else "🔴 Зиянды"
st.metric("🌫️ AQI (US EPA)", f"{aqi} — {aqi_status}")

# ====================== Pandas талдау (Hourly) ======================
forecast = weather_data["forecast"]["forecastday"]
hourly_data = []
for day in forecast:
    for hour in day["hour"]:
        hourly_data.append({
            "time": pd.to_datetime(hour["time"]),
            "temp": hour["temp_c"],
            "humidity": hour["humidity"],
            "precip_prob": hour["chance_of_rain"],
            "wind": hour["wind_kph"],
            "uv": hour["uv"]
        })

df_hourly = pd.DataFrame(hourly_data)

st.subheader("📈 Алдағы 24 сағаттағы тренд")
fig_temp = px.line(df_hourly.head(24), x="time", y="temp", title="Температура өзгерісі")
st.plotly_chart(fig_temp, use_container_width=True)

# ====================== ЖИ ТАЛДАУЫ ======================
st.header("🧠 ЖИ (GPT-4o-mini) талдауы және апат қаупі")

if client is None:
    ai_analysis = "ЖИ талдауы қолжетімсіз."
else:
    prompt = f"""
Сіз — метеорологиялық сарапшысыз. Берілген деректер бойынша табиғи апат қаупін (дауыл, су тасқыны, аптап ыстық, қатты жел, орман өрті) бағалаңыз.

Қала: {city_input}
Қазіргі: Температура {current['temp_c']}°C, Ылғалдылық {current['humidity']}%, Жел {current['wind_kph']} км/сағ

Алдағы 24 сағаттағы орташа температура: {df_hourly.head(24)['temp'].mean():.1f}°C
Жаңбыр ықтималдығы (орташа): {df_hourly.head(24)['precip_prob'].mean():.1f}%

Қауіп деңгейін 0-100% аралығында есептеңіз. 60%-дан жоғары болса «ЖОҒАРЫ ҚАУІП» деп ескертіңіз.
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

if client and ("жоғары қауіп" in ai_analysis.lower() or any(p in ai_analysis for p in ["60%", "70%", "80%", "90%"])):
    st.error("⚠️ ЖОҒАРЫ ҚАУІП! Алдын ала шаралар қабылдаңыз!")
else:
    st.success("Қауіп деңгейі қалыпты.")

# ====================== 7 КҮНДІК БОЛЖАМ ======================
st.header("📅 7 күндік болжам")
daily_rows = []
for day in forecast:
    daily_rows.append({
        "date": day["date"],
        "max_temp": day["day"]["maxtemp_c"],
        "min_temp": day["day"]["mintemp_c"],
        "precip": day["day"]["totalprecip_mm"],
        "wind_max": day["day"]["maxwind_kph"],
        "uv_max": day["day"]["uv"]
    })

df_daily = pd.DataFrame(daily_rows)
st.dataframe(df_daily.style.format({
    "max_temp": "{:.1f}°C", "min_temp": "{:.1f}°C",
    "precip": "{:.1f} мм", "wind_max": "{:.1f} км/сағ"
}), use_container_width=True)

# ====================== ИНТЕРАКТИВТІ WINDY КАРТАСЫ ======================
st.header("🗺️ Интерактивті Windy картасы (ауа райы қабаттары)")

windy_url = f"https://embed.windy.com/embed2.html?lat={lat}&lon={lon}&zoom=10&level=surface&overlay=wind&menu=&message=true&marker=true&calendar=now&pressure=&type=map&location=coordinates&detail=&metricWind=km/h&metricTemp=C"

st.components.v1.iframe(src=windy_url, height=650, scrolling=True)

st.caption("💡 Картада қабаттарды ауыстырыңыз: Wind, Rain, Temperature, Radar, Clouds, Pressure және т.б. Zoom және жылжыту мүмкіндігі бар.")

# ====================== ҚОСЫМША ======================
st.caption("Дерек көзі: WeatherAPI.com + Windy.com + OpenAI GPT-4o-mini")
