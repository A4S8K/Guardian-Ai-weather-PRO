"""
Guardian AI Weather PRO
========================
Табиғи апаттарды ЖИ арқылы болжайтын веб-платформа.
Авторлар: Арслан Өмен, Иманғали Құрбанбек
Мектеп: Төлеби ауданының мамандандырылған мектеп-интернаты, 9-сынып
Жетекші: Н.Әсілбай, математика пәні мұғалімі
Сілтеме: https://guardianaiweatherpro.streamlit.app/
"""

import streamlit as st
import requests
import pandas as pd
from openai import OpenAI
from datetime import datetime

# ══════════════════════════════════════════════════════════════════
# ТІЛДЕР / LANGUAGES
# ══════════════════════════════════════════════════════════════════
TRANSLATIONS = {
    "kk": {
        "title": "🌍 Guardian AI Weather PRO",
        "subtitle": "Табиғи апаттарды ЖИ арқылы болжау жүйесі",
        "city_label": "Қала атын енгізіңіз",
        "city_placeholder": "Мысалы: Алматы",
        "analyze_btn": "🔍 Талдау",
        "select_city": "Қаланы таңдаңыз:",
        "weather_header": "🌤 Ауа райы деректері",
        "risk_header": "⚠️ Апат қаупін бағалау",
        "ai_header": "🤖 ЖИ сараптамасы",
        "forecast_7_header": "📅 7 күндік болжам",
        "forecast_24_header": "🕐 24 сағаттық температура болжамы",
        "aqi_header": "💨 Ауа сапасы (AQI)",
        "uv_header": "☀️ UV индексі",
        "error_city": "Қала табылмады. Тексеріп қайта енгізіңіз.",
        "loading": "Деректер жүктелуде...",
        "temp": "Температура",
        "humidity": "Ылғалдылық",
        "wind": "Жел жылдамдығы",
        "rain": "Жауын-шашын",
        "uv": "UV индексі",
        "lat": "Ендік",
        "lon": "Бойлық",
        "aqi_good": "✅ Жақсы (AQI < 50)",
        "aqi_moderate": "🟡 Орташа (AQI < 100)",
        "aqi_bad": "🔴 Зиянды (AQI > 100)",
        "uv_low": "🟢 Төмен (0–2)",
        "uv_mod": "🟡 Орташа (3–5)",
        "uv_high": "🟠 Жоғары (6–7)",
        "uv_very_high": "🔴 Өте жоғары (8–10)",
        "uv_extreme": "🟣 Экстремалды (11+)",
        "risk_low": "🟢 Төмен қауіп",
        "risk_med": "🟡 Орташа қауіп",
        "risk_high": "🔴 ЖОҒАРЫ ҚАУІП — Алдын алу шараларын қолданыңыз!",
        "high_risk_warning": "🚨 Қауіп деңгейі 60%-дан асты! Дереу сақтық шараларын қолданыңыз.",
        "risk_score": "Қауіп ұпайы",
        "no_api": "⚠️ OpenAI API кілтін сол панелге енгізіңіз.",
        "ai_prompt": (
            "Сен табиғи апаттар бойынша ЖИ-сарапшысысың. "
            "Төмендегі ауа райы деректері бойынша апат қаупін қазақша бағала "
            "(дауыл, су тасқыны, аптап ыстық, өрт қаупі т.б.), "
            "себебін түсіндір және нақты алдын алу ұсыныстарын бер:\n\n{data}"
        ),
    },
    "ru": {
        "title": "🌍 Guardian AI Weather PRO",
        "subtitle": "ИИ-система прогнозирования стихийных бедствий",
        "city_label": "Введите название города",
        "city_placeholder": "Например: Алматы",
        "analyze_btn": "🔍 Анализ",
        "select_city": "Выберите город:",
        "weather_header": "🌤 Данные о погоде",
        "risk_header": "⚠️ Оценка риска катастрофы",
        "ai_header": "🤖 Анализ ИИ",
        "forecast_7_header": "📅 Прогноз на 7 дней",
        "forecast_24_header": "🕐 24-часовой прогноз температуры",
        "aqi_header": "💨 Качество воздуха (AQI)",
        "uv_header": "☀️ УФ-индекс",
        "error_city": "Город не найден. Проверьте и введите снова.",
        "loading": "Загрузка данных...",
        "temp": "Температура",
        "humidity": "Влажность",
        "wind": "Скорость ветра",
        "rain": "Осадки",
        "uv": "УФ-индекс",
        "lat": "Широта",
        "lon": "Долгота",
        "aqi_good": "✅ Хорошо (AQI < 50)",
        "aqi_moderate": "🟡 Умеренно (AQI < 100)",
        "aqi_bad": "🔴 Вредно (AQI > 100)",
        "uv_low": "🟢 Низкий (0–2)",
        "uv_mod": "🟡 Умеренный (3–5)",
        "uv_high": "🟠 Высокий (6–7)",
        "uv_very_high": "🔴 Очень высокий (8–10)",
        "uv_extreme": "🟣 Экстремальный (11+)",
        "risk_low": "🟢 Низкий риск",
        "risk_med": "🟡 Умеренный риск",
        "risk_high": "🔴 ВЫСОКИЙ РИСК — Примите меры предосторожности!",
        "high_risk_warning": "🚨 Риск превысил 60%! Немедленно примите меры безопасности.",
        "risk_score": "Уровень риска",
        "no_api": "⚠️ Введите ключ OpenAI API в левую панель.",
        "ai_prompt": (
            "Ты ИИ-эксперт по стихийным бедствиям. "
            "Оцени риск катастрофы по данным о погоде на русском языке "
            "(буря, наводнение, жара, пожар и др.), "
            "объясни причину и дай конкретные рекомендации:\n\n{data}"
        ),
    },
    "en": {
        "title": "🌍 Guardian AI Weather PRO",
        "subtitle": "AI-Powered Natural Disaster Prediction Platform",
        "city_label": "Enter city name",
        "city_placeholder": "E.g.: Almaty",
        "analyze_btn": "🔍 Analyze",
        "select_city": "Select a city:",
        "weather_header": "🌤 Current Weather",
        "risk_header": "⚠️ Disaster Risk Assessment",
        "ai_header": "🤖 AI Analysis",
        "forecast_7_header": "📅 7-Day Forecast",
        "forecast_24_header": "🕐 24-Hour Temperature Forecast",
        "aqi_header": "💨 Air Quality (AQI)",
        "uv_header": "☀️ UV Index",
        "error_city": "City not found. Please check and try again.",
        "loading": "Loading data...",
        "temp": "Temperature",
        "humidity": "Humidity",
        "wind": "Wind Speed",
        "rain": "Precipitation",
        "uv": "UV Index",
        "lat": "Latitude",
        "lon": "Longitude",
        "aqi_good": "✅ Good (AQI < 50)",
        "aqi_moderate": "🟡 Moderate (AQI < 100)",
        "aqi_bad": "🔴 Harmful (AQI > 100)",
        "uv_low": "🟢 Low (0–2)",
        "uv_mod": "🟡 Moderate (3–5)",
        "uv_high": "🟠 High (6–7)",
        "uv_very_high": "🔴 Very High (8–10)",
        "uv_extreme": "🟣 Extreme (11+)",
        "risk_low": "🟢 Low Risk",
        "risk_med": "🟡 Moderate Risk",
        "risk_high": "🔴 HIGH RISK — Take precautionary measures immediately!",
        "high_risk_warning": "🚨 Risk exceeded 60%! Take immediate safety measures.",
        "risk_score": "Risk Score",
        "no_api": "⚠️ Enter your OpenAI API key in the left panel.",
        "ai_prompt": (
            "You are an AI expert in natural disasters. "
            "Evaluate disaster risk based on the following weather data in English "
            "(storm, flood, heatwave, wildfire, etc.), "
            "explain the reasoning, and give specific prevention recommendations:\n\n{data}"
        ),
    },
}

