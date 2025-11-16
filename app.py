# app.py
import streamlit as st

from config import (
    ALL_TICKERS,
    SPY_TICKER,
    VOLATILITY_WINDOW,
    MOMENTUM_WINDOW,
)
from core.openai_client import get_client, call_llm
from core.financial_data import (
    download_all_tickers,
    intraday_high_low,
    compute_volatility,
    compute_momentum,
    seasonality_by_month,
)
from core.news_fetcher import (
    fetch_news_for_ticker,
    format_news_for_prompt,
)
from core.analysis_engine import (
    generate_macro_context,
    format_context_for_llm,
)

# -----------------------------
# CONFIGURACIÓN BÁSICA STREAMLIT
# -----------------------------
st.set_page_config(
    page_title="FinChat 🤖",
    page_icon="📈",
    layout="wide"
)

# -----------------------------
# ESTILOS CUSTOM (UI)
# -----------------------------
custom_css = """
<style>
.main {
    background: radial-gradient(circle at top left, #1f2937, #020617);
}
.chat-container {
    background: rgba(15, 23, 42, 0.85);
    border-radius: 24px;
    padding: 1.8rem 2.2rem;
    box-shadow: 0 20px 40px rgba(0,0,0,0.5);
    border: 1px solid rgba(148, 163, 184, 0.3);
}
.app-title {
    font-size: 2.4rem;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg, #38bdf8, #a855f7, #f97316);
    -webkit-background-clip: text;
    color: transparent;
    letter-spacing: 0.04em;
    margin-bottom: 0.2rem;
}
.app-subtitle {
    text-align: center;
    color: #e5e7eb;
    font-size: 0.95rem;
    opacity: 0.85;
    margin-bottom: 1.5rem;
}
.msg-user, .msg-bot {
    padding: 0.8rem 1rem;
    border-radius: 18px;
    margin-bottom: 0.4rem;
    max-width: 100%;
    font-size: 0.94rem;
    line-height: 1.5;
}
.msg-user {
    background: linear-gradient(135deg, #22c55e, #4ade80);
    color: #022c22;
    margin-left: auto;
}
.msg-bot {
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(148, 163, 184, 0.6);
    color: #e5e7eb;
    margin-right: auto;
}
.msg-label-user {
    font-size: 0.7rem;
    color: #a5b4fc;
    text-align: right;
    margin-bottom: 0.15rem;
}
.msg-label-bot {
    font-size: 0.7rem;
    color: #f97316;
    text-align: left;
    margin-bottom: 0.15rem;
}
.chat-history {
    max-height: 410px;
    overflow-y: auto;
    padding-right: 0.4rem;
}
.chat-history::-webkit-scrollbar {
    width: 6px;
}
.chat-history::-webkit-scrollbar-thumb {
    background: #4b5563;
    border-radius: 999px;
}
.stButton > button {
    width: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #38bdf8, #a855f7) !important;
    border: none;
    color: white;
    font-weight: 600;
    padding: 0.5rem 0 !important;
    box-shadow: 0 10px 25px rgba(15,23,42,0.8);
}
.stButton > button:hover {
    transform: translateY(-1px) scale(1.01);
    box-shadow: 0 14px 30px rgba(15,23,42,1);
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# -----------------------------
# ESTADO DE SESIÓN
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "¡Hola! Soy tu asistente de análisis bursátil 📈🤖.\n\n"
                "Puedo ayudarte con SPY y las 7 Magníficas: volatilidad, momentum, "
                "máximos/mínimos del día, estacionalidad y noticias.\n\n"
                "Hazme una pregunta o usa el panel derecho para cargar datos y noticias."
            ),
        }
    ]

if "market_data" not in st.session_state:
    st.session_state.market_data = {}

if "news_articles" not in st.session_state:
    st.session_state.news_articles = {}

if "news_summary" not in st.session_state:
    st.session_state.news_summary = {}

if "macro_context" not in st.session_state:
    st.session_state.macro_context = {}

if "macro_summary" not in st.session_state:
    st.session_state.macro_summary = {}

# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    api_key_input = st.text_input("🔑 OpenAI API key", type="password")
    model_name = st.selectbox(
        "🧠 Modelo",
        ["gpt-4.1-mini", "gpt-4o-mini", "gpt-4.1"],
        index=0
    )
    st.markdown("---")
    st.markdown("### 📈 Tickers analizados")
    st.write(", ".join(ALL_TICKERS))

    if st.button("🔄 Descargar datos (SPY + 7)"):
        with st.spinner("Descargando datos históricos..."):
            st.session_state.market_data = download_all_tickers()
        st.success("Datos descargados correctamente ✅")

# -----------------------------
# HEADER
# -----------------------------
st.markdown('<div class="app-title">FinChat 🤖</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">'
    'Asistente de análisis de la bolsa: SPY + 7 Magníficas, con IA generativa. 📊'
    '</div>',
    unsafe_allow_html=True
)
st.write("")

# -----------------------------
# LAYOUT PRINCIPAL
# -----------------------------
col_chat, col_side = st.columns([2.5, 1.5], gap="large")

# --------- COLUMNA CHAT ----------
with col_chat:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    st.markdown("##### 🗨️ Conversación")
    st.markdown('<div class="chat-history">', unsafe_allow_html=True)

    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            st.markdown('<div class="msg-label-bot">FinChat 🤖</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="msg-bot">{msg["content"]}</div>',
                unsafe_allow_html=True,
            )
        elif msg["role"] == "user":
            st.markdown('<div class="msg-label-user">Tú 👤</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="msg-user">{msg["content"]}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)   # cierra chat-history
    st.markdown("</div>", unsafe_allow_html=True)   # cierra chat-container

# --------- COLUMNA DERECHA: DATOS + NOTICIAS + MACRO ----------
with col_side:
    # ---- Datos rápidos SPY ----
    st.markdown("#### 🧮 Datos rápidos de SPY")

    if SPY_TICKER in st.session_state.market_data:
        df_spy = st.session_state.market_data[SPY_TICKER]
        info_day = intraday_high_low(df_spy)
        vol = compute_volatility(df_spy)
        mom = compute_momentum(df_spy)

        st.write(f"**Último día:** {info_day.get('date')}")
        st.write(f"Open: {info_day.get('open'):.2f}")
        st.write(f"High: {info_day.get('high'):.2f}")
        st.write(f"Low: {info_day.get('low'):.2f}")
        st.write(f"Close: {info_day.get('close'):.2f}")
        st.write(f"Volatilidad anualizada {VOLATILITY_WINDOW}d: {vol:.2%}")
        st.write(f"Momentum {MOMENTUM_WINDOW}d: {mom:.2%}")

        st.markdown("##### Estacionalidad por mes (SPY)")
        st.dataframe(seasonality_by_month(df_spy), width="stretch")
    else:
        st.info("Pulsa en el sidebar **🔄 Descargar datos (SPY + 7)** para cargar los datos de mercado.")

    # ---- Noticias ----
    st.markdown("---")
    st.markdown("#### 📰 Noticias por ticker")

    selected_ticker = st.selectbox("Elige un ticker", ALL_TICKERS, index=0)

    if st.button("📰 Cargar noticias de este ticker"):
        with st.spinner(f"Buscando noticias para {selected_ticker}..."):
            articles = fetch_news_for_ticker(selected_ticker, limit=5)
            st.session_state.news_articles[selected_ticker] = articles
        st.success("Noticias cargadas ✅")

    # Mostrar noticias si existen
    articles = st.session_state.news_articles.get(selected_ticker, [])
    if articles:
        for i, art in enumerate(articles, start=1):
            title = art.get("title") or f"Noticia {i}"
            publisher = art.get("publisher") or "Fuente desconocida"
            published = art.get("published")
            subtitle = f"{publisher} — {published}" if published else publisher

            st.markdown(f"**{i}. {title}**")
            st.caption(subtitle)
            if art.get("link"):
                st.markdown(f"[Ver noticia]({art['link']})")
            st.write("")
    else:
        st.caption("No hay noticias cargadas para este ticker todavía.")

    # Botón para resumir noticias con IA
    if articles:
        if st.button("🧠 Resumir noticias con IA"):
            client = get_client(api_key_input)
            if client is None:
                st.error("⚠️ No se encontró API key. Configúrala en el sidebar o en `OPENAI_API_KEY`.")
            else:
                news_text = format_news_for_prompt(selected_ticker, articles)
                system_prompt = (
                    "Eres un analista financiero especializado en bolsa de valores. "
                    "Lee la lista de noticias recientes y devuelve un resumen en español "
                    "en máximo 5 viñetas, destacando lo que más le interesa a un trader intradía "
                    "o swing trader."
                )

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": news_text},
                ]

                with st.spinner("Resumiendo noticias... 🧠"):
                    summary = call_llm(client, messages, model_name=model_name)

                # Guardar en estado y mostrar
                st.session_state.news_summary[selected_ticker] = summary
                # Añadir al chat como mensaje del bot
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Resumen de noticias para {selected_ticker}:\n\n{summary}",
                })
                st.success("Resumen generado ✅")

    # Mostrar último resumen si existe
    last_summary = st.session_state.news_summary.get(selected_ticker)
    if last_summary:
        st.markdown("##### 🧠 Último resumen de noticias")
        st.markdown(last_summary)

    # -----------------------------------
    # 🔍 ANÁLISIS MACRO DEL DÍA (PASO 3)
    # -----------------------------------
    st.markdown("---")
    st.markdown("#### 📊 Análisis macro del día")

    if st.button("📈 Generar análisis macro para este ticker"):
        if selected_ticker not in st.session_state.market_data:
            st.warning(
                f"No hay datos cargados para {selected_ticker}. "
                "Primero pulsa en el sidebar: '🔄 Descargar datos (SPY + 7)'."
            )
        else:
            df_ticker = st.session_state.market_data[selected_ticker]

            with st.spinner(f"Calculando contexto macro para {selected_ticker}..."):
                ctx = generate_macro_context(selected_ticker, df_ticker)
                ctx_text = format_context_for_llm(ctx)

                st.session_state.macro_context[selected_ticker] = ctx
                st.session_state.macro_summary[selected_ticker] = ctx_text

            st.success("Análisis macro generado ✅")

            st.markdown("##### 📌 Resumen estadístico (motor de análisis)")
            st.code(ctx_text, language="markdown")

            # Explicación con IA
            client = get_client(api_key_input)
            if client is None:
                st.info("Configura tu API key para obtener una explicación con IA del análisis macro.")
            else:
                system_prompt_macro = (
                    "Eres un analista financiero profesional. "
                    "A partir de este contexto cuantitativo del mercado, "
                    "explica en español y de forma clara qué significa para un trader diario: "
                    "¿el entorno está más alcista, bajista o neutro?, "
                    "¿qué precauciones tomarías?, ¿cómo resumirías el día en 4-5 frases?"
                )

                messages_macro = [
                    {"role": "system", "content": system_prompt_macro},
                    {"role": "user", "content": ctx_text},
                ]

                with st.spinner("Generando interpretación con IA... 🧠"):
                    explanation = call_llm(client, messages_macro, model_name=model_name)

                st.markdown("##### 🧠 Interpretación con IA")
                st.markdown(explanation)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": (
                        f"Análisis macro del día para {selected_ticker}:\n\n"
                        f"{explanation}"
                    ),
                })

    last_macro = st.session_state.macro_summary.get(selected_ticker)
    if last_macro:
        st.markdown("##### 📌 Último análisis macro generado (resumen estadístico)")
        st.code(last_macro, language="markdown")

# -----------------------------
# INPUT DE CHAT (ABAJO, ESTILO CHATGPT)
# -----------------------------
user_input = st.chat_input("Escribe tu pregunta para FinChat")
# Cuando el usuario envía algo en el chat_input:
if user_input is not None and user_input.strip():
    # Guardar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": user_input})

    client = get_client(api_key_input)
    if client is None:
        st.error("⚠️ No se encontró API key. Configúrala en el sidebar o en la variable de entorno `OPENAI_API_KEY`.")
    else:
        # Prompt base
        base_system = (
            "Eres un asistente experto en mercados financieros, especializado en el ETF SPY "
            "y en las empresas '7 Magníficas' (AAPL, MSFT, NVDA, GOOGL, AMZN, META, TSLA). "
            "Responde en español, de forma clara y pedagógica. "
            "Puedes hablar de volatilidad, momentum, estacionalidad, niveles clave del día "
            "y también interpretar noticias cuando el usuario te comente resúmenes.\n\n"
            "Si te proporciono un contexto cuantitativo (volatilidad, momentum, máximos/mínimos, "
            "estacionalidad), ÚSALO para dar números concretos. "
            "No inventes datos que no estén en ese contexto."
        )

        # Contexto cuantitativo de SPY si está disponible
        extra_context = ""
        if SPY_TICKER in st.session_state.market_data:
            try:
                df_spy_ctx = st.session_state.market_data[SPY_TICKER]
                ctx_spy = generate_macro_context(SPY_TICKER, df_spy_ctx)
                ctx_spy_text = format_context_for_llm(ctx_spy)

                extra_context = (
                    "\n\nContexto cuantitativo actual para SPY (calculado en Python):\n"
                    f"{ctx_spy_text}\n"
                    "Usa estos datos cuando el usuario pregunte por volatilidad, momentum, "
                    "máximos/mínimos del día o estacionalidad de SPY."
                )
            except Exception as e:
                extra_context = f"\n\n(No se pudo generar contexto cuantitativo por un error interno: {e})"

        messages_for_llm = [
            {"role": "system", "content": base_system + extra_context}
        ]

        # Historial de conversación
        for msg in st.session_state.messages:
            if msg["role"] in ("user", "assistant"):
                messages_for_llm.append(msg)

        with st.spinner("Analizando mercado... 💡"):
            try:
                response_text = call_llm(client, messages_for_llm, model_name=model_name)
            except Exception as e:
                response_text = f"Ups, hubo un error al llamar al modelo: {e}"

        st.session_state.messages.append({"role": "assistant", "content": response_text})
