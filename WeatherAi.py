import streamlit as st
import pandas as pd
import requests
from openai import OpenAI
import plotly.graph_objects as go
import json
import time

# ====================== КӨП ТІЛДІК ҚОЛДАУ (Қазақша + English + Русский) ======================
LANGUAGES = {
    "Қазақша": "kk",
    "English": "en",
    "Русский": "ru"
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
        "no_location": "❌ Қала табылмады. Қазақша, ағылшынша немесе орысша қайта жазып көріңіз",
        "select_location": "📍 Таңдаңыз (10 нұсқа):",
        "current_weather": "🌤️ Ағымдағы жағдай",
        "air_quality": "🌫️ Ауа сапасы (AQI)",
        "forecast_7days": "📅 7 күндік болжам",
        "risk_title": "⚠️ Табиғи апат қаупі",
        "high_risk": "🔴 ЖОҒАРЫ ҚАУІП! Алдын ала шаралар қабылдаңыз!",
        "ai_analysis": "🧠 ЖИ Сараптамасы және ұсыныстар",
        "map_title": "🗺️ Карта және жел динамикасы",
        "success": "✅ Барлық мәліметтер (ауа сапасы қосылған) сәтті жүктелді!",
        "retrying": "🔄 Қайталап көруде... (интернет немесе сервер мәселесі)",
        "connection_error": "🌐 Интернет байланысы нашар немесе Open-Meteo сервері уақытша қолжетімсіз.\nVPN қосыңыз немесе 30 секундтан кейін қайталаңыз.",
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
        "no_location": "❌ Location not found. Try again in Kazakh, English or Russian",
        "select_location": "📍 Choose (10 options):",
        "current_weather": "🌤️ Current Conditions",
        "air_quality": "🌫️ Air Quality (AQI)",
        "forecast_7days": "📅 7-Day Forecast",
        "risk_title": "⚠️ Natural Disaster Risk",
        "high_risk": "🔴 HIGH RISK! Take precautions immediately!",
        "ai_analysis": "🧠 AI Analysis & Recommendations",
        "map_title": "🗺️ Map and Wind Dynamics",
        "success": "✅ All data loaded successfully (air quality included)!",
        "retrying": "🔄 Retrying...",
        "connection_error": "🌐 Poor internet connection or Open-Meteo server temporarily unavailable.\nTry VPN or wait 30 seconds and retry.",
        "footer": "**Conclusion**: Guardian AI Weather PRO — math + AI symbiosis. Early prediction of natural disasters.",
    },
    "ru": {
        "title": "🛡️ Guardian AI Weather PRO",
        "subtitle": "Прогнозирование природных катастроф на Земле с помощью ИИ для помощи человечеству",
        "caption": "Арслан Омен, Имангали Курбанбек | Специализированный интернат Толебийского района, 9 класс | Туркестанская область",
        "sidebar_params": "⚙️ Параметры",
        "api_key_label": "Ключ OpenAI API (GPT-4o-mini)",
        "city_label": "Город / Населённый пункт",
        "search_btn": "🔍 Поиск и прогноз",
        "location_searching": "📍 Определение места и загрузка данных...",
        "no_location": "❌ Место не найдено. Попробуйте снова на казахском, английском или русском",
        "select_location": "📍 Выберите (10 вариантов):",
        "current_weather": "🌤️ Текущие условия",
        "air_quality": "🌫️ Качество воздуха (AQI)",
        "forecast_7days": "📅 Прогноз на 7 дней",
        "risk_title": "⚠️ Риск природных катастроф",
        "high_risk": "🔴 ВЫСОКИЙ РИСК! Примите меры предосторожности немедленно!",
        "ai_analysis": "🧠 Анализ ИИ и рекомендации",
        "map_title": "🗺️ Карта и динамика ветра",
        "success": "✅ Все данные успешно загружены (качество воздуха включено)!",
        "retrying": "🔄 Повторная попытка...",
        "connection_error": "🌐 Плохое интернет-соединение или сервер Open-Meteo временно недоступен.\nВключите VPN или подождите 30 секунд и повторите.",
        "footer": "**Заключение**: Guardian AI Weather PRO — симбиоз математики + ИИ. Раннее прогнозирование природных катастроф.",
    }
}

