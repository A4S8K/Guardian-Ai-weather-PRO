import streamlit as st
import pandas as pd
import requests
from openai import OpenAI
import plotly.express as px

# 1. ТІЛДЕР СӨЗДІГІ (Локализация)
lang_dict = {
    "kk": {
        "title": "🌍 Guardian AI Weather PRO",
        "subtitle": "Табиғи апаттарды болжау жүйесі",
        "city_label": "Қала атын қазақша енгізіңіз (мысалы: Шымкент, Астана):",
        "temp": "Температура",
        "wind": "Жел жылдамдығы",
        "precip": "Жауын-шашын",
        "risk_lvl": "Қауіп деңгейін бағалау",
        "ai_btn": "ЖИ сараптамасын алу",
        "high_risk": "ЖОҒАРЫ ҚАУІП",
        "low_risk": "Қауіп деңгейі төмен",
        "error": "Деректер табылмады немесе қате енгізілді",
        "api_lang": "kk",
        "team": "Әзірлеушілер: Арслан Өмен, Иманғали Құрбанбек. Жетекшісі: Н.Әсілбай"
    },
    "ru": {
        "title": "🌍 Guardian AI Weather PRO",
        "subtitle": "Система прогнозирования стихийных бедствий",
        "city_label": "Введите название города на русском (например: Алматы, Москва):",
        "temp": "Температура",
        "wind": "Скорость ветра",
        "precip": "Осадки",
        "risk_lvl": "Оценка уровня риска",
        "ai_btn": "Получить анализ ИИ",
        "high_risk": "ВЫСОКИЙ РИСК",
        "low_risk": "Уровень риска низкий",
        "error": "Данные не найдены или ошибка ввода",
        "api_lang": "ru",
        "team": "Разработчики: Арслан Омен, Имангали Курбанбек. Руководитель: Н.Асильбай"
    },
    "en": {
        "title": "🌍 Guardian AI Weather PRO",
        "subtitle": "Disaster Prediction System",
        "city_label": "Enter city name in English (e.g., London, New York):",
        "temp": "Temperature",
        "wind": "Wind Speed",
        "precip": "Precipitation",
        "risk_lvl": "Risk Level Assessment",
        "ai_btn": "Get AI Analysis",
        "high_risk": "HIGH RISK",
        "low_risk": "Risk level is low",
        "error": "Data not found or input error",
        "api_lang": "en",
        "team": "Developers: Arslan Omen, Imangali Kurbanbek. Supervisor: N.Asilbay"
    }
}

# 2. ПЛАТФОРМА КОНФИГУРАЦИЯСЫ
st.set_page_config(page_title="Guardian AI Weather PRO", layout="wide")

with st.sidebar:
    st.header("Language / Тіл / Язык")
    sel_lang = st.selectbox("", ["Қазақша", "Русский", "English"])
    # Тіл кодын анықтау
    if sel_lang == "Қазақша":
        lang_code = "kk"
    elif sel_lang == "Русский":
        lang_code = "ru"
    else:
        lang_code = "en"
    
    st.divider()
    api_key = st.text_input("OpenAI API Key:", type="password")

t = lang_dict[lang_code]

st.title(t["title"])
st.markdown(f"### {t['subtitle']}")

# 3. API ФУНКЦИЯЛАРЫ
def get_coords(city, lang):
    """Қаланы таңдалған тілде іздеу (kk, ru, en)"""
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language={lang}&format=json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['results'][0] if 'results' in data else None
    except:
        return None

def get_weather(lat, lon):
    """Ауа райы деректерін алу"""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation,wind_speed_10m&timezone=auto"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except:
        return None

# 4. НЕГІЗГІ ЛОГИКА
city_query = st.text_input(t["city_label"])

if city_query:
    # Іздеуді таңдалған тіл бойынша жүргізу
    location = get_coords(city_query, t["api_lang"])
    
    if location:
        st.success(f"📍 {location['name']}, {location.get('country', '')}")
        weather_data = get_weather(location['latitude'], location['longitude'])
        
        if weather_data:
            # Қазіргі көрсеткіштер
            curr_temp = weather_data['hourly']['temperature_2m'][0]
            curr_wind = weather_data['hourly']['wind_speed_10m'][0]
            curr_prec = weather_data['hourly']['precipitation'][0]

            col1, col2, col3 = st.columns(3)
            col1.metric(t["temp"], f"{curr_temp}°C")
            col2.metric(t["wind"], f"{curr_wind} km/h")
            col3.metric(t["precip"], f"{curr_prec} mm")

            # Апат қаупін бағалау (Құжаттағы алгоритм: 60% шегі)
            st.subheader(t["risk_lvl"])
            risk_score = 0
            if curr_wind > 50: risk_score += 40
            if curr_temp > 35: risk_score += 30
            if curr_prec > 10: risk_score += 30
            
            if risk_score >= 60:
                st.error(f"{t['high_risk']}: {risk_score}%")
            else:
                st.info(f"{t['low_risk']}: {risk_score}%")

            # График
            df = pd.DataFrame({
                'Time': weather_data['hourly']['time'][:24],
                'Temperature': weather_data['hourly']['temperature_2m'][:24]
            })
            fig = px.line(df, x='Time', y='Temperature', title="24h Forecast")
            st.plotly_chart(fig, use_container_width=True)

            # ЖИ Сараптамасы (OpenAI)
            st.subheader("🤖 AI Analysis")
            if st.button(t["ai_btn"]):
                if api_key:
                    try:
                        client = OpenAI(api_key=api_key)
                        prompt = f"Analyze disaster risk for {location['name']}. Current: Temp {curr_temp}C, Wind {curr_wind}km/h, Rain {curr_prec}mm. Respond in {sel_lang} language."
                        res = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": prompt}]
                        )
                        st.write(res.choices[0].message.content)
                    except Exception as e:
                        st.error(f"AI Error: {e}")
                else:
                    st.warning("Please enter OpenAI API Key in the sidebar.")
    else:
        st.error(t["error"])

# 5. ҚОРЫТЫНДЫ
st.divider()
st.caption(t["team"])
