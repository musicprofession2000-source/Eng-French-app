import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="French Practice App", layout="wide")
st.title("🇫🇷 French Practice App")

# 1. Cấu hình API Key
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Lỗi: Chưa tìm thấy 'GEMINI_API_KEY' trong phần Secrets.")
    st.stop()

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"].strip())
    # Sử dụng model 'gemini-1.0-pro' thay vì flash để tránh lỗi 404
    model = genai.GenerativeModel('gemini-1.0-pro') 
except Exception as e:
    st.error(f"Lỗi khởi tạo AI: {e}")
    st.stop()

# 2. Khởi tạo trạng thái
if "step" not in st.session_state: st.session_state.step = "config"
if "messages" not in st.session_state: st.session_state.messages = []

# 3. Sidebar
with st.sidebar:
    level = st.selectbox("Level:", ["A2", "B1", "B2", "C1"])
    topic = st.selectbox("Topic:", ["Restaurant", "Hotel", "Airport", "Shopping"])
    role = st.text_input("Your role:")

# 4. Logic
if st.session_state.step == "config":
    if st.button("Generate Vocabulary"):
        try:
            prompt = f"Give 5 essential French phrases for {topic} ({level}). Format: Phrase - Meaning."
            response = model.generate_content(prompt)
            st.session_state.vocab = response.text
            st.session_state.step = "warmup"
            st.rerun()
        except Exception as e:
            st.error(f"Lỗi gọi AI: {e}")

elif st.session_state.step == "warmup":
    st.write(st.session_state.vocab)
    if st.button("Start Chat"):
        st.session_state.step = "chat"
        st.rerun()

elif st.session_state.step == "chat":
    if prompt := st.chat_input("Message:"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        try:
            res = model.generate_content(f"Role: {role}. Reply in French: {prompt}")
            st.session_state.messages.append({"role": "assistant", "content": res.text})
            st.rerun()
        except Exception as e:
            st.error(f"Lỗi chat: {e}")

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])
