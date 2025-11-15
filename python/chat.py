# app.py
import os
import textwrap
import pandas as pd
import streamlit as st
from openai import OpenAI

# -----------------------------
# CONFIGURACIÓN BÁSICA STREAMLIT
# -----------------------------
st.set_page_config(
    page_title="ChatData 🤖",
    page_icon="🤖",
    layout="wide"
)

# -----------------------------
# ESTILOS CUSTOM (UI JOVEN)
# -----------------------------
custom_css = """
<style>
/* Fondo general con degradado suave */
.main {
    background: radial-gradient(circle at top left, #1f2937, #020617);
}

/* Contenedor principal tipo card */
.chat-container {
    background: rgba(15, 23, 42, 0.85);
    border-radius: 24px;
    padding: 1.8rem 2.2rem;
    box-shadow: 0 20px 40px rgba(0,0,0,0.5);
    border: 1px solid rgba(148, 163, 184, 0.3);
}

/* Título principal con efecto neón suave */
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

/* Burbuja de mensajes */
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

/* Etiquetas arriba de cada burbuja */
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

/* Contenedor de mensajes con scroll */
.chat-history {
    max-height: 410px;
    overflow-y: auto;
    padding-right: 0.4rem;
}

/* Scrollbar custom */
.chat-history::-webkit-scrollbar {
    width: 6px;
}
.chat-history::-webkit-scrollbar-track {
    background: transparent;
}
.chat-history::-webkit-scrollbar-thumb {
    background: #4b5563;
    border-radius: 999px;
}

/* Caja de input */
input[type="text"], textarea {
    background: rgba(15, 23, 42, 0.8) !important;
    color: #e5e7eb !important;
    border-radius: 999px !important;
}

/* Botón enviar */
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

/* Radios/tabs estilo pill */
.stRadio > div {
    justify-content: center;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# -----------------------------
# CLIENTE OPENAI
# -----------------------------
def get_client(api_key: str | None):
    """Devuelve el cliente de OpenAI o None si no hay API key."""
    os.environ['OPENAI_API_KEY'] = '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'
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        return None
    return OpenAI(api_key=key)

def call_llm(client, messages, model_name: str = "gpt-4.1-mini") -> str:
    """Llama al modelo de lenguaje y devuelve el texto de respuesta."""
    completion = client.chat.completions.create(
        model=model_name,
        messages=messages,
        max_tokens=400,
        temperature=0.8,
    )
    return completion.choices[0].message.content


# -----------------------------
# ESTADO DE SESIÓN
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "¡Hey! Soy tu chatbot de datos 🤖📊. "
                       "Puedes chatear normal o hacerme preguntas sobre un CSV. ¿Qué quieres probar hoy?"
        }
    ]

if "csv_info" not in st.session_state:
    st.session_state.csv_info = None  # texto breve con info del CSV


# -----------------------------
# SIDEBAR (CONFIG)
# -----------------------------
with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    st.markdown(
        "Pega tu API key de **OpenAI** o usa la variable de entorno `OPENAI_API_KEY`."
    )
    api_key_input = st.text_input("🔑 OpenAI API key", type="password", help="Se recomienda usar st.secrets o variables de entorno.")
    model_name = st.selectbox(
        "🧠 Modelo",
        ["gpt-4.1-mini", "gpt-4o-mini", "gpt-4.1"],
        index=0
    )
    st.markdown("---")
    st.markdown("#### Sobre el modo CSV")
    st.caption(
        "Sube un archivo CSV y luego haz preguntas como:\n"
        "- *¿Cuántas filas tiene?*\n"
        "- *¿Cuál es el promedio de la columna X?*"
    )


# -----------------------------
# HEADER
# -----------------------------
st.markdown('<div class="app-title">ChatData 🤖</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">'
    'Un mini copiloto de datos para la generación Z: chatea, sube un CSV y pregunta lo que quieras. ✨'
    '</div>',
    unsafe_allow_html=True
)
st.write("")

# -----------------------------
# LAYOUT PRINCIPAL
# -----------------------------
col_chat, col_side = st.columns([2.5, 1.5], gap="large")

with col_chat:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    # Selector de modo
    mode = st.radio(
        "¿Cómo quieres chatear hoy?",
        ["💬 Texto libre", "📁 Preguntar sobre un CSV"],
        horizontal=True,
        label_visibility="visible"
    )

    # Historial de chat
    st.markdown("##### 🗨️ Conversación")
    st.markdown('<div class="chat-history">', unsafe_allow_html=True)

    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            st.markdown('<div class="msg-label-bot">ChatData 🤖</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="msg-bot">{msg["content"]}</div>', unsafe_allow_html=True)
        elif msg["role"] == "user":
            st.markdown('<div class="msg-label-user">Tú 👤</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="msg-user">{msg["content"]}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.write("")

    # INPUT DEL USUARIO
    if mode == "💬 Texto libre":
        user_input = st.text_input(
            "Escribe tu mensaje",
            placeholder="Ej: Explícame qué es el overfitting pero como si tuviera 15 años 😎",
        )
    else:
        user_input = st.text_input(
            "Escribe tu pregunta sobre el CSV",
            placeholder="Ej: ¿Cuál es el promedio de la columna 'precio' por categoría?",
        )

    send_clicked = st.button("🚀 Enviar mensaje")

    st.markdown('</div>', unsafe_allow_html=True)  # cierre .chat-container

with col_side:
    st.markdown("#### 📊 Zona de datos / CSV")
    if mode == "📁 Preguntar sobre un CSV":
        uploaded_file = st.file_uploader(
            "Sube tu archivo CSV",
            type=["csv"],
            help="Tamaño recomendado: archivos pequeños/medianos para pruebas."
        )

        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
            except UnicodeDecodeError:
                df = pd.read_csv(uploaded_file, encoding="latin1")

            st.markdown("##### 👀 Vista rápida del CSV")
            st.dataframe(df.head(), use_container_width=True)

            # Construimos una pequeña descripción que enviaremos al modelo
            cols = ", ".join(df.columns.astype(str).tolist())

            # Usar to_string en lugar de to_markdown para no depender de 'tabulate'
            sample_rows = df.head(3).to_string(index=False)

            csv_info = textwrap.dedent(f"""
            El usuario ha subido un dataset CSV con las siguientes columnas:
            {cols}

            Aquí tienes una muestra de las primeras filas en formato tabla de texto:

            {sample_rows}

            Usa esta información para responder preguntas sobre el dataset.
            No inventes columnas ni datos que no estén presentes.
            """)

            st.session_state.csv_info = csv_info

    else:
        st.info("Cambia al modo **📁 Preguntar sobre un CSV** para subir y explorar un archivo.")

# -----------------------------
# LÓGICA AL ENVIAR MENSAJE
# -----------------------------
if send_clicked and user_input.strip():
    # Append mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": user_input})

    client = get_client(api_key_input)
    if client is None:
        st.error("⚠️ No se encontró API key. Configúrala en el sidebar o como variable de entorno `OPENAI_API_KEY`.")
    else:
        # Armamos el contexto para el modelo
        messages_for_llm = []

        # System prompt base
        base_system = (
            "Eres un chatbot amigable, creativo y muy claro, pensado para jóvenes "
            "que están aprendiendo ciencia de datos y programación en Python. "
            "Explica las cosas con ejemplos sencillos, emojis donde tenga sentido "
            "y evita tecnicismos innecesarios."
        )

        # Si estamos en modo CSV, agregamos información del dataset
        if mode == "📁 Preguntar sobre un CSV" and st.session_state.csv_info:
            system_content = base_system + (
                "\n\nAdemás, el usuario quiere hacer preguntas sobre un dataset en CSV. "
                "La siguiente descripción y muestra del dataset te sirve de contexto:\n\n"
                f"{st.session_state.csv_info}"
            )
        else:
            system_content = base_system

        messages_for_llm.append({"role": "system", "content": system_content})

        # Añadimos el historial de la conversación (sin el system original de la app)
        for msg in st.session_state.messages:
            if msg["role"] in ("user", "assistant"):
                messages_for_llm.append(msg)

        # Llamamos al modelo
        with st.spinner("Pensando la mejor respuesta... 💡"):
            try:
                response_text = call_llm(client, messages_for_llm, model_name=model_name)
            except Exception as e:
                response_text = (
                    "Ups, algo salió mal al hablar con el modelo 😢. "
                    f"Detalle técnico: {e}"
                )

        # Guardamos respuesta del bot en el historial
        st.session_state.messages.append({"role": "assistant", "content": response_text})

        # Forzamos un rerun para refrescar UI
        #st.experimental_rerun()
