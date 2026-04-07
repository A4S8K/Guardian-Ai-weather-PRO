import streamlit as st
import pandas as pd
import requests
from openai import OpenAI
import plotly.express as px

# 1. ТІЛДЕРГЕ АРНАЛҒАН СӨЗДІК
lang_dict = {
    "kk": {
        "title": "🌍 Guardian AI Weather PRO",
        "subtitle": "Табиғи апаттарды болжау және алдын алу жүйесі",
        "settings": "Баптаулар",
        "city_label": "Қала атын енгізіңіз (мысалы: Shymkent):",
        "temp": "Температура",
        "wind": "Жел жылдамдығы",
        "aqi": "Ауа сапасы",
        "risk_lvl": "Қауіп деңгейін бағалау",
        "high_risk": "ЖОҒАРЫ ҚАУІП",
        "low_risk": "Қауіп деңгейі төмен",
        "ai_btn": "ЖИ болжамын алу",
        "found": "Орын табылды",
        "not_found": "Қала табылмады немесе API қатесі",
        "error_api": "Деректерді алу мүмкін болмады (API қатесі)."
    },
    "ru": {
        "title": "🌍 Guardian AI Weather PRO",
        "subtitle": "Система прогнозирования и предотвращения стихийных бедствий",
        "settings": "Настройки",
        "city_label": "Введите название города (например: Almaty):",
        "temp": "Температура",
        "wind": "Скорость ветра",
        "aqi": "Качество воздуха",
        "risk_lvl": "Оценка уровня риска",
        "high_risk": "ВЫСОКИЙ РИСК",
        "low_risk": "Уровень риска низкий",
        "ai_btn": "Получить прогноз ИИ",
        "found": "Место найдено",
        "not_found": "Город не найден или ошибка API",
        "error_api": "Не удалось получить данные (Ошибка API)."
    },
    "en": {
        "title": "🌍 Guardian AI Weather PRO",
        "subtitle": "Natural Disaster Prediction and Prevention System",
        "settings": "Settings",
        "city_label": "Enter city name (e.g., London):",
        "temp": "Temperature",
        "wind": "Wind Speed",
        "aqi": "Air Quality",
        "risk_lvl": "Risk Level Assessment",
        "high_risk": "HIGH RISK",
        "low_risk": "Risk level is low",
        "ai_btn": "Get AI Forecast",
        "found": "Location found",
        "not_found": "City not found or API error",
        "error_api": "Could not retrieve data (API Error)."
    }
}

# 2. БЕТТІҢ КОНФИГУРАЦИЯСЫ
st.set_page_config(page_title="Guardian AI Weather PRO", layout="wide")

# Тілді таңдау
with st.sidebar:
    st.header("Language / Тіл / Язык")
    sel_lang = st.selectbox("", ["Қазақша", "Русский", "English"])
    lang_code = "kk" if sel_lang == "Қазақша" else "ru" if sel_lang == "Русский" else "en"
    
    st.header(lang_dict[lang_code]["settings"])
    api_key = st.text_input("OpenAI API Key:", type="password")

t = lang_dict[lang_code]

st.title(t["title"])
st.markdown(f"### {t['subtitle']}")

# 3. ҚАТЕЛЕРДІ ӨҢДЕЙТІН API ФУНКЦИЯЛАРЫ
def get_weather_data(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m&timezone=auto"
    try:
        response = requests.get(url)
        response.raise_for_status() # Статус кодын тексереді (404, 500 т.б.)
        return response.json()
    except Exception as e:
        st.error(f"{t['error_api']}: {e}")
        return None

def get_coordinates(city):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&format=json"
    try:
        res = requests.get(url).json()
        return res['results'][0] if 'results' in res else None
    except: return None

# 4. НЕГІЗГІ ЛОГИКА
city_input = st.text_input(t["city_label"])

if city_input:
    location = get_coordinates(city_input)
    if location:
        lat, lon = location['latitude'], location['longitude']
        weather = get_weather_data(lat, lon)
        
        if weather:
            st.success(f"{t['found']}: {location['name']}")
            
            # Көрсеткіштер
            c1, c2 = st.columns(2)
            curr_temp = weather['hourly']['temperature_2m'][0]
            curr_wind = weather['hourly']['wind_speed_10m'][0]
            
            c1.metric(t["temp"], f"{curr_temp}°C")
            c2.metric(t["wind"], f"{curr_wind} km/h")

            # [span_0](start_span)Апат қаупін бағалау (Құжаттағы логика бойынша[span_0](end_span))
            st.subheader(t["risk_lvl"])
            risk = 0
            if curr_wind > 50: risk += 40
            if curr_temp > 35: risk += 30
            if weather['hourly']['precipitation'][0] > 10: risk += 30
            
            if risk >= 60:
                st.error(f"{t['high_risk']}: {risk}%")
            else:
                st.info(f"{t['low_risk']}: {risk}%")

            # График
            df = pd.DataFrame({
                'Time': weather['hourly']['time'][:24],
                'Temp': weather['hourly']['temperature_2m'][:24]
            })
            st.plotly_chart(px.line(df, x='Time', y='Temp'))

            # [span_1](start_span)[span_2](start_span)ЖИ болжамы (GPT-4o-mini қолдану[span_1](end_span)[span_2](end_span))
            if st.button(t["ai_btn"]):
                if api_key:
                    client = OpenAI(api_key=api_key)
                    prompt = f"Analyze weather for {location['name']}: Temp {curr_temp}C, Wind {curr_wind}km/h. Provide disaster risk in {sel_lang}."
                    res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":prompt}])
                    st.write(res.choices[0].message.content)
                else:
                    st.warning("Please enter API Key")
    else:
        st.error(t["not_found"])

st.divider()
[span_3](start_span)st.caption("Guardian AI Weather PRO - Team: Arslan Omen, Imangali Kurbanbek[span_3](end_span)")
