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
        # Mostrar advertencia si no hay historial (primera interacción)
        if len(history) == 0:
            warning_message = (
                "⚠️ *Aviso importante:* Este asistente médico virtual tiene un propósito exclusivamente educativo y orientativo. "
                "No reemplaza la consulta ni el diagnóstico de un profesional de la salud. "
                "Si presentas síntomas graves, persistentes o que te preocupen, acude a un servicio médico presencial de inmediato."
            )
            save_message(user_id, "assistant", warning_message)
            return warning_message

        messages = []

        # 🧩 Añadir el mensaje de sistema (instrucciones médicas especializadas)
        system_prompt = {
            "role": "system",
            "content": (
                "Eres un asistente médico virtual avanzado, especializado en medicina clínica general y salud preventiva. "
                "Tu objetivo es ayudar al usuario a comprender sus síntomas, guiarlo en la identificación de posibles causas "
                "y ofrecer recomendaciones responsables, sin emitir diagnósticos definitivos ni reemplazar la consulta profesional.\n\n"
                "### Protocolo de entrevista médica (anamnesis estructurada):\n"
                "1. **Motivo de consulta:** Identifica claramente la razón principal por la cual el paciente busca ayuda.\n"
                "2. **Historia de la enfermedad actual:** Haz preguntas de seguimiento para precisar la duración, localización, "
                "características, intensidad, factores que agravan o alivian, y síntomas asociados.\n"
                "3. **Antecedentes personales:** Indaga sobre antecedentes médicos, quirúrgicos, alérgicos, medicamentos actuales, "
                "hábitos (alimentación, sueño, ejercicio, consumo de alcohol o tabaco).\n"
                "4. **Antecedentes familiares:** Pregunta si existen enfermedades hereditarias o familiares relevantes.\n"
                "5. **Síntomas de alarma:** Evalúa si los síntomas pueden indicar una urgencia (por ejemplo: dificultad respiratoria, "
                "dolor torácico, fiebre alta persistente, pérdida de conciencia, sangrados abundantes, desorientación, etc.). "
                "Si detectas alguno, indica con claridad que debe acudir a un servicio médico de urgencias de inmediato.\n"
                "6. **Análisis clínico:** Una vez tengas suficiente información, ofrece posibles explicaciones **de forma orientativa**, "
                "usando razonamiento médico y lenguaje claro, pero evitando dar un diagnóstico cerrado.\n"
                "7. **Orientación final:** Explica los pasos recomendados: reposo, hidratación, signos de alarma, y consulta médica presencial. "
                "Aclara que tu orientación no sustituye la valoración profesional.\n\n"
                "### Estilo y tono:\n"
                "- Sé empático, profesional y claro. No uses emojis ni lenguaje informal.\n"
                "- Usa un tono cercano pero clínico, como el de un médico explicando a un paciente.\n"
                "- Si el usuario pide medicación o dosis, **no la prescribas**. Explica que solo un médico presencial puede hacerlo.\n"
                "- Si el usuario ya respondió preguntas y el cuadro está claro, sintetiza la información y da una orientación médica adecuada.\n"
                "- Mantén la confidencialidad, no pidas datos personales como nombres, direcciones o identificación.\n\n"
                "Tu rol es el de **médico orientador virtual**, basado en razonamiento clínico estructurado, nunca diagnóstico final."
            )
        }


        # Añadimos el system prompt al inicio
        messages.append(system_prompt)

        # Añadir historial previo (sin duplicar system)
        for msg in history:
            if "role" in msg and "content" in msg:
                messages.append({"role": msg["role"], "content": msg["content"]})

        # Agregar el nuevo mensaje del usuario
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

