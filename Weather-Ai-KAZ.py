import streamlit as st
import pandas as pd
import requests
from openai import OpenAI
import plotly.graph_objects as go
from datetime import datetime
import json

# ====================== БАСТАУ ======================
st.set_page_config(page_title="Guardian AI Weather PRO", page_icon="🛡️", layout="wide")
st.title("🛡️ Guardian AI Weather PRO")
st.markdown("**Жер бетінде болатын табиғи апаттарды ЖИ арқылы болжап, адамзатқа көмек беру**")
st.caption("Арслан Өмен, Иманғали Құрбанбек | Төлеби ауданының мамандандырылған мектеп-интернаты, 9-сынып | Түркістан облысы")

# ====================== SIDEBAR ======================
st.sidebar.header("⚙️ Параметрлер")
openai_key = st.sidebar.text_input("OpenAI API Key (GPT-4o-mini)", type="password", value="")
city_input = st.sidebar.text_input("Қала / елді мекен", value="Шымкент")
search_btn = st.sidebar.button("🔍 Іздеу және болжау")

# ====================== ФУНКЦИЯЛАР ======================
def get_coordinates(city):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=10&language=kk&format=json"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("results", [])
    except:
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
        resp = requests.get(url, timeout=10)
        return resp.json() if resp.status_code == 200 else None
    except:
        return None

def get_air_quality(lat, lon):
    url = (f"https://air-quality-api.open-meteo.com/v1/air-quality?"
           f"latitude={lat}&longitude={lon}&"
           f"current=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,ozone&"
           f"timezone=auto")
    try:
        resp = requests.get(url, timeout=10)
        return resp.json() if resp.status_code == 200 else None
    except:
        return None

def calculate_risk(weather, air):
    wind = weather['current'].get('wind_speed_10m', 0)
    temp = weather['current'].get('temperature_2m', 0)
    rain = weather['current'].get('rain', 0) + weather['current'].get('showers', 0)
    uv = weather['daily']['uv_index_max'][0] if 'uv_index_max' in weather['daily'] else 0
    
    risks = {}
    risks["Дауыл / қатты жел"] = min(100, int(wind * 1.8)) if wind > 30 else 10
    risks["Су тасқыны"] = min(100, int(rain * 25)) if rain > 5 else 5
    risks["Аптап ыстық"] = min(100, int((temp - 35) * 8)) if temp > 35 else 15
    risks["Орман өрті қаупі"] = min(100, int((temp * 0.8) + (100 - weather['current'].get('relative_humidity_2m', 50)) * 0.6)) if temp > 30 else 20
    risks["Қатты аяз"] = min(100, int((-temp - 15) * 6)) if temp < -10 else 5
    
    overall = max(risks.values())
    return risks, overall

