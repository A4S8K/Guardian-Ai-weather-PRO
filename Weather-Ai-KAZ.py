import streamlit as st
import pandas as pd
import requests
from openai import OpenAI
import plotly.graph_objects as go
import json

# ====================== КӨП ТІЛДІК ҚОЛДАУ ======================
LANGUAGES = {
    "Қазақша": "kk",
    "English": "en"
}

TEXTS = {
    "kk": {
        "title": "🛡️ Guardian AI Weather PRO",
        "subtitle": "Жер бетінде болатын табиғи апаттарды ЖИ арқылы болжап, адамзатқа көмек беру",
        "caption": "Арслан Өмен, Иманғали Құрбанбек | Төлеби ауданының мамандандырылған мектеп-интернаты, 9-сынып | Түркістан облысы",
        "sidebar_params": "⚙️ Параметрлер",
        "api_key_label": "OpenAI API Key (GPT-4o-mini)",
        "city_label": "Қала / елді мекен",
        "search_btn": "🔍 Іздеу және болжау",
        "location_searching": "📍 Орынды анықтау және мәліметтерді жүктеу...",
        "no_location": "❌ Қала табылмады. Қазақша немесе ағылшынша қайта жазып көріңіз",
        "select_location": "📍 Таңдаңыз (10 нұсқа):",
        "current_weather": "🌤️ Ағымдағы жағдай",
        "air_quality": "🌫️ Ауа сапасы (AQI)",
        "forecast_7days": "📅 7 күндік болжам",
        "risk_title": "⚠️ Табиғи апат қаупі",
        "high_risk": "🔴 ЖОҒАРЫ ҚАУІП! Алдын ала шаралар қабылдаңыз!",
        "ai_analysis": "🧠 ЖИ Сараптамасы және ұсыныстар",
        "map_title": "🗺️ Карта және жел динамикасы",
        "success": "✅ Барлық мәліметтер сәтті жүктелді! Ауа сапасы қосылды.",
        "footer": "**Қорытынды**: Guardian AI Weather PRO — математика + ЖИ симбиозы. Табиғи апаттарды ерте болжайды.",
    },
    "en": {
        "title": "🛡️ Guardian AI Weather PRO",
        "subtitle": "Predicting natural disasters on Earth with AI to help humanity",
        "caption": "Arslan Omen, Imangali Kurbanbek | Specialized Boarding School of Tolebi District, 9th grade | Turkistan Region",
        "sidebar_params": "⚙️ Settings",
        "api_key_label": "OpenAI API Key (GPT-4o-mini)",
        "city_label": "City / Location",
        "search_btn": "🔍 Search and Forecast",
        "location_searching": "📍 Detecting location and loading data...",
        "no_location": "❌ Location not found. Try again in Kazakh or English",
        "select_location": "📍 Choose (10 options):",
        "current_weather": "🌤️ Current Conditions",
        "air_quality": "🌫️ Air Quality (AQI)",
        "forecast_7days": "📅 7-Day Forecast",
        "risk_title": "⚠️ Natural Disaster Risk",
        "high_risk": "🔴 HIGH RISK! Take precautions immediately!",
        "ai_analysis": "🧠 AI Analysis & Recommendations",
        "map_title": "🗺️ Map and Wind Dynamics",
        "success": "✅ All data loaded successfully! Air quality included.",
        "footer": "**Conclusion**: Guardian AI Weather PRO — math + AI symbiosis. Early prediction of natural disasters.",
    }
}

# ====================== БАСТАУ ======================
st.set_page_config(page_title="Guardian AI Weather PRO", page_icon="🛡️", layout="wide")

# Тіл таңдау (көп тілдік)
selected_lang_name = st.sidebar.selectbox("🌐 Тіл / Language", options=list(LANGUAGES.keys()), index=0)
lang = LANGUAGES[selected_lang_name]
t = TEXTS[lang]

st.title(t["title"])
st.markdown(f"**{t['subtitle']}**")
st.caption(t["caption"])

# ====================== SIDEBAR ======================
st.sidebar.header(t["sidebar_params"])
openai_key = st.sidebar.text_input(t["api_key_label"], type="password", value="")
city_input = st.sidebar.text_input(t["city_label"], value="Шымкент" if lang == "kk" else "Shymkent")
search_btn = st.sidebar.button(t["search_btn"], type="primary")

# ====================== ФУНКЦИЯЛАР ======================
def get_coordinates(city):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=10&language=kk&format=json"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data.get("results", [])
    except Exception as e:
        st.error(f"📍 {t['no_location']}: {str(e)}")
        return []

