"""
Guardian AI Weather PRO — v3 (Windy картасымен)
================================================
Авторлар: Арслан Өмен, Иманғали Құрбанбек
Жетекші: Н.Әсілбай | Төлеби ауданы, 9-сынып
https://guardianaiweatherpro.streamlit.app/
"""

import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
from openai import OpenAI
from datetime import datetime

# ══════════════════════════════════════════════════════════════
# CSS ДИЗАЙН / CUSTOM STYLING
# ══════════════════════════════════════════════════════════════
CUSTOM_CSS = """
<style>
/* ── Негізгі фон / Main background ── */
[data-testid="stAppViewContainer"] {
    background: 
        radial-gradient(ellipse at 20% 50%, rgba(0, 201, 167, 0.06) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 20%, rgba(79, 195, 247, 0.05) 0%, transparent 50%),
        radial-gradient(ellipse at 60% 80%, rgba(123, 97, 255, 0.05) 0%, transparent 50%),
        linear-gradient(135deg, #060D1F 0%, #0D1F3C 40%, #060D1F 100%);
    background-attachment: fixed;
    color: #E8F4FD;
}

/* Жұлдыздар / Star particles */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image:
        radial-gradient(1px 1px at 15% 20%, rgba(255,255,255,0.6) 0%, transparent 100%),
        radial-gradient(1px 1px at 35% 10%, rgba(255,255,255,0.4) 0%, transparent 100%),
        radial-gradient(2px 2px at 55% 30%, rgba(255,255,255,0.5) 0%, transparent 100%),
        radial-gradient(1px 1px at 75% 15%, rgba(255,255,255,0.3) 0%, transparent 100%),
        radial-gradient(1px 1px at 90% 40%, rgba(255,255,255,0.4) 0%, transparent 100%),
        radial-gradient(1px 1px at 5%  70%, rgba(255,255,255,0.3) 0%, transparent 100%),
        radial-gradient(2px 2px at 45% 60%, rgba(255,255,255,0.2) 0%, transparent 100%),
        radial-gradient(1px 1px at 65% 75%, rgba(255,255,255,0.4) 0%, transparent 100%),
        radial-gradient(1px 1px at 82% 85%, rgba(255,255,255,0.3) 0%, transparent 100%),
        radial-gradient(1px 1px at 25% 90%, rgba(255,255,255,0.2) 0%, transparent 100%);
    pointer-events: none;
    z-index: 0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #060D1F 0%, #0A1830 100%) !important;
    border-right: 1px solid rgba(0, 201, 167, 0.2) !important;
}
[data-testid="stSidebar"] * {
    color: #8EAAC8 !important;
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {
    color: #00C9A7 !important;
}

/* ── Тақырып / Title ── */
h1 {
    background: linear-gradient(90deg, #00C9A7, #4FC3F7, #7B61FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 900 !important;
    letter-spacing: -1px;
}
h2, h3 {
    color: #E8F4FD !important;
    border-left: 3px solid #00C9A7;
    padding-left: 10px;
}

/* ── Метрика карточкалары / Metric cards ── */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #112240, #0D1F3C);
    border: 1px solid rgba(0, 201, 167, 0.2);
    border-radius: 12px;
    padding: 12px 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4), 0 0 20px rgba(0, 201, 167, 0.05);
    transition: transform 0.2s, box-shadow 0.2s;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5), 0 0 30px rgba(0, 201, 167, 0.15);
    border-color: rgba(0, 201, 167, 0.5);
}
[data-testid="stMetricLabel"] { color: #8EAAC8 !important; font-size: 12px !important; }
[data-testid="stMetricValue"] { color: #FFFFFF !important; font-weight: 700 !important; }
[data-testid="stMetricDelta"] { color: #00C9A7 !important; }

/* ── Батырмалар / Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #00C9A7, #009980) !important;
    color: #060D1F !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 8px 20px !important;
    box-shadow: 0 4px 15px rgba(0, 201, 167, 0.3) !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 25px rgba(0, 201, 167, 0.5) !important;
}

/* ── Input ── */
.stTextInput input {
    background: #112240 !important;
    border: 1px solid rgba(0, 201, 167, 0.3) !important;
    border-radius: 8px !important;
    color: #E8F4FD !important;
    font-size: 16px !important;
    padding: 10px 14px !important;
}
.stTextInput input:focus {
    border-color: #00C9A7 !important;
    box-shadow: 0 0 20px rgba(0, 201, 167, 0.2) !important;
}

/* ── Progress bar ── */
.stProgress > div > div {
    background: linear-gradient(90deg, #00C9A7, #4FC3F7) !important;
    border-radius: 10px !important;
}
.stProgress > div {
    background: rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
}

/* ── Info/Warning/Error boxes ── */
.stInfo {
    background: rgba(79, 195, 247, 0.08) !important;
    border: 1px solid rgba(79, 195, 247, 0.3) !important;
    border-radius: 10px !important;
    color: #E8F4FD !important;
}
.stError {
    background: rgba(255, 107, 107, 0.08) !important;
    border: 1px solid rgba(255, 107, 107, 0.4) !important;
    border-radius: 10px !important;
}
.stWarning {
    background: rgba(255, 209, 102, 0.08) !important;
    border: 1px solid rgba(255, 209, 102, 0.4) !important;
    border-radius: 10px !important;
}
.stSuccess {
    background: rgba(6, 214, 160, 0.08) !important;
    border: 1px solid rgba(6, 214, 160, 0.4) !important;
    border-radius: 10px !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: #112240 !important;
    border: 1px solid rgba(0, 201, 167, 0.3) !important;
    border-radius: 8px !important;
    color: #E8F4FD !important;
}

/* ── Slider ── */
.stSlider > div > div > div > div {
    background: linear-gradient(90deg, #00C9A7, #4FC3F7) !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    background: #112240 !important;
    border: 1px solid rgba(0, 201, 167, 0.15) !important;
    border-radius: 10px !important;
    overflow: hidden;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #112240 !important;
    border: 1px solid rgba(0, 201, 167, 0.2) !important;
    border-radius: 8px !important;
    color: #00C9A7 !important;
}

/* ── Chart ── */
[data-testid="stArrowVegaLiteChart"] {
    background: transparent !important;
}

/* ── Divider ── */
hr {
    border-color: rgba(0, 201, 167, 0.2) !important;
}

/* ── Caption / Footer ── */
.stCaption {
    color: #8EAAC8 !important;
    border-top: 1px solid rgba(0, 201, 167, 0.15);
    padding-top: 8px;
}

/* ── Animated glow on title area ── */
@keyframes pulse-glow {
    0%, 100% { text-shadow: 0 0 20px rgba(0,201,167,0.3); }
    50% { text-shadow: 0 0 40px rgba(0,201,167,0.6), 0 0 80px rgba(79,195,247,0.2); }
}
h1 { animation: pulse-glow 4s ease-in-out infinite; }

/* ── Weather icon badges ── */
.weather-badge {
    display: inline-block;
    background: rgba(0,201,167,0.15);
    border: 1px solid rgba(0,201,167,0.3);
    border-radius: 20px;
    padding: 4px 12px;
    margin: 2px;
    font-size: 13px;
    color: #00C9A7;
}

/* ── Map container ── */
iframe {
    border-radius: 14px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5), 0 0 40px rgba(0, 201, 167, 0.1) !important;
    border: 1px solid rgba(0, 201, 167, 0.2) !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #060D1F; }
::-webkit-scrollbar-thumb { background: #00C9A7; border-radius: 3px; }

/* Main content padding */
[data-testid="stMainBlockContainer"] {
    padding-top: 1.5rem;
}
</style>
"""