# ══════════════════════════════════════════════════════════════════
# ГЕОКОДИНГ / GEOCODING
# ══════════════════════════════════════════════════════════════════

def search_cities(city_name: str) -> list[dict]:
    """
    Nominatim арқылы ең ықтимал 10 нұсқаны қайтарады.
    Returns top-10 location candidates.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": city_name, "format": "json", "limit": 10, "addressdetails": 1}
    headers = {"User-Agent": "GuardianAIWeatherPRO/2.0"}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        results = resp.json()
        cities = []
        for r in results:
            addr = r.get("address", {})
            cities.append({
                "label": r.get("display_name", "—"),
                "lat": float(r["lat"]),
                "lon": float(r["lon"]),
                "city": addr.get("city") or addr.get("town") or addr.get("village") or city_name,
                "country": addr.get("country", ""),
            })
        return cities
    except Exception:
        return []

# ══════════════════════════════════════════════════════════════════
# OPEN-METEO API
# ══════════════════════════════════════════════════════════════════

def fetch_weather(lat: float, lon: float) -> dict | None:
    """Нақты уақыт + 24 сағат + 7 күн болжамын алу."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": [
            "temperature_2m", "relative_humidity_2m",
            "wind_speed_10m", "wind_gusts_10m",
            "precipitation", "weather_code",
            "uv_index", "cloud_cover",
        ],
        "hourly": [
            "temperature_2m",
            "precipitation_probability",
            "wind_speed_10m",
        ],
        "daily": [
            "temperature_2m_max", "temperature_2m_min",
            "precipitation_sum", "wind_speed_10m_max",
            "uv_index_max", "weather_code",
        ],
        "timezone": "auto",
        "forecast_days": 7,
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        return resp.json()
    except Exception:
        return None


