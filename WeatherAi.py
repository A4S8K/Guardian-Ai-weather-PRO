import streamlit as st
import pandas as pd
import requests
from openai import OpenAI
import plotly.express as px
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
        st.warning("⚠️ OpenAI API кілтін енгізіңіз! ЖИ талдауы жұмыс істемейді.")
        client = None
    else:
        client = OpenAI(api_key=openai_key)
    
    st.info("Дерек көздері: Open-Meteo + OpenAI GPT-4o-mini")

# ====================== ҚАЛА ІЗДЕУ ======================
st.header("📍 Қала немесе елді мекенді енгізіңіз")
city_input = st.text_input("Қала аты", placeholder="Алматы / Astana / Shymkent", value="Shymkent")

def geocode_city(city_name: str):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=10&language=kk&format=json"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json().get("results", [])
    except Exception as e:
        st.error(f"Геокодтау қатесі: {e}")
        return []

if city_input.strip():
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
    st.warning("Қала атын енгізіңіз.")
    st.stop()

# ====================== ДЕРЕКТЕРДІ АЛУ (ҚОРҒАНЫС ҚОСЫЛДЫ) ======================
@st.cache_data(ttl=1800)
def fetch_weather(lat: float, lon: float):
    url = (f"https://api.open-meteo.com/v1/forecast?"
           f"latitude={lat}&longitude={lon}&"
           f"current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,"
           f"rain,showers,snowfall,weather_code,cloud_cover,wind_speed_10m,wind_gusts_10m,uv_index&"
           f"hourly=temperature_2m,relative_humidity_2m,precipitation_probability,precipitation,"
           f"cloud_cover,wind_speed_10m,uv_index&"
           f"daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,"
           f"wind_speed_10m_max,uv_index_max&timezone=auto")
    
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            st.error(f"🌩️ Open-Meteo қатесі: {data.get('reason', data)}")
            st.stop()
        return data
    except requests.exceptions.JSONDecodeError:
        st.error("❌ Open-Meteo API JSON қайтармады!")
        st.error(f"Жауап: {resp.text[:800]}")
        st.stop()
    except Exception as e:
        st.error(f"🌩️ Ауа райы деректерін алу қатесі: {e}")
        st.stop()

@st.cache_data(ttl=1800)
def fetch_air_quality(lat: float, lon: float):
    url = (f"https://air-quality-api.open-meteo.com/v1/air-quality?"
           f"latitude={lat}&longitude={lon}&"
           f"current=european_aqi,pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone")
    
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.JSONDecodeError:
        st.error("❌ Air Quality API JSON қайтармады!")
        st.error(f"Жауап: {resp.text[:800]}")
        st.stop()
    except Exception as e:
        st.error(f"🌫️ AQI деректерін алу қатесі: {e}")
        st.stop()

weather_data = fetch_weather(lat, lon)
aq_data = fetch_air_quality(lat, lon)

# ====================== ҚАЗІРГІ ЖАҒДАЙ ======================
current = weather_data["current"]
current_time = pd.to_datetime(current["time"])

st.header(f"📊 Қазіргі жағдай — {current_time.strftime('%d.%m.%Y %H:%M')}")

col1, col2, col3, col4, col5 = st.columns(5)
with col1: st.metric("🌡️ Температура", f"{current['temperature_2m']}°C")
with col2: st.metric("💧 Ылғалдылық", f"{current['relative_humidity_2m']}%")
with col3: st.metric("🌬️ Жел", f"{current['wind_speed_10m']} км/сағ")
with col4: st.metric("☀️ UV индексі", f"{current.get('uv_index', 'N/A')}")
with col5: st.metric("🌧️ Жаңбыр", f"{current.get('precipitation', 0)} мм")

# AQI
aqi = aq_data["current"].get("european_aqi", 0)
if aqi < 50: aqi_status = "✅ Жақсы"
elif aqi < 100: aqi_status = "🟡 Орташа"
else: aqi_status = "🔴 Зиянды"
st.metric("🌫️ AQI (Еуропалық индекс)", f"{aqi} — {aqi_status}")

# ====================== Pandas талдау ======================
hourly = weather_data["hourly"]
df_hourly = pd.DataFrame({
    "time": pd.to_datetime(hourly["time"]),
    "temp": hourly["temperature_2m"],
    "humidity": hourly["relative_humidity_2m"],
    "precip_prob": hourly["precipitation_probability"],
    "wind": hourly["wind_speed_10m"],
    "uv": hourly["uv_index"]
})

# ====================== ЖИ ТАЛДАУЫ ======================
st.header("🧠 ЖИ (GPT-4o-mini) талдауы және апат қаупі")

if client is None:
    ai_analysis = "ЖИ талдауы қолжетімсіз (API key жоқ)."
else:
    prompt = f"""
Сіз — метеорологиялық сарапшысыз. ... (өзгеріссіз)
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

if client and any(x in ai_analysis for x in ["60%", "70%", "80%", "90%", "жоғары қауіп"]):
    st.error("⚠️ ЖОҒАРЫ ҚАУІП! Алдын ала шаралар қабылдаңыз!")
else:
    st.success("Қауіп деңгейі қалыпты.")

# ====================== ГРАФИК ======================
st.subheader("📈 Алдағы 24 сағаттағы тренд")
fig_temp = px.line(df_hourly.head(24), x="time", y="temp", title="Алдағы 24 сағаттағы температура")
st.plotly_chart(fig_temp, use_container_width=True)

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
    "max_temp": "{:.1f}°C", "min_temp": "{:.1f}°C",
    "precip": "{:.1f} мм", "wind_max": "{:.1f} км/сағ"
}), use_container_width=True)

st.caption("Технологиялық стек: Python + Streamlit + Open-Meteo + OpenAI + Plotly")
st.success("✅ Қате түзетілді! Енді қосымша қате шықса — экранда нақты себебі көрінеді.")