# ══════════════════════════════════════════════════════════════
# ТІЛДЕР / LANGUAGES
# ══════════════════════════════════════════════════════════════
LANG = {
    "kk": {
        "title": "🌍 Guardian AI Weather PRO",
        "subtitle": "Табиғи апаттарды ЖИ арқылы болжау жүйесі",
        "city_label": "Қала атын енгізіңіз",
        "city_ph": "Мысалы: Алматы",
        "btn": "🔍 Талдау",
        "select": "Қаланы нақтылаңыз:",
        "loading": "Деректер жүктелуде...",
        "err": "Қала табылмады.",
        "weather": "🌤 Ауа Райы",
        "risk": "⚠️ Апат Қаупі",
        "aqi": "💨 AQI",
        "uv": "☀️ UV Индексі",
        "h24": "🕐 24 Сағат",
        "h7": "📅 7 Күн",
        "map": "🗺️ Windy Интерактивті Карта",
        "ai": "🤖 ЖИ Сараптамасы",
        "no_api": "⚠️ OpenAI API кілтін енгізіңіз.",
        "high_warn": "🚨 Қауіп ≥ 60%! Дереу сақтық шараларын қолданыңыз!",
        "aqi_good": "✅ Жақсы", "aqi_med": "🟡 Орташа", "aqi_bad": "🔴 Зиянды",
        "uv_low": "🟢 Төмен", "uv_med": "🟡 Орташа", "uv_hi": "🟠 Жоғары",
        "uv_vhi": "🔴 Өте жоғары", "uv_ex": "🟣 Экстремалды",
        "risk_low": "🟢 Төмен қауіп", "risk_med": "🟡 Орташа қауіп",
        "risk_hi": "🔴 ЖОҒАРЫ ҚАУІП",
        "map_layer": "Карта қабатын таңдаңыз",
        "map_zoom": "Масштаб (zoom)",
        "prompt": (
            "Сен табиғи апаттар бойынша ЖИ-сарапшысысың. "
            "Төмендегі ауа райы деректері бойынша апат қаупін қазақша бағала "
            "(дауыл, су тасқыны, аптап, өрт қаупі т.б.) және нақты "
            "алдын алу ұсыныстарын бер:\n\n{data}"
        ),
    },
    "ru": {
        "title": "🌍 Guardian AI Weather PRO",
        "subtitle": "ИИ-система прогнозирования стихийных бедствий",
        "city_label": "Введите название города",
        "city_ph": "Например: Алматы",
        "btn": "🔍 Анализ",
        "select": "Уточните город:",
        "loading": "Загрузка данных...",
        "err": "Город не найден.",
        "weather": "🌤 Погода",
        "risk": "⚠️ Оценка риска",
        "aqi": "💨 AQI",
        "uv": "☀️ УФ-индекс",
        "h24": "🕐 24 часа",
        "h7": "📅 7 дней",
        "map": "🗺️ Интерактивная карта Windy",
        "ai": "🤖 Анализ ИИ",
        "no_api": "⚠️ Введите ключ OpenAI API.",
        "high_warn": "🚨 Риск ≥ 60%! Немедленно примите меры безопасности!",
        "aqi_good": "✅ Хорошо", "aqi_med": "🟡 Умеренно", "aqi_bad": "🔴 Вредно",
        "uv_low": "🟢 Низкий", "uv_med": "🟡 Умеренный", "uv_hi": "🟠 Высокий",
        "uv_vhi": "🔴 Очень высокий", "uv_ex": "🟣 Экстремальный",
        "risk_low": "🟢 Низкий риск", "risk_med": "🟡 Умеренный риск",
        "risk_hi": "🔴 ВЫСОКИЙ РИСК",
        "map_layer": "Выберите слой карты",
        "map_zoom": "Масштаб (zoom)",
        "prompt": (
            "Ты ИИ-эксперт по стихийным бедствиям. "
            "Оцени риск катастрофы по данным о погоде на русском языке "
            "(буря, наводнение, жара, пожар и др.) и дай рекомендации:\n\n{data}"
        ),
    },
    "en": {
        "title": "🌍 Guardian AI Weather PRO",
        "subtitle": "AI-Powered Natural Disaster Prediction Platform",
        "city_label": "Enter city name",
        "city_ph": "E.g.: Almaty",
        "btn": "🔍 Analyze",
        "select": "Select a location:",
        "loading": "Loading data...",
        "err": "City not found.",
        "weather": "🌤 Weather",
        "risk": "⚠️ Risk Assessment",
        "aqi": "💨 AQI",
        "uv": "☀️ UV Index",
        "h24": "🕐 24 Hours",
        "h7": "📅 7 Days",
        "map": "🗺️ Windy Interactive Map",
        "ai": "🤖 AI Analysis",
        "no_api": "⚠️ Enter your OpenAI API key.",
        "high_warn": "🚨 Risk ≥ 60%! Take immediate safety measures!",
        "aqi_good": "✅ Good", "aqi_med": "🟡 Moderate", "aqi_bad": "🔴 Harmful",
        "uv_low": "🟢 Low", "uv_med": "🟡 Moderate", "uv_hi": "🟠 High",
        "uv_vhi": "🔴 Very High", "uv_ex": "🟣 Extreme",
        "risk_low": "🟢 Low Risk", "risk_med": "🟡 Moderate Risk",
        "risk_hi": "🔴 HIGH RISK",
        "map_layer": "Select map layer",
        "map_zoom": "Zoom level",
        "prompt": (
            "You are an AI expert in natural disasters. "
            "Evaluate disaster risk based on the following weather data "
            "(storm, flood, heatwave, wildfire, etc.) and give recommendations:\n\n{data}"
        ),
    },
}