def get_weather(lat, lon):
    url = (f"https://api.open-meteo.com/v1/forecast?"
           f"latitude={lat}&longitude={lon}&"
           f"current=temperature_2m,relative_humidity_2m,apparent_temperature,"
           f"rain,showers,snowfall,weather_code,wind_speed_10m,wind_gusts_10m,wind_direction_10m&"
           f"hourly=temperature_2m,relative_humidity_2m,uv_index,precipitation_probability,wind_speed_10m&"
           f"daily=weather_code,temperature_2m_max,temperature_2m_min,uv_index_max,"
           f"precipitation_sum,wind_speed_10m_max,wind_gusts_10m_max&"
           f"forecast_days=7&timezone=auto")
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"🌤️ {t['current_weather']} мәліметтері жүктелмеді: {str(e)}")
        return None

def get_air_quality(lat, lon):
    """Ауа сапасы ӘЛДЕҚАШАН қосылған және міндетті болып есептеледі"""
    url = (f"https://air-quality-api.open-meteo.com/v1/air-quality?"
           f"latitude={lat}&longitude={lon}&"
           f"current=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,ozone&"
           f"timezone=auto")
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except:
        return None  # Қателік болса да бөлім көрсетіледі

def calculate_risk(weather):
    if not weather or 'current' not in weather:
        return {}, 0
    wind = weather['current'].get('wind_speed_10m', 0)
    temp = weather['current'].get('temperature_2m', 0)
    rain = weather['current'].get('rain', 0) + weather['current'].get('showers', 0)
    
    risks = {}
    risks["Дауыл / қатты жел" if lang == "kk" else "Storm / Strong Wind"] = min(100, int(wind * 1.8)) if wind > 30 else 10
    risks["Су тасқыны" if lang == "kk" else "Flood"] = min(100, int(rain * 25)) if rain > 5 else 5
    risks["Аптап ыстық" if lang == "kk" else "Heatwave"] = min(100, int((temp - 35) * 8)) if temp > 35 else 15
    risks["Орман өрті қаупі" if lang == "kk" else "Forest Fire Risk"] = min(100, int((temp * 0.8) + (100 - weather['current'].get('relative_humidity_2m', 50)) * 0.6)) if temp > 30 else 20
    risks["Қатты аяз" if lang == "kk" else "Severe Frost"] = min(100, int((-temp - 15) * 6)) if temp < -10 else 5
    
    overall = max(risks.values()) if risks else 0
    return risks, overall

