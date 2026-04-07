import streamlit as st
import pandas as pd
import requests
from openai import OpenAI
import plotly.express as px

# 1. КӨП ТІЛДІЛІК СӨЗДІГІ (Multi-language support)
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
        "error_api": "Деректерді алу мүмкін болмады (API қатесі)",
        "team": "Әзірлеушілер: Арслан Өмен, Иманғали Құрбанбек. Жетекшісі: Н.Әсілбай"
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
        "error_api": "Не удалось получить данные (Ошибка API)",
        "team": "Разработчики: Арслан Омен, Имангали Курбанбек. Руководитель: Н.Асильбай"
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
        "error_api": "Could not retrieve data (API Error)",
        "team": "Developers: Arslan Omen, Imangali Kurbanbek. Supervisor: N.Asilbay"
    }
}

# 2. ПЛАТФОРМА БАПТАУЛАРЫ
st.set_page_config(page_title="Guardian AI Weather PRO", layout="wide")

with st.sidebar:
    st.header("Language / Тіл / Язык")
    sel_lang = st.selectbox("", ["Қазақша", "Русский", "English"])
    lang_code = "kk" if sel_lang == "Қазақша" else "ru" if sel_lang == "Русский" else "en"
    
    st.header(lang_dict[lang_code]["settings"])
    api_key = st.text_input("OpenAI API Key:", type="password")

t = lang_dict[lang_code]

st.title(t["title"])
st.markdown(f"### {t['subtitle']}")

# 3. API ФУНКЦИЯЛАРЫ (Қателерді өңдеумен)
def get_coordinates(city):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&format=json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['results'][0] if 'results' in data else None
    except:
        return None

def get_weather_data(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m&timezone=auto"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"{t['error_api']}: {e}")
        return None

# 4. НЕГІЗГІ ЖҰМЫС ЦИКЛІ
city_input = st.text_input(t["city_label"])

if city_input:
    location = get_coordinates(city_input)
    if location:
        lat, lon = location['latitude'], location['longitude']
        weather = get_weather_data(lat, lon)
        
        if weather:
            st.success(f"{t['found']}: {location['name']}, {location.get('country', '')}")
            
            # Метрикалар
            col1, col2 = st.columns(2)
            curr_temp = weather['hourly']['temperature_2m'][0]
            curr_wind = weather['hourly']['wind_speed_10m'][0]
            curr_prec = weather['hourly']['precipitation'][0]
            
            col1.metric(t["temp"], f"{curr_temp}°C")
            col2.metric(t["wind"], f"{curr_wind} km/h")

            # Апат қаупін бағалау алгоритмі (Математикалық логика)
            st.subheader(t["risk_lvl"])
            risk_score = 0
            if curr_wind > 50: risk_score += 40
            if curr_temp > 35: risk_score += 30
            if curr_prec > 10: risk_score += 30
            
            if risk_score >= 60:
                st.error(f"{t['high_risk']}: {risk_score}%")
            else:
                st.info(f"{t['low_risk']}: {risk_score}%")

            # Температура графигі
            df = pd.DataFrame({
                'Time': weather['hourly']['time'][:24],
                'Temp': weather['hourly']['temperature_2m'][:24]
            })
            fig = px.line(df, x='Time', y='Temp', title="24h Forecast")
            st.plotly_chart(fig, use_container_width=True)

            # ЖИ Сараптамасы (OpenAI)
            st.subheader("🤖 AI Analysis")
            if st.button(t["ai_btn"]):
                if api_key:
                    try:
                        client = OpenAI(api_key=api_key)
                        prompt = f"Analyze weather for {location['name']}: Temp {curr_temp}C, Wind {curr_wind}km/h. Disaster risk {risk_score}%. Language: {sel_lang}."
                        res = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": prompt}]
                        )
                        st.write(res.choices[0].message.content)
                    except Exception as e:
                        st.error(f"AI Error: {e}")
                else:
                    st.warning("Please enter OpenAI API Key in sidebar")
    else:
        st.error(t["not_found"])

# 5. ҚОРЫТЫНДЫ
st.divider()
st.caption(t["team"])