# ══════════════════════════════════════════════════════════════
# WINDY ҚАБАТТАРЫ / WINDY LAYERS
# ══════════════════════════════════════════════════════════════
WINDY_LAYERS = {
    "💨 Жел / Wind":             "wind",
    "🌡️ Температура / Temp":    "temp",
    "☁️ Бұлттылық / Clouds":    "clouds",
    "🌧️ Жаңбыр / Rain":         "rain",
    "❄️ Қар / Snow":             "snowcover",
    "🌨️ Жаңбыр+Қар / RainAccum":"rainAccum",
    "💧 Ылғалдылық / Humidity":  "humidity",
    "⚡ Найзағай / Thunder":      "thunder",
    "🌫️ Тұман/Түтін / Smoke":   "smoke",
    "🔵 Атм.қысым / Pressure":   "pressure",
    "🌊 Толқын / Waves":         "waves",
    "🌡️ Теңіз темп. / SST":     "sst",
}

# ══════════════════════════════════════════════════════════════
# УТИЛИТАЛАР / UTILITIES
# ══════════════════════════════════════════════════════════════

def geocode(city: str) -> list[dict]:
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": city, "format": "json", "limit": 10, "addressdetails": 1},
            headers={"User-Agent": "GuardianAIWeatherPRO/3.0"},
            timeout=10,
        )
        out = []
        for item in r.json():
            addr = item.get("address", {})
            out.append({
                "label": item.get("display_name", "—"),
                "lat": float(item["lat"]),
                "lon": float(item["lon"]),
                "city": addr.get("city") or addr.get("town") or addr.get("village") or city,
                "country": addr.get("country", ""),
            })
        return out
    except Exception:
        return []