# ====================== НЕГІЗГІ ЛОГИКА ======================
if search_btn:
    with st.spinner(t["location_searching"]):
        locations = get_coordinates(city_input)
    
    if not locations:
        st.stop()
    
    options = []
    for loc in locations:
        admin = loc.get('admin1', '')
        country = loc.get('country', '')
        label = f"{loc['name']} {', ' + admin if admin else ''} ({country}) — {loc['latitude']:.2f}, {loc['longitude']:.2f}"
        options.append(label)
    
    selected_label = st.selectbox(t["select_location"], options, index=0)
    idx = options.index(selected_label)
    selected = locations[idx]
    
    lat, lon = selected['latitude'], selected['longitude']
    st.success(f"✅ **{selected['name']}**, {selected.get('country','')} ({lat:.4f}, {lon:.4f})")

    weather = get_weather(lat, lon)
    air = get_air_quality(lat, lon)   # Ауа сапасы ӘЛДЕҚАШАН қосылды
    
    if not weather:
        st.stop()
    
    current = weather['current']
    daily = weather['daily']
    
    # 1. АҒЫМДАҒЫ ЖАҒДАЙ
    st.subheader(t["current_weather"])
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🌡️ Температура" if lang == "kk" else "🌡️ Temperature", 
                  f"{current['temperature_2m']}°C", 
                  f"Сезіледі: {current.get('apparent_temperature', current['temperature_2m'])}°C" if lang == "kk" else f"Feels like: {current.get('apparent_temperature', current['temperature_2m'])}°C")
    with col2:
        st.metric("💧 Ылғалдылық" if lang == "kk" else "💧 Humidity", f"{current['relative_humidity_2m']}%")
    with col3:
        st.metric("🌬️ Жел" if lang == "kk" else "🌬️ Wind", f"{current['wind_speed_10m']} км/сағ (порыв {current.get('wind_gusts_10m',0)})" if lang == "kk" else f"{current['wind_speed_10m']} km/h (gusts {current.get('wind_gusts_10m',0)})")
    with col4:
        st.metric("🌧️ Жаңбыр" if lang == "kk" else "🌧️ Rain", f"{current.get('rain',0) + current.get('showers',0)} мм" if lang == "kk" else f"{current.get('rain',0) + current.get('showers',0)} mm")
    
    # 2. АУА САПАСЫ (ӘЛДЕҚАШАН ҚОСЫЛҒАН)
    st.subheader(t["air_quality"])
    if air and 'current' in air:
        aqi_pm25 = air['current'].get('pm2_5', 0)
        if aqi_pm25 < 50:
            aqi_text = "✅ Жақсы" if lang == "kk" else "✅ Good"
            color = "green"
        elif aqi_pm25 < 100:
            aqi_text = "⚠️ Орташа" if lang == "kk" else "⚠️ Moderate"
            color = "orange"
        else:
            aqi_text = "❌ Зиянды" if lang == "kk" else "❌ Unhealthy"
            color = "red"
        st.markdown(f"<h3 style='color:{color}'>AQI = {aqi_pm25:.1f} — {aqi_text}</h3>", unsafe_allow_html=True)
    else:
        st.info("🌫️ Ауа сапасы мәліметтері уақытша қолжетімсіз (бірақ бөлім сақталды)" if lang == "kk" else "🌫️ Air quality data temporarily unavailable (section preserved)")
    
    # 3. 7 КҮНДІК БОЛЖАМ
    st.subheader(t["forecast_7days"])
    df_daily = pd.DataFrame({
        "Күн" if lang == "kk" else "Day": daily['time'],
        "Max °C": daily['temperature_2m_max'],
        "Min °C": daily['temperature_2m_min'],
        "UV max": daily['uv_index_max'],
        "Жаңбыр (мм)" if lang == "kk" else "Rain (mm)": daily['precipitation_sum'],
        "Жел max (км/сағ)" if lang == "kk" else "Wind max (km/h)": daily['wind_speed_10m_max']
    })
    st.dataframe(df_daily, use_container_width=True)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily['time'], y=daily['temperature_2m_max'], name="Max температура" if lang == "kk" else "Max Temp", line=dict(color="red")))
    fig.add_trace(go.Scatter(x=daily['time'], y=daily['temperature_2m_min'], name="Min температура" if lang == "kk" else "Min Temp", line=dict(color="blue")))
    fig.update_layout(title="Температура өзгерісі (7 күн)" if lang == "kk" else "Temperature Change (7 days)", xaxis_title="Күн" if lang == "kk" else "Day", yaxis_title="°C", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # 4. АПАТ ҚАУПІ
    risks, overall_risk = calculate_risk(weather)
    st.subheader(f"{t['risk_title']} — Жалпы: {overall_risk}%" if lang == "kk" else f"{t['risk_title']} — Overall: {overall_risk}%")
    if overall_risk >= 60:
        st.error(t["high_risk"])
    cols = st.columns(len(risks))
    for i, (risk_name, value) in enumerate(risks.items()):
        with cols[i]:
            st.metric(risk_name, f"{value}%")
    
    # 5. ЖИ САРАПТАМАСЫ (тілге сәйкес)
    if openai_key:
        client = OpenAI(api_key=openai_key)
        prompt_lang = "Қазақ тілінде" if lang == "kk" else "in English"
        prompt = f"""Сіз метеорология және табиғи апаттар бойынша сарапшысыз. 
Қала: {selected['name']} ({lat}, {lon})
Ағымдағы деректер: температура {current['temperature_2m']}°C, жел {current['wind_speed_10m']} км/сағ, ылғалдылық {current['relative_humidity_2m']}%, жаңбыр {current.get('rain',0)} мм.
7 күндік болжам: {json.dumps(daily, ensure_ascii=False)[:800]}...
Ауа сапасы: {'PM2.5 = ' + str(air['current'].get('pm2_5',0)) if air else 'қолжетімсіз'}.

{prompt_lang} толық сараптама жасаңыз:
- Әр апаттың ықтималдығын % есебінде беріңіз.
- Егер қауіп 60%-дан асса — қызыл ескерту.
- Адамдарға нақты ұсыныстар беріңіз.
- Математикалық негіз көрсетіңіз."""
        
        with st.spinner("🧠 ЖИ (GPT-4o-mini) талдау жүргізуде..." if lang == "kk" else "🧠 AI (GPT-4o-mini) is analyzing..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                ai_text = response.choices[0].message.content
                st.subheader(t["ai_analysis"])
                st.markdown(ai_text)
            except Exception as e:
                st.error(f"OpenAI қатесі: {str(e)}" if lang == "kk" else f"OpenAI error: {str(e)}")
    else:
        st.warning("🔑 OpenAI API Key енгізіңіз — ЖИ сараптамасы жұмыс істейді!" if lang == "kk" else "🔑 Enter OpenAI API Key — AI analysis will work!")
    
    # 6. КАРТА
    st.subheader(t["map_title"])
    st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}), zoom=10)
    
    st.success(t["success"])
    st.info("💡 Болашақта: push-хабарламалар, LSTM, мобильді нұсқа" if lang == "kk" else "💡 Future: push notifications, LSTM, mobile version")

else:
    st.info("🔍 Іздеу түймесін басыңыз — мәліметтер бірден жүктеледі." if lang == "kk" else "🔍 Press the Search button — data will load immediately.")

st.divider()
st.markdown(t["footer"])
st.caption("© Арслан Өмен, Иманғали Құрбанбек | 2026 ж." if lang == "kk" else "© Arslan Omen, Imangali Kurbanbek | 2026")
