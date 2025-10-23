"""
agent_core.py
Lógica del agente médico (LangChain + Groq).
Analiza síntomas, hace preguntas, y da posibles causas y recomendaciones.
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from memory_manager import get_conversation_history, save_message

load_dotenv()

# =========================
# 🔹 Inicializar modelo Groq
# =========================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("❌ Falta la variable GROQ_API_KEY en el archivo .env")

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.1-8b-instant",
    temperature=0.4
)

# =========================
# 🔹 Función principal del agente
# =========================
def invoke_agent(user_input: str, user_id: str):
    """
    Procesa la entrada del usuario, consulta la memoria en Supabase
    y responde usando el modelo Groq.
    """
    try:
        # 📜 Obtener historial de conversación del usuario
        history = get_conversation_history(user_id)
        messages = []

        # 🧩 Convertir historial al formato que el modelo espera
        for msg in history:
            if "role" in msg and "content" in msg:
                messages.append({"role": msg["role"], "content": msg["content"]})

        # ➕ Agregar el nuevo mensaje del usuario
        messages.append({"role": "user", "content": user_input})

        # 💬 Llamar al modelo de Groq
        response = llm.invoke(messages)

        # 💾 Guardar mensajes en Supabase
        save_message(user_id, "user", user_input)
        save_message(user_id, "assistant", response.content)

        return response.content

    except Exception as e:
        print(f"❌ Error al procesar: {e}")
        return "Ocurrió un error al procesar tu mensaje. Intenta nuevamente."