def fetch_weather(lat: float, lon: float) -> dict | None:
    try:
        return requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat, "longitude": lon,
                "current": ["temperature_2m","relative_humidity_2m","wind_speed_10m",
                            "wind_gusts_10m","precipitation","weather_code",
                            "uv_index","cloud_cover"],
                "hourly": ["temperature_2m","precipitation_probability","wind_speed_10m"],
                "daily":  ["temperature_2m_max","temperature_2m_min","precipitation_sum",
                           "wind_speed_10m_max","uv_index_max","weather_code"],
                "timezone": "auto", "forecast_days": 7,
            },
            timeout=15,
        ).json()
    except Exception:
        return None


def fetch_aqi(lat: float, lon: float) -> int | None:
    try:
        return requests.get(
            "https://air-quality-api.open-meteo.com/v1/air-quality",
            params={"latitude": lat, "longitude": lon,
                    "current": ["european_aqi"], "timezone": "auto"},
            timeout=10,
        ).json().get("current", {}).get("european_aqi")
    except Exception:
        return None


def aqi_label(v, t):
    if v is None: return "—"
    if v < 50:   return t["aqi_good"]
    if v < 100:  return t["aqi_med"]
    return t["aqi_bad"]


def uv_label(v, t):
    if v is None: return "—"
    if v <= 2:   return t["uv_low"]
    if v <= 5:   return t["uv_med"]
    if v <= 7:   return t["uv_hi"]
    if v <= 10:  return t["uv_vhi"]
    return t["uv_ex"]