def fetch_aqi(lat: float, lon: float) -> int | None:
    """AQI алу."""
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {"latitude": lat, "longitude": lon, "current": ["european_aqi"], "timezone": "auto"}
    try:
        resp = requests.get(url, params=params, timeout=10)
        return resp.json().get("current", {}).get("european_aqi")
    except Exception:
        return None

# ══════════════════════════════════════════════════════════════════
# АЛГОРИТМДЕР / ALGORITHMS
# ══════════════════════════════════════════════════════════════════

def evaluate_aqi(aqi: int | None, t: dict) -> str:
    """AQI шартты логикасы (docx алгоритмі): <50 Жақсы | <100 Орташа | >100 Зиянды."""
    if aqi is None:
        return "—"
    if aqi < 50:
        return t["aqi_good"]
    elif aqi < 100:
        return t["aqi_moderate"]
    else:
        return t["aqi_bad"]


def evaluate_uv(uv: float | None, t: dict) -> str:
    """UV индексін бағалау."""
    if uv is None:
        return "—"
    if uv <= 2:
        return t["uv_low"]
    elif uv <= 5:
        return t["uv_mod"]
    elif uv <= 7:
        return t["uv_high"]
    elif uv <= 10:
        return t["uv_very_high"]
    else:
        return t["uv_extreme"]


def evaluate_risk(current: dict, t: dict) -> tuple[str, int]:
    """
    Апат қаупін бағалау алгоритмі (docx бойынша).
    Параметрлер: температура, жел, жел соғысы, ылғалдылық, UV, жаңбыр, бұлттылық.
    Қауіп >= 60% → ЖОҒАРЫ ҚАУІП (docx: «Қауіп деңгейі 60%-дан асса, жоғары қауіп туралы ескерту шығады»).
    """
    score = 0
    wind   = current.get("wind_speed_10m", 0) or 0
    gusts  = current.get("wind_gusts_10m", 0) or 0
    rain   = current.get("precipitation", 0) or 0
    hum    = current.get("relative_humidity_2m", 0) or 0
    temp   = current.get("temperature_2m", 20) or 20
    uv     = current.get("uv_index", 0) or 0
    clouds = current.get("cloud_cover", 0) or 0

    # Жел / Wind — дауыл қаупі
    if wind > 100 or gusts > 120:
        score += 35
    elif wind > 70 or gusts > 90:
        score += 25
    elif wind > 50:
        score += 15
    elif wind > 30:
        score += 8

    # Жауын-шашын / Precipitation — су тасқыны қаупі
    if rain > 30:
        score += 30
    elif rain > 15:
        score += 20
    elif rain > 5:
        score += 10

    # Ылғалдылық / Humidity
    if hum > 92:
        score += 10
    elif hum > 80:
        score += 5

    # Температура шегі — аптап / аяз қаупі
    if temp >= 45 or temp <= -40:
        score += 20
    elif temp >= 40 or temp <= -30:
        score += 12
    elif temp >= 36 or temp <= -20:
        score += 6

    # UV индексі — өрт + денсаулық қаупі
    if uv >= 11:
        score += 10
    elif uv >= 8:
        score += 6
    elif uv >= 6:
        score += 3

    # Бұлттылық + жауын — жайын қаупі
    if clouds > 85 and rain > 5:
        score += 5

    score = min(score, 100)

    if score >= 60:
        label = t["risk_high"]
    elif score >= 30:
        label = t["risk_med"]
    else:
        label = t["risk_low"]

    return label, score


