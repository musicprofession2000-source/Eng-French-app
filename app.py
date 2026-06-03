import streamlit as st
import google.generativeai as genai
import json
from gtts import gTTS
import io

# Cấu hình API - Dùng model ổn định nhất gemini-1.0-pro
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.0-pro')

st.set_page_config(page_title="French Practice App", layout="wide")
st.title("🇫🇷 French Practice App")

# Cấu hình
topic = st.selectbox("Select Topic:", ["Pharmacy", "Interview", "Restaurant", "Airport", "Hotel"])

if "chat" not in st.session_state: st.session_state["chat"] = []
if "unlocked" not in st.session_state: st.session_state["unlocked"] = False

# Chat
st.header("💬 Chat Room")
for msg in st.session_state["chat"]:
    with st.chat_message(msg["role"]): st.write(msg["content"])

if prompt := st.chat_input("Message:"):
    st.session_state["chat"].append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.write(prompt)
    
    with st.chat_message("assistant"):
        # Gửi prompt cho model gemini-1.0-pro
        res = model.generate_content(f"Topic: {topic}. User: {prompt}. Reply in French.")
        st.session_state["chat"].append({"role": "assistant", "content": res.text})
        
        # Audio
        tts = gTTS(res.text, lang='fr')
        f = io.BytesIO()
        tts.write_to_fp(f)
        st.audio(f.getvalue(), format='audio/mp3')
        st.rerun()