# ====================== БАСТАУ ======================
st.set_page_config(page_title="Guardian AI Weather PRO", page_icon="🛡️", layout="wide")

selected_lang_name = st.sidebar.selectbox("🌐 Тіл / Язык / Language", options=list(LANGUAGES.keys()), index=0)
lang_code = LANGUAGES[selected_lang_name]
t = TEXTS[lang_code]

st.title(t["title"])
st.markdown(f"**{t['subtitle']}**")
st.caption(t["caption"])

if "first_load" not in st.session_state:
    st.session_state.first_load = True

# ====================== SIDEBAR ======================
st.sidebar.header(t["sidebar_params"])
openai_key = st.sidebar.text_input(t["api_key_label"], type="password", value="")
city_input = st.sidebar.text_input(t["city_label"], value="Шымкент")
search_btn = st.sidebar.button(t["search_btn"], type="primary")

# ====================== RETRY HELPER (Қателіктерді автоматты түзету) ======================
def retry_request(func, max_retries=3, delay=3):
    last_error = None
    for attempt in range(max_retries):
        try:
            return func()
        except requests.exceptions.RequestException as e:
            last_error = e
            if attempt == max_retries - 1:
                raise
            st.warning(t["retrying"])
            time.sleep(delay * (attempt + 1))
    raise last_error

# ====================== ФУНКЦИЯЛАР (ретримен) ======================
def get_coordinates(city, lang_code):
    def _fetch():
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=10&language={lang_code}&format=json"
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json().get("results", [])
    return retry_request(_fetch)

def get_weather(lat, lon):
    def _fetch():
        url = (f"https://api.open-meteo.com/v1/forecast?"
               f"latitude={lat}&longitude={lon}&"
               f"current=temperature_2m,relative_humidity_2m,apparent_temperature,"
               f"rain,showers,snowfall,weather_code,wind_speed_10m,wind_gusts_10m,wind_direction_10m&"
               f"hourly=temperature_2m,relative_humidity_2m,uv_index,precipitation_probability,wind_speed_10m&"
               f"daily=weather_code,temperature_2m_max,temperature_2m_min,uv_index_max,"
               f"precipitation_sum,wind_speed_10m_max,wind_gusts_10m_max&"
               f"forecast_days=7&timezone=auto")
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
    return retry_request(_fetch)

def get_air_quality(lat, lon):
    def _fetch():
        url = (f"https://air-quality-api.open-meteo.com/v1/air-quality?"
               f"latitude={lat}&longitude={lon}&"
               f"current=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,ozone&"
               f"timezone=auto")
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
    try:
        return retry_request(_fetch)
    except:
        return None

def calculate_risk(weather, lang_code):
    if not weather or 'current' not in weather:
        return {}, 0
    wind = weather['current'].get('wind_speed_10m', 0)
    temp = weather['current'].get('temperature_2m', 0)
    rain = weather['current'].get('rain', 0) + weather['current'].get('showers', 0)
    
    if lang_code == "kk":
        risk_names = ["Дауыл / қатты жел", "Су тасқыны", "Аптап ыстық", "Орман өрті қаупі", "Қатты аяз"]
    elif lang_code == "ru":
        risk_names = ["Шторм / сильный ветер", "Наводнение", "Жара", "Риск лесного пожара", "Сильный мороз"]
    else:
        risk_names = ["Storm / Strong Wind", "Flood", "Heatwave", "Forest Fire Risk", "Severe Frost"]
    
    risks = {}
    risks[risk_names[0]] = min(100, int(wind * 1.8)) if wind > 30 else 10
    risks[risk_names[1]] = min(100, int(rain * 25)) if rain > 5 else 5
    risks[risk_names[2]] = min(100, int((temp - 35) * 8)) if temp > 35 else 15
    risks[risk_names[3]] = min(100, int((temp * 0.8) + (100 - weather['current'].get('relative_humidity_2m', 50)) * 0.6)) if temp > 30 else 20
    risks[risk_names[4]] = min(100, int((-temp - 15) * 6)) if temp < -10 else 5
    
    overall = max(risks.values()) if risks else 0
    return risks, overall

