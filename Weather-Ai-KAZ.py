import streamlit as st
import pandas as pd
import requests
from openai import OpenAI
import plotly.express as px

# 1. БЕТТІҢ КОНФИГУРАЦИЯСЫ (Guardian AI Weather PRO)
st.set_page_config(page_title="Guardian AI Weather PRO", layout="wide")

# [span_1](start_span)Жоба тақырыбы және сипаттамасы[span_1](end_span)
st.title("🌍 Guardian AI Weather PRO")
st.markdown("### Табиғи апаттарды болжау және алдын алу жүйесі")

# [span_2](start_span)Бүйірлік панель - Баптаулар мен Технологиялық стек[span_2](end_span)
with st.sidebar:
    st.header("Баптаулар")
    api_key = st.text_input("OpenAI API Key енгізіңіз:", type="password")
    st.info("Технологиялар: Python, Streamlit, Pandas, OpenAI GPT-4o-mini")

# 2. [span_3](start_span)[span_4](start_span)ДЕРЕКТЕРДІ АЛУ ФУНКЦИЯЛАРЫ (Open-Meteo API)[span_3](end_span)[span_4](end_span)
def get_coordinates(city):
    [span_5](start_span)"""Қала аты арқылы координаталарды анықтау[span_5](end_span)"""
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
    response = requests.get(url).json()
    if "results" in response:
        return response["results"][0]
    return None

def get_weather_data(lat, lon):
    [span_6](start_span)[span_7](start_span)"""Ауа райы деректерін алу[span_6](end_span)[span_7](end_span)"""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,uv_index&timezone=auto"
    return requests.get(url).json()

def get_air_quality(lat, lon):
    [span_8](start_span)"""Ауа сапасын талдау (AQI)[span_8](end_span)"""
    url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&hourly=european_aqi"
    return requests.get(url).json()

# 3. [span_9](start_span)[span_10](start_span)ЖАСАНДЫ ИНТЕЛЛЕКТ ТАЛДАУЫ (OpenAI GPT-4o-mini)[span_9](end_span)[span_10](end_span)
def analyze_weather_ai(data, aqi_val, city_name):
    if not api_key:
        return "ЖИ сараптамасы үшін OpenAI API кілтті енгізіңіз."
    
    client = OpenAI(api_key=api_key)
    prompt = f"""
    Қала: {city_name}. 
    Метеорологиялық деректер: Температура {data['hourly']['temperature_2m'][0]}°C, 
    Жел жылдамдығы: {data['hourly']['wind_speed_10m'][0]} км/сағ, 
    Ылғалдылық: {data['hourly']['relative_humidity_2m'][0]}%,
    Ауа сапасы (AQI): {aqi_val}.
    Осы деректер негізінде табиғи апат қаупін (су тасқыны, өрт, дауыл) бағалап, қысқаша кеңес бер.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# 4. [span_11](start_span)[span_12](start_span)НЕГІЗГІ ЛОГИКА ЖӘНЕ ПЛАТФОРМА[span_11](end_span)[span_12](end_span)
city_input = st.text_input("Қала атын енгізіңіз (мысалы: Shymkent, Almaty):")

if city_input:
    location = get_coordinates(city_input)
    
    if location:
        lat, lon = location['latitude'], location['longitude']
        st.success(f"Орын табылды: {location['name']}, {location.get('country', '')}")
        
        # [span_13](start_span)Деректерді өңдеу (Processing Layer)[span_13](end_span)
        weather = get_weather_data(lat, lon)
        aqi_data = get_air_quality(lat, lon)
        aqi_val = aqi_data['hourly']['european_aqi'][0]
        
        # Визуалды көрсеткіштер
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Температура", f"{weather['hourly']['temperature_2m'][0]}°C")
        with col2:
            st.metric("Жел жылдамдығы", f"{weather['hourly']['wind_speed_10m'][0]} км/сағ")
        with col3:
            # [span_14](start_span)Ауа сапасының логикасы[span_14](end_span)
            status = "Жақсы" if aqi_val < 50 else "Орташа" if aqi_val < 100 else "Зиянды"
            st.metric("Ауа сапасы (AQI)", f"{aqi_val} ({status})")

        # [span_15](start_span)Апат қаупін бағалау алгоритмі (Математикалық модель)[span_15](end_span)
        st.subheader("⚠️ Қауіп деңгейін бағалау")
        risk_score = 0
        if weather['hourly']['wind_speed_10m'][0] > 50: risk_score += 40
        if weather['hourly']['temperature_2m'][0] > 35: risk_score += 30
        if weather['hourly']['precipitation'][0] > 10: risk_score += 30
        
        if risk_score >= 60:
            [span_16](start_span)st.error(f"ЖОҒАРЫ ҚАУІП: {risk_score}% - Сақтық шараларын көріңіз[span_16](end_span)!")
        else:
            st.info(f"Қауіп деңгейі төмен: {risk_score}%")

        # [span_17](start_span)Графиктер (Visualisation)[span_17](end_span)
        df = pd.DataFrame({
            'Уақыт': weather['hourly']['time'][:24],
            'Температура (°C)': weather['hourly']['temperature_2m'][:24]
        })
        fig = px.line(df, x='Уақыт', y='Температура (°C)', title="24 сағаттық температура болжамы")
        st.plotly_chart(fig, use_container_width=True)

        # [span_18](start_span)[span_19](start_span)ЖИ Сараптамасы[span_18](end_span)[span_19](end_span)
        st.subheader("🤖 ЖИ Сараптамасы")
        if st.button("ЖИ болжамын алу"):
            with st.spinner("ЖИ деректерді талдауда..."):
                analysis = analyze_weather_ai(weather, aqi_val, location['name'])
                st.write(analysis)
        
        # [span_20](start_span)[span_21](start_span)Спутниктік карта (Windy API интеграциясы)[span_20](end_span)[span_21](end_span)
        st.subheader("Спутниктік жел картасы")
        windy_url = f"https://embed.windy.com/embed2.html?lat={lat}&lon={lon}&zoom=5&level=surface&overlay=wind"
        st.components.v1.iframe(windy_url, height=400)

    else:
        st.error("Қала табылмады. Қайта тексеріңіз.")

# 5. [span_22](start_span)[span_23](start_span)ҚОРЫТЫНДЫ[span_22](end_span)[span_23](end_span)
st.divider()
[span_24](start_span)[span_25](start_span)st.caption("Әзірлеушілер: Арслан Өмен, Иманғали Құрбанбек. Жетекшісі: Н.Әсілбай[span_24](end_span)[span_25](end_span)")
        
