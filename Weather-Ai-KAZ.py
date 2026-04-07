import streamlit as st
import pandas as pd
import requests
from openai import OpenAI
import plotly.express as px
from datetime import datetime

# Беттің конфигурациясы
st.set_page_config(page_title="Guardian AI Weather PRO", layout="wide")

# --- 1. ПАЙДАЛАНУШЫ ИНТЕРФЕЙСІ (UI) ---
st.title("🌍 Guardian AI Weather PRO")
[span_3](start_span)st.markdown("### Табиғи апаттарды болжау және алдын алу жүйесі")[span_3](end_span)

# OpenAI API кілтін енгізу (бүйірлік панельде)
with st.sidebar:
    st.header("Баптаулар")
    api_key = st.text_input("OpenAI API Key енгізіңіз:", type="password")
    [span_4](start_span)language = st.selectbox("Тілді таңдаңыз:", ["Қазақша", "English", "Русский"])[span_4](end_span)
    [span_5](start_span)st.info("Бұл жүйе ЖИ мен математикалық модельдерді қолданады.")[span_5](end_span)

# --- 2. ДЕРЕКТЕРДІ АЛУ ФУНКЦИЯЛАРЫ (API) ---
def get_coordinates(city):
    [span_6](start_span)"""Қала аты арқылы координаталарды анықтау[span_6](end_span)"""
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
    response = requests.get(url).json()
    if "results" in response:
        return response["results"][0]
    return None

def get_weather_data(lat, lon):
    [span_7](start_span)[span_8](start_span)"""Ауа райы және апат қаупі деректерін алу[span_7](end_span)[span_8](end_span)"""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,uv_index&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
    return requests.get(url).json()

def get_air_quality(lat, lon):
    [span_9](start_span)"""Ауа сапасын талдау[span_9](end_span)"""
    url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&hourly=european_aqi"
    return requests.get(url).json()

# --- 3. ЖАСАНДЫ ИНТЕЛЛЕКТ ТАЛДАУЫ (LLM) ---
def analyze_weather_ai(data, aqi_val, city_name):
    [span_10](start_span)"""OpenAI GPT-4o-mini арқылы сараптама жасау[span_10](end_span)"""
    if not api_key:
        return "ЖИ сараптамасы үшін API кілтті енгізіңіз."
    
    client = OpenAI(api_key=api_key)
    prompt = f"""
    Қала: {city_name}. 
    Метеорологиялық деректер: Температура {data['hourly']['temperature_2m'][0]}°C, 
    Жел жылдамдығы: {data['hourly']['wind_speed_10m'][0]} км/сағ, 
    Ылғалдылық: {data['hourly']['relative_humidity_2m'][0]}%,
    Ауа сапасы (AQI): {aqi_val}.
    [span_11](start_span)[span_12](start_span)Осы деректер негізінде табиғи апат қаупін (су тасқыны, өрт, дауыл) бағалап, қысқаша кеңес бер.[span_11](end_span)[span_12](end_span)
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# --- 4. НЕГІЗГІ ЛОГИКА ---
city_input = st.text_input("Қала атын енгізіңіз (мысалы: Shymkent, Almaty):")

if city_input:
    location = get_coordinates(city_input)
    
    if location:
        lat, lon = location['latitude'], location['longitude']
        [span_13](start_span)st.success(f"Орын табылды: {location['name']}, {location.get('country', '')}")[span_13](end_span)
        
        # Деректерді жүктеу
        weather = get_weather_data(lat, lon)
        aqi_data = get_air_quality(lat, lon)
        aqi_val = aqi_data['hourly']['european_aqi'][0]
        
        # Визуалды блоктар
        col1, col2, col3 = st.columns(3)
        
        with col1:
            temp = weather['hourly']['temperature_2m'][0]
            st.metric("Температура", f"{temp}°C")
            
        with col2:
            wind = weather['hourly']['wind_speed_10m'][0]
            [span_14](start_span)st.metric("Жел жылдамдығы", f"{wind} км/сағ")[span_14](end_span)
            
        with col3:
            # [span_15](start_span)Ауа сапасының логикасы[span_15](end_span)
            status = "Жақсы" if aqi_val < 50 else "Орташа" if aqi_val < 100 else "Зиянды"
            st.metric("Ауа сапасы (AQI)", f"{aqi_val} ({status})")

        # --- 5. АПАТ ҚАУПІН БАҒАЛАУ (МАТЕМАТИКАЛЫҚ ЛОГИКА) ---
        st.subheader("⚠️ Қауіп деңгейін бағалау")
        risk_score = 0
        if wind > 50: risk_score += 40  # Дауыл қаупі
        if temp > 35: risk_score += 30  # Аптап ыстық/Өрт қаупі
        if weather['hourly']['precipitation'][0] > 10: risk_score += 30 # Су тасқыны қаупі
        
        if risk_score >= 60:
            [span_16](start_span)st.error(f"ЖОҒАРЫ ҚАУІП: {risk_score}% - Сақтық шараларын көріңіз!")[span_16](end_span)
        else:
            st.info(f"Қауіп деңгейі төмен: {risk_score}%")

        # [span_17](start_span)Графиктер[span_17](end_span)
        st.subheader("7 күндік болжам")
        df = pd.DataFrame({
            'Уақыт': weather['hourly']['time'][:168],
            'Температура (°C)': weather['hourly']['temperature_2m'][:168]
        })
        [span_18](start_span)fig = px.line(df, x='Уақыт', y='Температура (°C)', title="Температура тренді")[span_18](end_span)
        st.plotly_chart(fig, use_container_width=True)

        # ЖИ Сараптамасы
        st.subheader("🤖 Guardian AI Сараптамасы")
        if st.button("ЖИ болжамын алу"):
            with st.spinner("ЖИ деректерді талдауда..."):
                analysis = analyze_weather_ai(weather, aqi_val, location['name'])
                [span_19](start_span)[span_20](start_span)st.write(analysis)[span_19](end_span)[span_20](end_span)
        
        # [span_21](start_span)Windy картасын интеграциялау[span_21](end_span)
        st.subheader("Спутниктік жел картасы")
        windy_url = f"https://embed.windy.com/embed2.html?lat={lat}&lon={lon}&zoom=5&level=surface&overlay=wind"
        [span_22](start_span)st.components.v1.iframe(windy_url, height=400)[span_22](end_span)

    else:
        st.error("Қала табылмады. Қайта тексеріңіз.")

# --- 6. ТӨМЕНГІ БӨЛІМ (FOOTER) ---
st.divider()
[span_23](start_span)[span_24](start_span)st.caption("Әзірлеушілер: Арслан Өмен, Иманғали Құрбанбек. Жетекшісі: Н.Әсілбай")[span_23](end_span)[span_24](end_span)
            