def risk_score(cur: dict) -> int:
    """
    Апат қаупін бағалау алгоритмі.
    Қауіп ≥ 60 → Жоғары қауіп ескертуі.
    """
    s = 0
    wind  = cur.get("wind_speed_10m", 0) or 0
    gusts = cur.get("wind_gusts_10m", 0) or 0
    rain  = cur.get("precipitation", 0) or 0
    hum   = cur.get("relative_humidity_2m", 0) or 0
    temp  = cur.get("temperature_2m", 20) or 20
    uv    = cur.get("uv_index", 0) or 0
    cld   = cur.get("cloud_cover", 0) or 0

    if wind > 100 or gusts > 120: s += 35
    elif wind > 70 or gusts > 90: s += 25
    elif wind > 50:                s += 15
    elif wind > 30:                s += 8

    if rain > 30:   s += 30
    elif rain > 15: s += 20
    elif rain > 5:  s += 10

    if hum > 92: s += 10
    elif hum > 80: s += 5

    if temp >= 45 or temp <= -40:   s += 20
    elif temp >= 40 or temp <= -30: s += 12
    elif temp >= 36 or temp <= -20: s += 6

    if uv >= 11: s += 10
    elif uv >= 8: s += 6
    elif uv >= 6: s += 3

    if cld > 85 and rain > 5: s += 5

    return min(s, 100)


def risk_label(score: int, t: dict) -> str:
    if score >= 60: return t["risk_hi"]
    if score >= 30: return t["risk_med"]
    return t["risk_low"]


def wmo_icon(code: int) -> str:
    if code == 0:            return "☀️"
    if code in (1, 2, 3):   return "⛅"
    if code in range(45,50): return "🌫️"
    if code in range(51,68): return "🌧️"
    if code in range(71,78): return "❄️"
    if code in range(80,90): return "⛈️"
    if code in range(95,100):return "🌩️"
    return "🌡️"


def windy_iframe(lat: float, lon: float, layer: str, zoom: int) -> str:
    """Windy embed iframe HTML-ін қайтарады."""
    return f"""
<iframe
  src="https://embed.windy.com/embed2.html?lat={lat:.4f}&lon={lon:.4f}&detailLat={lat:.4f}&detailLon={lon:.4f}&width=650&height=480&zoom={zoom}&level=surface&overlay={layer}&product=ecmwf&menu=&message=true&marker=true&calendar=now&pressure=true&type=map&location=coordinates&detail=&metricWind=km%2Fh&metricTemp=%C2%B0C&radarRange=-1"
  width="100%" height="500"
  frameborder="0"
  style="border-radius:12px; box-shadow:0 4px 20px rgba(0,0,0,0.15);"
></iframe>
"""


def ai_analysis(summary: str, prompt_tpl: str, api_key: str) -> str:
    try:
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt_tpl.format(data=summary)}],
            max_tokens=700,
            temperature=0.4,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"ЖИ қатесі / AI Error: {e}"


# ══════════════════════════════════════════════════════════════
# STREAMLIT ҚОСЫМШАСЫ
# ══════════════════════════════════════════════════════════════

