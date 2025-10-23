import streamlit as st
from supabase import create_client, Client

st.set_page_config(page_title="Dashboard Bot Médico", page_icon="🩺", layout="wide")
st.title("🩺 Dashboard del Bot Médico")
st.write("Visualiza el historial de conversaciones almacenadas en Supabase.")

# ------------------------------
# 🧠 Manejo de credenciales
# ------------------------------
if "supabase" not in st.session_state:
    st.session_state.supabase = None

# Si no hay cliente ni credenciales guardadas, pedirlas al usuario
if st.session_state.supabase is None:
    st.subheader("🔑 Conexión a Supabase")

    with st.form("supabase_login"):
        url = st.text_input("SUPABASE_URL", placeholder="https://tu-proyecto.supabase.co")
        key = st.text_input("SUPABASE_KEY", placeholder="Tu clave API de Supabase", type="password")
        conectar = st.form_submit_button("Conectar")

        if conectar:
            if url.strip() and key.strip():
                try:
                    supabase = create_client(url.strip(), key.strip())
                    st.session_state.supabase = supabase
                    st.success("✅ Conexión exitosa a Supabase.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al conectar a Supabase: {e}")
            else:
                st.warning("Por favor, completa ambos campos antes de continuar.")
    st.stop()

# Si ya existe cliente, usarlo
supabase: Client = st.session_state.supabase

# ------------------------------
# 📊 Mostrar historial
# ------------------------------
try:
    response = supabase.table("chat_history").select("*").order("created_at", desc=True).execute()
    data = response.data or []

    if not data:
        st.warning("No hay conversaciones registradas aún.")
    else:
        usuarios = sorted({chat["user_id"] for chat in data})
        usuario_filtrado = st.selectbox("Filtrar por usuario", options=["Todos"] + usuarios)

        for chat in data:
            if usuario_filtrado != "Todos" and chat["user_id"] != usuario_filtrado:
                continue

            with st.container():
                st.markdown(f"**👤 Usuario {chat['user_id']}** — {chat.get('created_at')}")
                if chat.get("sender_role") == "user":
                    st.info(f"🗣️ {chat.get('content')}")
                else:
                    st.success(f"🤖 {chat.get('content')}")
except Exception as e:
    st.error(f"⚠️ Error al obtener datos desde Supabase: {e}")