def get_ai_analysis(summary: str, prompt_template: str, api_key: str) -> str:
    """OpenAI GPT-4o-mini сараптамасы."""
    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt_template.format(data=summary)}],
            max_tokens=700,
            temperature=0.4,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"ЖИ қатесі / AI Error: {e}"


def wmo_icon(code: int) -> str:
    if code == 0:
        return "☀️"
    elif code in (1, 2, 3):
        return "⛅"
    elif code in range(45, 50):
        return "🌫️"
    elif code in range(51, 68):
        return "🌧️"
    elif code in range(71, 78):
        return "❄️"
    elif code in range(80, 90):
        return "⛈️"
    elif code in range(95, 100):
        return "🌩️"
    else:
        return "🌡️"

# ══════════════════════════════════════════════════════════════════
# STREAMLIT ҚОСЫМШАСЫ / MAIN APP
# ══════════════════════════════════════════════════════════════════

def main():
    st.set_page_config(page_title="Guardian AI Weather PRO", page_icon="🌍", layout="wide")

    # ── Сол панел / Sidebar ────────────────────────────────────────
    st.sidebar.title("🌍 Guardian AI")
    lang = st.sidebar.selectbox(
        "🌐 Тіл / Язык / Language",
        options=["kk", "ru", "en"],
        format_func=lambda x: {"kk": "🇰🇿 Қазақша", "ru": "🇷🇺 Русский", "en": "🇬🇧 English"}[x],
    )
    t = TRANSLATIONS[lang]

    st.sidebar.markdown("---")
    api_key = st.sidebar.text_input("🔑 OpenAI API Key", type="password", placeholder="sk-...")
    st.sidebar.markdown("---")
    st.sidebar.caption(
        "👨‍💻 Арслан Өмен · Иманғали Құрбанбек\n\n"
        "🏫 Төлеби ауданы, 9-сынып\n\n"
        "👩‍🏫 Жетекші: Н.Әсілбай"
    )

    # ── Тақырып ───────────────────────────────────────────────────
    st.title(t["title"])
    st.caption(t["subtitle"])
    st.markdown("---")

    # ── Іздеу / Search ────────────────────────────────────────────
    col_inp, col_btn = st.columns([5, 1])
    with col_inp:
        city_input = st.text_input(
            t["city_label"], placeholder=t["city_placeholder"], label_visibility="collapsed"
        )
    with col_btn:
        clicked = st.button(t["analyze_btn"], use_container_width=True)

    if not (city_input and clicked):
        st.info("👆 " + t["city_label"])
        return

    # ── Геокодинг (10 нұсқа / 10 candidates) ─────────────────────
    with st.spinner(t["loading"]):
        candidates = search_cities(city_input)

    if not candidates:
        st.error(t["error_city"])
        return

    if len(candidates) > 1:
        chosen_label = st.selectbox(t["select_city"], [c["label"] for c in candidates])
        chosen = next(c for c in candidates if c["label"] == chosen_label)
    else:
        chosen = candidates[0]

    lat, lon = chosen["lat"], chosen["lon"]
    city_title = chosen["city"] + (f", {chosen['country']}" if chosen["country"] else "")

    # ── Деректер / Data fetch ─────────────────────────────────────
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

    risk_label, risk_score = evaluate_risk(cur, t)
    aqi_label = evaluate_aqi(aqi_val, t)
    uv_num    = uv if uv != "—" else None
    uv_label  = evaluate_uv(uv_num, t)

    # ── Метрикалар / Metrics ──────────────────────────────────────
    st.subheader(f"📍 {city_title}  ({t['lat']}: {lat:.4f}, {t['lon']}: {lon:.4f})")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric(f"{wmo_icon(wcode)} {t['temp']}", f"{temp} °C")
    c2.metric(f"💧 {t['humidity']}", f"{hum} %")
    c3.metric(f"🌬️ {t['wind']}", f"{wind} km/h", f"💨 {gusts} km/h")
    c4.metric(f"🌧️ {t['rain']}", f"{rain} mm")
    c5.metric(f"☀️ {t['uv']}", str(uv))
    c6.metric("☁️ Бұлт/Cloud", f"{clouds} %")
    st.markdown("---")

    # ── Қауіп + AQI + UV ──────────────────────────────────────────
    cr, ca, cu = st.columns(3)
    with cr:
        st.subheader(t["risk_header"])
        st.progress(risk_score / 100)
        st.markdown(f"**{risk_label}**")
        st.caption(f"{t['risk_score']}: {risk_score}/100")
        if risk_score >= 60:
            st.error(t["high_risk_warning"])
    with ca:
        st.subheader(t["aqi_header"])
        if aqi_val is not None:
            st.progress(min(aqi_val, 200) / 200)
            st.markdown(f"**{aqi_label}**")
            st.caption(f"AQI: {aqi_val}")
        else:
            st.info("AQI деректері жоқ.")
    with cu:
        st.subheader(t["uv_header"])
        if uv_num is not None:
            st.progress(min(float(uv_num), 12) / 12)
            st.markdown(f"**{uv_label}**")
            st.caption(f"UV: {uv_num}")
        else:
            st.info("UV деректері жоқ.")
    st.markdown("---")

    # ── 24 сағаттық болжам / 24-hour forecast ────────────────────
    st.subheader(t["forecast_24_header"])
    hourly = weather.get("hourly", {})
    if hourly:
        hours   = hourly.get("time", [])[:24]
        h_temps = hourly.get("temperature_2m", [])[:24]
        h_prec  = hourly.get("precipitation_probability", [])[:24]
        h_wind  = hourly.get("wind_speed_10m", [])[:24]
        h_labels = [h[11:16] for h in hours]  # "HH:MM"

        h_df = pd.DataFrame(
            {f"{t['temp']} (°C)": h_temps, "Жауын/Precip. prob. (%)": h_prec, f"{t['wind']} (km/h)": h_wind},
            index=h_labels,
        )
        st.line_chart(h_df[[f"{t['temp']} (°C)"]])
        with st.expander("📊 Толық 24 сағаттық кесте / Full 24h table"):
            st.dataframe(h_df, use_container_width=True)
    st.markdown("---")

    # ── 7 күндік болжам / 7-day forecast ─────────────────────────
    st.subheader(t["forecast_7_header"])
    daily = weather.get("daily", {})
    if daily:
        df7 = pd.DataFrame({
            "📅 Күн": daily.get("time", []),
            "☁️": [wmo_icon(c) for c in daily.get("weather_code", [])],
            "🌡️ Max (°C)": daily.get("temperature_2m_max", []),
            "🌡️ Min (°C)": daily.get("temperature_2m_min", []),
            "🌧️ Жауын/Rain (mm)": daily.get("precipitation_sum", []),
            "🌬️ Жел/Wind max (km/h)": daily.get("wind_speed_10m_max", []),
            "☀️ UV max": daily.get("uv_index_max", []),
        })
        st.dataframe(df7, use_container_width=True, hide_index=True)
        chart_df = pd.DataFrame(
            {"Max °C": daily.get("temperature_2m_max", []), "Min °C": daily.get("temperature_2m_min", [])},
            index=daily.get("time", []),
        )
        st.line_chart(chart_df)
    st.markdown("---")

    # ── ЖИ сараптамасы / AI Analysis ──────────────────────────────
    st.subheader(t["ai_header"])
    if not api_key:
        st.warning(t["no_api"])
    else:
        summary = (
            f"Қала/City: {city_title}\n"
            f"Уақыт/Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"Температура/Temperature: {temp}°C\n"
            f"Ылғалдылық/Humidity: {hum}%\n"
            f"Жел/Wind: {wind} km/h (соғысы/gusts: {gusts} km/h)\n"
            f"Жауын/Precipitation: {rain} mm\n"
            f"UV индексі/UV index: {uv}\n"
            f"Бұлттылық/Cloud cover: {clouds}%\n"
            f"AQI: {aqi_val}\n"
            f"Қауіп ұпайы/Risk score: {risk_score}/100\n"
            f"Қауіп деңгейі/Risk level: {risk_label}\n"
        )
        with st.spinner("ЖИ талдауда... / AI analyzing..."):
            analysis = get_ai_analysis(summary, t["ai_prompt"], api_key)
        st.info(analysis)

    # ── Футер ──────────────────────────────────────────────────────
    st.markdown("---")
    st.caption(
        "**Guardian AI Weather PRO** | "
        "Арслан Өмен · Иманғали Құрбанбек | "
        "Жетекші: Н.Әсілбай | "
        "Төлеби ауданының мамандандырылған мектеп-интернаты, 9-сынып | "
        "🌐 [guardianaiweatherpro.streamlit.app](https://guardianaiweatherpro.streamlit.app/)"
    )


if __name__ == "__main__":
    main()