def main():
    st.set_page_config(page_title="Guardian AI Weather PRO", page_icon="🌍", layout="wide")
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # ── Sidebar ──────────────────────────────────────────────
    st.sidebar.title("🌍 Guardian AI")
    lang_code = st.sidebar.selectbox(
        "🌐 Тіл / Язык / Language",
        ["kk", "ru", "en"],
        format_func=lambda x: {"kk":"🇰🇿 Қазақша","ru":"🇷🇺 Русский","en":"🇬🇧 English"}[x],
    )
    t = LANG[lang_code]

    st.sidebar.markdown("---")
    api_key = st.sidebar.text_input("🔑 OpenAI API Key", type="password", placeholder="sk-...")

    st.sidebar.markdown("---")
    st.sidebar.markdown("**🗺️ Windy Карта**")
    layer_name = st.sidebar.selectbox(t["map_layer"], list(WINDY_LAYERS.keys()))
    layer_code = WINDY_LAYERS[layer_name]
    zoom = st.sidebar.slider(t["map_zoom"], 3, 12, 7)

    st.sidebar.markdown("---")
    st.sidebar.caption("👨‍💻 Арслан Өмен · Иманғали Құрбанбек\n\n👩‍🏫 Жетекші: Н.Әсілбай\n\n🏫 Төлеби ауданы, 9-сынып")

    # ── Header ───────────────────────────────────────────────
    st.title(t["title"])
    st.caption(t["subtitle"])
    st.markdown("---")

    # ── Search ───────────────────────────────────────────────
    col_in, col_btn = st.columns([5, 1])
    with col_in:
        city_in = st.text_input(t["city_label"], placeholder=t["city_ph"], label_visibility="collapsed")
    with col_btn:
        clicked = st.button(t["btn"], use_container_width=True)

    if not (city_in and clicked):
        st.info("👆 " + t["city_label"])
        # Still show a default Windy map centered on Kazakhstan
        st.subheader(t["map"])
        components.html(windy_iframe(48.0, 68.0, layer_code, 4), height=520)
        return

    # ── Geocoding ────────────────────────────────────────────
    with st.spinner(t["loading"]):
        candidates = geocode(city_in)
    if not candidates:
        st.error(t["err"])
        return

    if len(candidates) > 1:
        chosen_label = st.selectbox(t["select"], [c["label"] for c in candidates])
        chosen = next(c for c in candidates if c["label"] == chosen_label)
    else:
        chosen = candidates[0]

    lat, lon = chosen["lat"], chosen["lon"]
    city_title = chosen["city"] + (f", {chosen['country']}" if chosen["country"] else "")

    # ── Fetch data ───────────────────────────────────────────
    with st.spinner(t["loading"]):
        weather = fetch_weather(lat, lon)
        aqi_val = fetch_aqi(lat, lon)

    if not weather or "current" not in weather:
        st.error("API қатесі. Кейінірек қайталаңыз.")
        return

    cur    = weather["current"]
    temp   = cur.get("temperature_2m", "—")
    hum    = cur.get("relative_humidity_2m", "—")
    wind   = cur.get("wind_speed_10m", "—")
    gusts  = cur.get("wind_gusts_10m", "—")
    rain   = cur.get("precipitation", "—")
    uv     = cur.get("uv_index", "—")
    clouds = cur.get("cloud_cover", "—")
    wcode  = cur.get("weather_code", 0) or 0

    score  = risk_score(cur)
    rlabel = risk_label(score, t)
    alabel = aqi_label(aqi_val, t)
    uvnum  = uv if uv != "—" else None
    ulabel = uv_label(uvnum, t)

    # ══════════════════════════════════════════════════════════
    # МЕТРИКАЛАР
    # ══════════════════════════════════════════════════════════
    st.subheader(f"📍 {city_title}  (lat: {lat:.4f}, lon: {lon:.4f})")
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric(f"{wmo_icon(wcode)} Температура", f"{temp} °C")
    c2.metric("💧 Ылғалдылық", f"{hum} %")
    c3.metric("🌬️ Жел", f"{wind} km/h", f"💨 {gusts} km/h")
    c4.metric("🌧️ Жауын", f"{rain} mm")
    c5.metric("☀️ UV", str(uv))
    c6.metric("☁️ Бұлт", f"{clouds} %")
    st.markdown("---")

    # ══════════════════════════════════════════════════════════
    # ҚАУІП + AQI + UV
    # ══════════════════════════════════════════════════════════
    cr, ca, cu = st.columns(3)
    with cr:
        st.subheader(t["risk"])
        st.progress(score / 100)
        st.markdown(f"**{rlabel}** ({score}/100)")
        if score >= 60:
            st.error(t["high_warn"])
    with ca:
        st.subheader(t["aqi"])
        if aqi_val is not None:
            st.progress(min(aqi_val, 200) / 200)
            st.markdown(f"**{alabel}** (AQI: {aqi_val})")
        else:
            st.info("AQI деректері жоқ.")
    with cu:
        st.subheader(t["uv"])
        if uvnum is not None:
            st.progress(min(float(uvnum), 12) / 12)
            st.markdown(f"**{ulabel}** (UV: {uvnum})")
        else:
            st.info("UV деректері жоқ.")
    st.markdown("---")

    # ══════════════════════════════════════════════════════════
    # 24 САҒАТ
    # ══════════════════════════════════════════════════════════
    st.subheader(t["h24"])
    hourly = weather.get("hourly", {})
    if hourly:
        hrs    = hourly.get("time", [])[:24]
        h_t    = hourly.get("temperature_2m", [])[:24]
        h_pp   = hourly.get("precipitation_probability", [])[:24]
        h_w    = hourly.get("wind_speed_10m", [])[:24]
        labels = [h[11:16] for h in hrs]
        hdf = pd.DataFrame({
            "Temp (°C)": h_t,
            "Жауын ықт. (%)": h_pp,
            "Жел (km/h)": h_w,
        }, index=labels)
        st.line_chart(hdf[["Temp (°C)"]])
        with st.expander("📊 Толық 24h кесте"):
            st.dataframe(hdf, use_container_width=True)
    st.markdown("---")

    # ══════════════════════════════════════════════════════════
    # 7 КҮН
    # ══════════════════════════════════════════════════════════
    st.subheader(t["h7"])
    daily = weather.get("daily", {})
    if daily:
        df7 = pd.DataFrame({
            "📅 Күн": daily.get("time", []),
            "☁️": [wmo_icon(c) for c in daily.get("weather_code", [])],
            "🌡️ Max (°C)": daily.get("temperature_2m_max", []),
            "🌡️ Min (°C)": daily.get("temperature_2m_min", []),
            "🌧️ Жауын (mm)": daily.get("precipitation_sum", []),
            "🌬️ Жел max (km/h)": daily.get("wind_speed_10m_max", []),
            "☀️ UV max": daily.get("uv_index_max", []),
        })
        st.dataframe(df7, use_container_width=True, hide_index=True)
        cdf = pd.DataFrame({
            "Max °C": daily.get("temperature_2m_max", []),
            "Min °C": daily.get("temperature_2m_min", []),
        }, index=daily.get("time", []))
        st.line_chart(cdf)
    st.markdown("---")

    # ══════════════════════════════════════════════════════════
    # 🗺️ WINDY ИНТЕРАКТИВТІ КАРТА
    # ══════════════════════════════════════════════════════════
    st.subheader(t["map"])

    # Layer quick-select chips (columns)
    layer_cols = st.columns(6)
    quick_layers = [
        ("💨 Жел", "wind"), ("🌧️ Жаңбыр", "rain"), ("❄️ Қар", "snowcover"),
        ("☁️ Бұлт", "clouds"), ("⚡ Найзағай", "thunder"), ("🌡️ Темп.", "temp"),
    ]
    for i, (label, code) in enumerate(quick_layers):
        if layer_cols[i].button(label, use_container_width=True):
            layer_code = code
            layer_name = label

    st.markdown(f"**Таңдалған қабат / Текущий слой:** `{layer_name}` — `{layer_code}`")

    components.html(windy_iframe(lat, lon, layer_code, zoom), height=520)

    # Info about all available layers
    with st.expander("📋 Барлық Windy қабаттары / All Windy layers"):
        layer_df = pd.DataFrame([
            {"Белгіше": k.split()[0], "Қабат": " ".join(k.split()[1:]), "Код (API)": v}
            for k, v in WINDY_LAYERS.items()
        ])
        st.dataframe(layer_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ══════════════════════════════════════════════════════════
    # 🤖 ЖИ САРАПТАМАСЫ
    # ══════════════════════════════════════════════════════════
    st.subheader(t["ai"])
    if not api_key:
        st.warning(t["no_api"])
    else:
        summary = (
            f"Қала/City: {city_title}\n"
            f"Уақыт/Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"Температура: {temp}°C\n"
            f"Ылғалдылық: {hum}%\n"
            f"Жел: {wind} km/h (соғысы: {gusts} km/h)\n"
            f"Жауын: {rain} mm\n"
            f"UV: {uv}\n"
            f"Бұлттылық: {clouds}%\n"
            f"AQI: {aqi_val}\n"
            f"Қауіп ұпайы/Risk score: {score}/100\n"
            f"Қауіп деңгейі: {rlabel}\n"
        )
        with st.spinner("ЖИ талдауда..."):
            result = ai_analysis(summary, t["prompt"], api_key)
        st.info(result)

    # ── Footer ───────────────────────────────────────────────
    st.markdown("---")
    st.caption(
        "**Guardian AI Weather PRO** | Арслан Өмен · Иманғали Құрбанбек | "
        "Жетекші: Н.Әсілбай | Төлеби ауданы мектеп-интернаты, 9-сынып | "
        "🌐 [guardianaiweatherpro.streamlit.app](https://guardianaiweatherpro.streamlit.app/)"
    )


if __name__ == "__main__":
    main()