# ====================== НЕГІЗГІ ЛОГИКА ======================
trigger = search_btn or st.session_state.first_load
if st.session_state.first_load:
    st.session_state.first_load = False

if trigger:
    with st.spinner(t["location_searching"]):
        try:
            locations = get_coordinates(city_input, lang_code)
        except Exception as e:
            st.error(t["connection_error"] + f"\n\nҚате: {str(e)}")
            st.stop()
    
    if not locations:
        st.error(t["no_location"])
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

    try:
        weather = get_weather(lat, lon)
    except Exception as e:
        st.error(t["connection_error"] + f"\n\n🌤️ Қате: {str(e)}")
        st.info("🔄 Қайталап көріңіз немесе VPN қосыңыз")
        st.stop()

    air = get_air_quality(lat, lon)
    
    current = weather['current']
    daily = weather['daily']
    
    # 1. АҒЫМДАҒЫ ЖАҒДАЙ
    st.subheader(t["current_weather"])
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🌡️ Температура" if lang_code == "kk" else "🌡️ Temperature" if lang_code == "en" else "🌡️ Температура", 
                  f"{current['temperature_2m']}°C", 
                  f"Сезіледі: {current.get('apparent_temperature', current['temperature_2m'])}°C" if lang_code == "kk" else 
                  f"Feels like: {current.get('apparent_temperature', current['temperature_2m'])}°C" if lang_code == "en" else 
                  f"Ощущается: {current.get('apparent_temperature', current['temperature_2m'])}°C")
    with col2:
        st.metric("💧 Ылғалдылық" if lang_code == "kk" else "💧 Humidity" if lang_code == "en" else "💧 Влажность", f"{current['relative_humidity_2m']}%")
    with col3:
        st.metric("🌬️ Жел" if lang_code == "kk" else "🌬️ Wind" if lang_code == "en" else "🌬️ Ветер", 
                  f"{current['wind_speed_10m']} км/сағ (порыв {current.get('wind_gusts_10m',0)})" if lang_code == "kk" else 
                  f"{current['wind_speed_10m']} km/h (gusts {current.get('wind_gusts_10m',0)})" if lang_code == "en" else 
                  f"{current['wind_speed_10m']} км/ч (порывы {current.get('wind_gusts_10m',0)})")
    with col4:
        st.metric("🌧️ Жаңбыр" if lang_code == "kk" else "🌧️ Rain" if lang_code == "en" else "🌧️ Дождь", 
                  f"{current.get('rain',0) + current.get('showers',0)} мм" if lang_code == "kk" else 
                  f"{current.get('rain',0) + current.get('showers',0)} mm" if lang_code == "en" else 
                  f"{current.get('rain',0) + current.get('showers',0)} мм")
    
    # 2. АУА САПАСЫ
    st.subheader(t["air_quality"])
    if air and 'current' in air:
        aqi_pm25 = air['current'].get('pm2_5', 0)
        if aqi_pm25 < 50:
            aqi_text = "✅ Жақсы" if lang_code == "kk" else "✅ Good" if lang_code == "en" else "✅ Хорошее"
            color = "green"
        elif aqi_pm25 < 100:
            aqi_text = "⚠️ Орташа" if lang_code == "kk" else "⚠️ Moderate" if lang_code == "en" else "⚠️ Умеренное"
            color = "orange"
        else:
            aqi_text = "❌ Зиянды" if lang_code == "kk" else "❌ Unhealthy" if lang_code == "en" else "❌ Вредное"
            color = "red"
        st.markdown(f"<h3 style='color:{color}'>AQI = {aqi_pm25:.1f} — {aqi_text}</h3>", unsafe_allow_html=True)
    else:
        st.info("🌫️ Ауа сапасы мәліметтері уақытша қолжетімсіз" if lang_code == "kk" else 
                "🌫️ Air quality data temporarily unavailable" if lang_code == "en" else 
                "🌫️ Данные о качестве воздуха временно недоступны")
    
    # 3. 7 КҮНДІК БОЛЖАМ
    st.subheader(t["forecast_7days"])
    df_daily = pd.DataFrame({
        "Күн" if lang_code == "kk" else "Day" if lang_code == "en" else "День": daily['time'],
        "Max °C": daily['temperature_2m_max'],
        "Min °C": daily['temperature_2m_min'],
        "UV max": daily['uv_index_max'],
        "Жаңбыр (мм)" if lang_code == "kk" else "Rain (mm)" if lang_code == "en" else "Дождь (мм)": daily['precipitation_sum'],
        "Жел max (км/сағ)" if lang_code == "kk" else "Wind max (km/h)" if lang_code == "en" else "Ветер max (км/ч)": daily['wind_speed_10m_max']
    })
    st.dataframe(df_daily, use_container_width=True)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily['time'], y=daily['temperature_2m_max'], name="Max температура" if lang_code == "kk" else "Max Temp" if lang_code == "en" else "Макс. температура", line=dict(color="red")))
    fig.add_trace(go.Scatter(x=daily['time'], y=daily['temperature_2m_min'], name="Min температура" if lang_code == "kk" else "Min Temp" if lang_code == "en" else "Мин. температура", line=dict(color="blue")))
    fig.update_layout(title="Температура өзгерісі (7 күн)" if lang_code == "kk" else "Temperature Change (7 days)" if lang_code == "en" else "Изменение температуры (7 дней)", 
                      xaxis_title="Күн" if lang_code == "kk" else "Day" if lang_code == "en" else "День", 
                      yaxis_title="°C", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # 4. АПАТ ҚАУПІ
    risks, overall_risk = calculate_risk(weather, lang_code)
    st.subheader(f"{t['risk_title']} — Жалпы: {overall_risk}%" if lang_code == "kk" else f"{t['risk_title']} — Overall: {overall_risk}%" if lang_code == "en" else f"{t['risk_title']} — Общий: {overall_risk}%")
    if overall_risk >= 60:
        st.error(t["high_risk"])
    cols = st.columns(len(risks))
    for i, (risk_name, value) in enumerate(risks.items()):
        with cols[i]:
            st.metric(risk_name, f"{value}%")
    
    # 5. ЖИ САРАПТАМАСЫ
    if openai_key:
        client = OpenAI(api_key=openai_key)
        prompt_lang = "Қазақ тілінде" if lang_code == "kk" else "на русском языке" if lang_code == "ru" else "in English"
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
        
        with st.spinner("🧠 ЖИ (GPT-4o-mini) талдау жүргізуде..." if lang_code == "kk" else "🧠 ИИ (GPT-4o-mini) анализирует..." if lang_code == "ru" else "🧠 AI (GPT-4o-mini) is analyzing..."):
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
                st.error(f"OpenAI қатесі: {str(e)}" if lang_code == "kk" else f"Ошибка OpenAI: {str(e)}" if lang_code == "ru" else f"OpenAI error: {str(e)}")
    else:
        st.warning("🔑 OpenAI API Key енгізіңіз — ЖИ сараптамасы жұмыс істейді!" if lang_code == "kk" else 
                   "🔑 Введите ключ OpenAI API — анализ ИИ будет работать!" if lang_code == "ru" else 
                   "🔑 Enter OpenAI API Key — AI analysis will work!")
    
    # 6. КАРТА
    st.subheader(t["map_title"])
    st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}), zoom=10)
    
    st.success(t["success"])
    st.info("💡 Егер мәліметтер жүктелмесе — VPN қосыңыз немесе интернетті тексеріңіз")

else:
    st.info("🔍 Іздеу түймесін басыңыз немесе тілді ауыстырыңыз — мәліметтер бірден жүктеледі.")

st.divider()
st.markdown(t["footer"])
st.caption("© Арслан Өмен, Иманғали Құрбанбек | 2026 ж." if lang_code == "kk" else 
           "© Arslan Omen, Imangali Kurbanbek | 2026" if lang_code == "en" else 
           "© Арслан Омен, Имангали Курбанбек | 2026")
