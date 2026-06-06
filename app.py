import streamlit as st
import google.generativeai as genai

# Cấu hình giao diện
st.set_page_config(page_title="French Practice App", layout="wide")
st.title("🇫🇷 French Practice App")

# Cấu hình AI (Bắt buộc dùng gemini-pro để tránh lỗi 404)
try:
    key = st.secrets["GEMINI_API_KEY"].strip()
    genai.configure(api_key=key)
    # Dùng model 'gemini-pro' thay cho flash để đảm bảo luôn tồn tại
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error(f"Lỗi khởi tạo: {e}")
    st.stop()

# Khởi tạo trạng thái
if "step" not in st.session_state: st.session_state.step = "config"
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# Danh sách chủ đề
topics = ["Restaurant", "Hotel", "Airport", "Shopping", "Pharmacy", "Interview"]
topic = st.sidebar.selectbox("Topic:", topics)
level = st.sidebar.selectbox("Level:", ["A2", "B1", "B2", "C1"])

# Luồng logic
if st.session_state.step == "config":
    if st.button("Generate Vocabulary"):
        try:
            prompt = f"Provide 5 essential French phrases for {topic} at level {level}. Meaning and example."
            res = model.generate_content(prompt)
            st.session_state.vocab = res.text
            st.session_state.step = "warmup"
            st.rerun()
        except Exception as e:
            st.error(f"Lỗi khi gọi AI: {e}")

elif st.session_state.step == "warmup":
    st.write(st.session_state.vocab)
    if st.button("Start Conversation"):
        st.session_state.step = "chat"
        st.rerun()

elif st.session_state.step == "chat":
    if prompt := st.chat_input("Type here..."):
        st.session_state.chat_history.append({"role": "user", "text": prompt})
        try:
            reply = model.generate_content(f"Topic: {topic}. Reply in French: {prompt}")
            st.session_state.chat_history.append({"role": "assistant", "text": reply.text})
            st.rerun()
        except Exception as e:
            st.error(f"Lỗi chat: {e}")
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.write(msg["text"])
