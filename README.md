
https://chatfintech-fia.streamlit.app/

# 📈 FinChat – Asistente Inteligente de Análisis Bursátil

FinChat es una aplicación interactiva construida en **Python + Streamlit** que integra análisis cuantitativo, descarga de datos bursátiles, consulta de noticias y capacidades de IA generativa utilizando la API de **OpenAI**.

El asistente está diseñado para analizar el ETF **SPY** y las **7 Magníficas**:
- AAPL  
- MSFT  
- NVDA  
- GOOGL  
- AMZN  
- META  
- TSLA  

---

## 🧠 Funcionalidades principales

### ✅ 1. Chat financiero inteligente
- Asistente entrenado con prompts avanzados.
- Protegido contra *prompt injection*.
- Usa datos cuantitativos reales (volatilidad, momentum, estacionalidad, máximos/mínimos).
- Conversación en lenguaje natural.

---

## 📥 2. Descarga automática de datos financieros
La app descarga precios históricos con:
- `yfinance`
- Cálculo de:
  - Volatilidad anualizada (20 días por defecto)
  - Momentum (10 días por defecto)
  - Máximos y mínimos intradía
  - Estacionalidad promedio mensual

---

## 📰 3. Noticias bursátiles por ticker
- Obtiene titulares desde la API de OpenAI.
- Muestra título, fecha, fuente y enlace.
- Guarda las noticias por ticker en el estado de sesión.

---

## 🧠 4. Resumen de noticias con IA
- Resume las últimas 5 noticias.
- Enfocado a traders intradía y swing.
- Formato de máximo 5 viñetas.
- Se inserta directamente en el chat.

---

## 📊 5. Análisis macro cuantitativo
El módulo analiza:
- Tendencia reciente
- Volatilidad
- Momentum
- Rango intradía
- Estacionalidad del activo
- Comportamiento relativo frente al promedio

Incluye:
- Interpretación automática generada con IA.
- Explicación para traders: sesgo alcista/bajista, riesgos y lectura del mercado.

---

## 🎨 6. Interfaz tipo ChatGPT
- Chat estilizado con Dark Mode.
- Burbujas de usuario y asistente.
- Scroll automático.
- Todos los botones están en el **sidebar** y agregan respuestas directamente al chat.

---

## ⚙️ 7. Arquitectura de carpetas

```
chatFintech/
│── app.py
│── config.py
│── README.md  👈 (este archivo)
│
├── core/
│   ├── financial_data.py
│   ├── news_fetcher.py
│   ├── analysis_engine.py
│   ├── openai_client.py
│
└── requirements.txt
```

---

## 🚀 8. Cómo ejecutar la aplicación

### 1️⃣ Crear entorno virtual
```bash
python -m venv .venv
```

### 2️⃣ Activar entorno  
Windows:
```bash
.venv\Scriptsctivate
```

Linux/Mac:
```bash
source .venv/bin/activate
```

### 3️⃣ Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4️⃣ Ejecutar la app
```bash
streamlit run app.py
```

---

## 🔐 API Key requerida
La app utiliza:
- `OpenAI API` → para IA y noticias

Se coloca desde el sidebar.

---

## 📘 Licencia
Proyecto académico para la materia **Fundamentos de Inteligencia Artificial**.  
Uso libre para fines educativos.

---

## 👨‍💻 Autor
**Jairo Pérez**  
Maestría en Ciencia de Datos  
Proyecto final – Inteligencia Artificial

---

