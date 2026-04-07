import streamlit as st
import pandas as pd
import requests
from openai import OpenAI
import plotly.express as px

# 1. БЕТТІҢ КОНФИГУРАЦИЯСЫ (UI ҚАБАТЫ)
st.set_page_config(page_title="Guardian AI Weather PRO", layout="wide")

st.title("🌍 Guardian AI Weather PRO")
st.markdown("### Табиғи апаттарды болжау және алдын алу жүйесі")

# Бүйірлік панель - Баптаулар
with st.sidebar:
    st.header("Баптаулар")
    api_key = st.text_input("OpenAI API Key енгізіңіз:", type="password")
    st.info("Технологиялар: Python, Streamlit, Pandas, OpenAI GPT-4o-mini")

# 2. ДЕРЕКТЕРДІ АЛУ ФУНКЦИЯЛАРЫ (API ҚАБАТЫ)
def get_coordinates(city):
    """Қала аты арқылы географиялық координаталарды анықтау"""
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
    response = requests.get(url).json()
    if "results" in response:
        return response["results"][0]
    return None

def get_weather_data(lat, lon):
    """Нақты уақыттағы метеорологиялық деректерді алу"""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,uv_index&timezone=auto"
    return requests.get(url).json()

def get_air_quality(lat, lon):
    """Ауа сапасын талдау (AQI)"""
    url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&hourly=european_aqi"
    return requests.get(url).json()

# 3. ЖАСАНДЫ ИНТЕЛЛЕКТ ТАЛДАУЫ (ИНТЕЛЛЕКТ ҚАБАТЫ)
def analyze_weather_ai(weather, aqi_val, city_name):
    if not api_key:
        return "ЖИ сараптамасы үшін OpenAI API кілтті енгізіңіз."
    
    client = OpenAI(api_key=api_key)
    prompt = f"""
    Қала: {city_name}. 
    Метеорологиялық деректер: Температура {weather['hourly']['temperature_2m'][0]}°C, 
    Жел жылдамдығы: {weather['hourly']['wind_speed_10m'][0]} км/сағ, 
    Ылғалдылық: {weather['hourly']['relative_humidity_2m'][0]}%,
    Ауа сапасы (AQI): {aqi_val}.
    Осы деректер негізінде табиғи апат қаупін (су тасқыны, өрт, дауыл) бағалап, қысқаша кеңес бер.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# 4. НЕГІЗГІ ПЛАТФОРМА ЛОГИКАСЫ
city_input = st.text_input("Қала атын енгізіңіз (мысалы: Shymkent, Almaty):")

if city_input:
    location = get_coordinates(city_input)
    
    if location:
        lat, lon = location['latitude'], location['longitude']
        st.success(f"Орын табылды: {location['name']}, {location.get('country', '')}")
        
        # Деректерді өңдеу (Processing Layer)
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
            # Ауа сапасының шартты логикасы
            status = "Жақсы" if aqi_val < 50 else "Орташа" if aqi_val < 100 else "Зиянды"
            st.metric("Ауа сапасы (AQI)", f"{aqi_val} ({status})")

        # Апат қаупін бағалау алгоритмі (Математикалық модель)
        st.subheader("⚠️ Қауіп деңгейін бағалау")
        risk_score = 0
        if weather['hourly']['wind_speed_10m'][0] > 50: risk_score += 40
        if weather['hourly']['temperature_2m'][0] > 35: risk_score += 30
        if weather['hourly']['precipitation'][0] > 10: risk_score += 30
        
        if risk_score >= 60:
            st.error(f"ЖОҒАРЫ ҚАУІП: {risk_score}% - Сақтық шараларын көріңіз!")
        else:
            st.info(f"Қауіп деңгейі төмен: {risk_score}%")

        # Визуализация (Plotly)
        df = pd.DataFrame({
            'Уақыт': weather['hourly']['time'][:24],
            'Температура (°C)': weather['hourly']['temperature_2m'][:24]
        })
        fig = px.line(df, x='Уақыт', y='Температура (°C)', title="24 сағаттық температура графигі")
        st.plotly_chart(fig, use_container_width=True)

        # ЖИ Сараптамасы
        st.subheader("🤖 Guardian AI Сараптамасы")
        if st.button("ЖИ болжамын алу"):
            with st.spinner("ЖИ деректерді талдауда..."):
                analysis = analyze_weather_ai(weather, aqi_val, location['name'])
                st.write(analysis)
        
        # Спутниктік карта (Windy API)
        st.subheader("Спутниктік жел картасы")
        windy_url = f"https://embed.windy.com/embed2.html?lat={lat}&lon={lon}&zoom=5&level=surface&overlay=wind"
        st.components.v1.iframe(windy_url, height=450)

    else:
        st.error("Қала табылмады. Қайта тексеріңіз.")

# 5. ҚОРЫТЫНДЫ (FOOTER)
st.divider()
st.caption("Әзірлеушілер: Арслан Өмен, Иманғали Құрбанбек. Жетекшісі: Н.Әсілбай")
        
