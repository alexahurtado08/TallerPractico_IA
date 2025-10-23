# dashboard.py
import streamlit as st
from memory_manager import supabase

st.set_page_config(page_title="Dashboard Bot Médico", page_icon="🩺", layout="wide")

st.title("🩺 Dashboard del Bot Médico")
st.write("Visualiza el historial de conversaciones almacenadas en Supabase.")

# Obtener historial completo
response = supabase.table("chat_history").select("*").order("created_at", desc=True).execute()
data = response.data

if data:
    for chat in data:
        with st.container():
            st.markdown(f"**👤 Usuario {chat['user_id']}** — {chat['created_at']}")
            if chat["sender"] == "user":
                st.info(f"🗣️ {chat['message']}")
            else:
                st.success(f"🤖 {chat['message']}")
else:
    st.warning("No hay conversaciones registradas aún.")
