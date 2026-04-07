import streamlit as st
import pandas as pd
import requests
from openai import OpenAI
import plotly.express as px

# 1. ТІЛДЕР СӨЗДІГІ
lang_dict = {
    "kk": {
        "title": "🌍 Guardian AI Weather PRO",
        "subtitle": "Табиғи апаттарды болжау жүйесі",
        "city_label": "Қала атын қазақша енгізіңіз (мысалы: Алматы):",
        "temp": "Температура",
        "wind": "Жел жылдамдығы",
        "precip": "Жауын-шашын",
        "risk_lvl": "Қауіп деңгейі",
        "ai_btn": "ЖИ сараптамасын алу",
        "high_risk": "ЖОҒАРЫ ҚАУІП",
        "low_risk": "Қауіп төмен",
        "error": "Деректер табылмады",
        "api_lang": "kk",
        [span_4](start_span)"team": "Әзірлеушілер: Арслан Өмен, Иманғали Құрбанбек[span_4](end_span)"
    },
    "ru": {
        "title": "🌍 Guardian AI Weather PRO",
        "subtitle": "Система прогнозирования стихийных бедствий",
        "city_label": "Введите название города на русском (например: Шымкент):",
        "temp": "Температура",
        "wind": "Скорость ветра",
        "precip": "Осадки",
        "risk_lvl": "Уровень риска",
        "ai_btn": "Получить анализ ИИ",
        "high_risk": "ВЫСОКИЙ РИСК",
        "low_risk": "Риск низкий",
        "error": "Данные не найдены",
        "api_lang": "ru",
        [span_5](start_span)"team": "Разработчики: Арслан Омен, Имангали Курбанбек[span_5](end_span)"
    },
    "en": {
        "title": "🌍 Guardian AI Weather PRO",
        "subtitle": "Disaster Prediction System",
        "city_label": "Enter city name in English (e.g., Astana):",
        "temp": "Temperature",
        "wind": "Wind Speed",
        "precip": "Precipitation",
        "risk_lvl": "Risk Level",
        "ai_btn": "Get AI Analysis",
        "high_risk": "HIGH RISK",
        "low_risk": "Low Risk",
        "error": "Data not found",
        "api_lang": "en",
        [span_6](start_span)"team": "Developers: Arslan Omen, Imangali Kurbanbek[span_6](end_span)"
    }
}

st.set_page_config(page_title="Guardian AI Weather PRO", layout="wide")

# Тілді таңдау интерфейсі
with st.sidebar:
    st.header("Settings / Баптаулар")
    sel_lang = st.selectbox("Language / Тіл", ["Қазақша", "Русский", "English"])
    lang_code = "kk" if sel_lang == "Қазақша" else "ru" if sel_lang == "Русский" else "en"
    api_key = st.text_input("OpenAI API Key:", type="password")

t = lang_dict[lang_code]

st.title(t["title"])
st.markdown(f"**{t['subtitle']}**")

# 2. ГЕОЛОКАЦИЯ (Тілге байланысты іздеу)
def get_coords(city, lang):
    # [span_7](start_span)language параметрі қаланы сол тілде іздеуге мүмкіндік береді[span_7](end_span)
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language={lang}&format=json"
    try:
        res = requests.get(url).json()
        return res['results'][0] if 'results' in res else None
    except: return None

# 3. АУА РАЙЫ ДЕРЕКТЕРІ
def get_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation,wind_speed_10m&timezone=auto"
    try:
        return requests.get(url).json()
    except: return None

# Платформа жұмысы
city_query = st.text_input(t["city_label"])

if city_query:
    location = get_coords(city_query, t["api_lang"])
    
    if location:
        st.success(f"📍 {location['name']}, {location.get('country', '')}")
        data = get_weather(location['latitude'], location['longitude'])
        
        if data:
            curr_temp = data['hourly']['temperature_2m'][0]
            curr_wind = data['hourly']['wind_speed_10m'][0]
            curr_prec = data['hourly']['precipitation'][0]

            # Метрикалар
            c1, c2, c3 = st.columns(3)
            c1.metric(t["temp"], f"{curr_temp}°C")
            c2.metric(t["wind"], f"{curr_wind} km/h")
            c3.metric(t["precip"], f"{curr_prec} mm")

            # [span_8](start_span)Апат қаупін есептеу (60% логикасы)[span_8](end_span)
            st.subheader(t["risk_lvl"])
            risk = 0
            if curr_wind > 50: risk += 40
            if curr_temp > 35: risk += 30
            if curr_prec > 10: risk += 30
            
            if risk >= 60:
                st.error(f"{t['high_risk']}: {risk}%")
            else:
                st.info(f"{t['low_risk']}: {risk}%")

            # [span_9](start_span)[span_10](start_span)ЖИ Сараптамасы[span_9](end_span)[span_10](end_span)
            if st.button(t["ai_btn"]):
                if api_key:
                    client = OpenAI(api_key=api_key)
                    prompt = f"Analyze disaster risk for {location['name']}: Temp {curr_temp}C, Wind {curr_wind}km/h. Respond in {sel_lang}."
                    response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":prompt}])
                    st.write(response.choices[0].message.content)
                else:
                    st.warning("API Key қажет")
    else:
        st.error(t["error"])

st.divider()
st.caption(t["team"])
                    