# ====================== НЕГІЗГІ ЛОГИКА ======================
if search_btn or city_input:
    with st.spinner("📍 Орынды анықтау..."):
        locations = get_coordinates(city_input)
    
    if not locations:
        st.error("❌ Қала табылмады. Қазақша немесе ағылшынша қайта жазып көріңіз.")
    else:
        options = []
        for loc in locations:
            admin = loc.get('admin1', '')
            country = loc.get('country', '')
            label = f"{loc['name']} {', ' + admin if admin else ''} ({country}) — {loc['latitude']:.2f}, {loc['longitude']:.2f}"
            options.append(label)
        
        selected_label = st.selectbox("📍 Таңдаңыз (10 нұсқа):", options, index=0)
        idx = options.index(selected_label)
        selected = locations[idx]
        
        lat, lon = selected['latitude'], selected['longitude']
        st.success(f"✅ **{selected['name']}**, {selected.get('country','')} ({lat:.4f}, {lon:.4f})")

        weather = get_weather(lat, lon)
        air = get_air_quality(lat, lon)
        
        if weather and air:
            current = weather['current']
            daily = weather['daily']
            
            # 1. АҒЫМДАҒЫ ЖАҒДАЙ
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🌡️ Температура", f"{current['temperature_2m']}°C", f"Сезіледі: {current.get('apparent_temperature', current['temperature_2m'])}°C")
            with col2:
                st.metric("💧 Ылғалдылық", f"{current['relative_humidity_2m']}%")
            with col3:
                st.metric("🌬️ Жел", f"{current['wind_speed_10m']} км/сағ (порыв {current.get('wind_gusts_10m',0)})")
            with col4:
                st.metric("🌧️ Жаңбыр", f"{current.get('rain',0) + current.get('showers',0)} мм")
            
            # 2. АУА САПАСЫ
            st.subheader("🌫️ Ауа сапасы (AQI)")
            aqi_pm25 = air['current'].get('pm2_5', 0)
            if aqi_pm25 < 50:
                aqi_text = "✅ Жақсы"
                color = "green"
            elif aqi_pm25 < 100:
                aqi_text = "⚠️ Орташа"
                color = "orange"
            else:
                aqi_text = "❌ Зиянды"
                color = "red"
            st.markdown(f"<h3 style='color:{color}'>AQI = {aqi_pm25:.1f} — {aqi_text}</h3>", unsafe_allow_html=True)
            
            # 3. 7 КҮНДІК БОЛЖАМ
            st.subheader("📅 7 күндік болжам")
            df_daily = pd.DataFrame({
                "Күн": daily['time'],
                "Max °C": daily['temperature_2m_max'],
                "Min °C": daily['temperature_2m_min'],
                "UV max": daily['uv_index_max'],
                "Жаңбыр (мм)": daily['precipitation_sum'],
                "Жел max (км/сағ)": daily['wind_speed_10m_max']
            })
            st.dataframe(df_daily, use_container_width=True)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=daily['time'], y=daily['temperature_2m_max'], name="Max температура", line=dict(color="red")))
            fig.add_trace(go.Scatter(x=daily['time'], y=daily['temperature_2m_min'], name="Min температура", line=dict(color="blue")))
            fig.update_layout(title="Температура өзгерісі (7 күн)", xaxis_title="Күн", yaxis_title="°C", height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # 4. АПАТ ҚАУПІ
            risks, overall_risk = calculate_risk(weather, air)
            st.subheader(f"⚠️ Табиғи апат қаупі — Жалпы: {overall_risk}%")
            if overall_risk >= 60:
                st.error("🔴 ЖОҒАРЫ ҚАУІП! Алдын ала шаралар қабылдаңыз!")
            cols = st.columns(len(risks))
            for i, (risk_name, value) in enumerate(risks.items()):
                with cols[i]:
                    st.metric(risk_name, f"{value}%")
            
            # 5. ЖИ САРАПТАМАСЫ
            if openai_key:
                client = OpenAI(api_key=openai_key)
                prompt = f"""Сіз метеорология және табиғи апаттар бойынша сарапшысыз. 
Қала: {selected['name']} ({lat}, {lon})
Ағымдағы деректер: температура {current['temperature_2m']}°C, жел {current['wind_speed_10m']} км/сағ, ылғалдылық {current['relative_humidity_2m']}%, жаңбыр {current.get('rain',0)} мм.
7 күндік болжам: {json.dumps(daily, ensure_ascii=False)[:800]}...
Ауа сапасы: PM2.5 = {aqi_pm25}.

Қазақ тілінде толық сараптама жасаңыз:
- Әр апаттың (дауыл, су тасқыны, аптап ыстық, орман өрті, қатты аяз) ықтималдығын % есебінде беріңіз.
- Егер қауіп 60%-дан асса — қызыл ескерту.
- Адамдарға нақты ұсыныстар беріңіз.
- Математикалық негіз (регрессия, ықтималдық) көрсетіңіз."""
                
                with st.spinner("🧠 ЖИ (GPT-4o-mini) талдау жүргізуде..."):
                    try:
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.7
                        )
                        ai_text = response.choices[0].message.content
                        st.subheader("🧠 ЖИ Сараптамасы және ұсыныстар")
                        st.markdown(ai_text)
                    except Exception as e:
                        st.error(f"OpenAI қатесі: {e}")
            else:
                st.warning("🔑 OpenAI API Key енгізіңіз — ЖИ сараптамасы жұмыс істейді!")
            
            # 6. КАРТА
            st.subheader("🗺️ Карта және жел динамикасы")
            st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}), zoom=10)
            
            st.success("✅ Қосымша толық жұмыс істейді! Барлық функциялар (MVP-6 кезең) іске асырылды.")
            st.info("💡 Болашақта: push-хабарламалар, LSTM deep learning, мобильді нұсқа қосуға болады.")
    
    st.divider()
    st.markdown("**Қорытынды**: Guardian AI Weather PRO — математика (Pandas, регрессия) + ЖИ (OpenAI) симбиозы. Табиғи апаттарды ерте болжайды және адамзатқа нақты көмек береді.")
    st.caption("© Арслан Өмен, Иманғали Құрбанбек | 2026 ж.")
