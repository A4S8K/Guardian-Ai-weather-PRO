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
    
    client = OpenAI(api_key=openai_key) if openai_key else None

# ====================== ҚАЛА ІЗДЕУ ======================
st.header("📍 Қала немесе елді мекенді енгізіңіз")
city_input = st.text_input("Қала аты", placeholder="Shymkent / Алматы / Astana", value="Shymkent")

if not city_input.strip():
    st.stop()

# ====================== ДЕРЕКТЕРДІ АЛУ ======================
@st.cache_data(ttl=1800)
def fetch_weather_weatherapi(city: str, api_key: str):
    url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=7&aqi=yes&alerts=yes&lang=kk"
    for attempt in range(3):
        try:
            with st.spinner("🌤 Ауа райы деректері жүктелуде..."):
                resp = requests.get(url, timeout=15)
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            if attempt == 2:
                st.error(f"🌩️ WeatherAPI қатесі: {str(e)}")
                st.stop()
            time.sleep(5)
    st.stop()

weather_data = fetch_weather_weatherapi(city_input, weatherapi_key)

lat = weather_data["location"]["lat"]
lon = weather_data["location"]["lon"]

# ====================== ҚАЗІРГІ ЖАҒДАЙ ======================
current = weather_data["current"]
loc = weather_data["location"]

st.header(f"📊 Қазіргі жағдай — {loc['name']}, {loc['country']} ({current['last_updated']})")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("🌡️ Температура", f"{current['temp_c']}°C", f"Сезіледі: {current['feelslike_c']}°C")
with col2:
    st.metric("💧 Ылғалдылық", f"{current['humidity']}%")
with col3:
    st.metric("🌬️ Жел", f"{current['wind_kph']} км/сағ ({current['wind_dir']})")
with col4:
    st.metric("☁️ Бұлттылық", f"{current['cloud']}%")
with col5:
    st.metric("🌧️ Жаңбыр", f"{current.get('precip_mm', 0)} мм")

# ====================== AQI — ДҰРЫС СТАНДАРТ БОЙЫНША ======================
aqi = current.get('air_quality', {}).get('us-epa-index', 0)

if aqi <= 50:
    aqi_status = "✅ Жақсы"
    aqi_emoji = "🟢"
elif aqi <= 100:
    aqi_status = "🟡 Орташа"
    aqi_emoji = "🟡"
elif aqi <= 150:
    aqi_status = "🟠 Сезімтал топтарға зиянды"
    aqi_emoji = "🟠"
elif aqi <= 200:
    aqi_status = "🔴 Зиянды"
    aqi_emoji = "🔴"
elif aqi <= 300:
    aqi_status = "⚠️ Өте зиянды"
    aqi_emoji = "🔴"
else:
    aqi_status = "🚨 Қауіпті"
    aqi_emoji = "⚫"

st.metric("🌫️ AQI (US EPA)", f"{aqi} — {aqi_emoji} {aqi_status}")

# ====================== АЛДАҒЫ 24 САҒАТ ГРАФИГІ ======================
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

st.subheader("📈 Алдағы 24 сағаттағы температура өзгерісі")
fig = px.line(df_hourly.head(24), x="time", y="temp", 
              title="Температура (°C)", 
              labels={"temp": "Температура (°C)", "time": "Уақыт"})
fig.update_layout(height=400)
st.plotly_chart(fig, use_container_width=True)

# ====================== ЖИ ТАЛДАУЫ ======================
st.header("🧠 ЖИ (GPT-4o-mini) апат қаупін талдауы")

if not client:
    ai_analysis = "ЖИ талдауы қолжетімсіз (OpenAI кілті енгізілмеген)."
else:
    prompt = f"""
Сіз — тәжірибелі метеорологиялық сарапшысыз. Берілген деректер бойынша табиғи апат қаупін бағалаңыз (дауыл, су тасқыны, аптап ыстық, қатты жел, орман өрті).

Қала: {city_input}
Қазіргі температура: {current['temp_c']}°C
Ылғалдылық: {current['humidity']}%
Жел: {current['wind_kph']} км/сағ
Алдағы 24 сағаттағы орташа температура: {df_hourly.head(24)['temp'].mean():.1f}°C
Жаңбыр ықтималдығы (орташа): {df_hourly.head(24)['precip_prob'].mean():.1f}%

Қауіп деңгейін 0-100% аралығында есептеңіз. 60%-дан жоғары болса «ЖОҒАРЫ ҚАУІП» деп анық ескертіңіз.
Әр апат түріне қысқаша түсініктеме және ұсыныс беріңіз. Жауап **қазақ тілінде** болсын.
"""
    with st.spinner("🧠 ЖИ талдау жасап жатыр..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=900
        )
        ai_analysis = response.choices[0].message.content

st.markdown("### ЖИ-дың толық сараптамасы")
st.write(ai_analysis)

if client and ("жоғары қауіп" in ai_analysis.lower() or any(x in ai_analysis for x in ["60%", "70%", "80%", "90%"])):
    st.error("⚠️ ЖОҒАРЫ ҚАУІП! Алдын ала шаралар қабылдаңыз!")
else:
    st.success("✅ Қауіп деңгейі қалыпты.")

# ====================== 7 КҮНДІК БОЛЖАМ ======================
st.header("📅 7 күндік болжам")

daily_rows = []
for day in forecast:
    d = day["day"]
    daily_rows.append({
        "Күн": day["date"],
        "Макс. температура": f"{d['maxtemp_c']}°C",
        "Мин. температура": f"{d['mintemp_c']}°C",
        "Жаңбыр (мм)": f"{d['totalprecip_mm']} мм",
        "Жел макс (км/сағ)": f"{d['maxwind_kph']} км/сағ",
        "UV индексі": d["uv"]
    })

df_daily = pd.DataFrame(daily_rows)
st.dataframe(df_daily, use_container_width=True, hide_index=True)

# ====================== ИНТЕРАКТИВТІ WINDY КАРТАСЫ ======================
st.header("🗺️ Интерактивті Windy картасы")

st.markdown("**Қабатты таңдаңыз** — карта бірден жаңарады:")

overlay_dict = {
    "🌬️ Жел (Wind)": "wind",
    "🌧️ Жаңбыр (Rain)": "rain",
    "🌡️ Температура (Temperature)": "temp",
    "📡 Радар (Radar)": "radar",
    "☁️ Бұлттар (Clouds)": "clouds",
    "🌪️ Желдің күшеюі (Gust)": "gust",
    "❄️ Қар (Snow)": "snow",
    "💧 Ылғалдылық (Humidity)": "rh",
    "📉 Қысым (Pressure)": "pressure"
}

selected_label = st.selectbox("Ауа райы қабаты", options=list(overlay_dict.keys()), index=0)
selected_overlay = overlay_dict[selected_label]

windy_url = (
    f"https://embed.windy.com/embed2.html?"
    f"lat={lat}&lon={lon}&zoom=10&level=surface&overlay={selected_overlay}&"
    f"menu=&message=true&marker=true&calendar=now&pressure=true&"
    f"type=map&location=coordinates&detail=true&metricWind=km/h&metricTemp=C"
)

st.components.v1.iframe(src=windy_url, height=700, scrolling=True)

st.caption("💡 Кеңес: Тышқанмен жылжытыңыз, zoom жасаңыз. Қабатты ауыстырған сайын карта автоматты түрде жаңарады.")

# ====================== ФУТЕР ======================
st.markdown("---")
st.caption("Технологиялық стек: Streamlit • WeatherAPI.com • Windy.com • OpenAI GPT-4o-mini • Plotly")
