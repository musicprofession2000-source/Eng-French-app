import streamlit as st
import google.generativeai as genai

# Cấu hình giao diện
st.set_page_config(page_title="French Practice App", layout="wide")
st.title("🇫🇷 French Practice App")

# Cấu hình API Key
if "GEMINI_API_KEY" not in st.secrets:
    st.error("LỖI: Bạn chưa dán GEMINI_API_KEY vào mục Secrets trên Streamlit Cloud!")
    st.stop()

# Khởi tạo AI
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Lỗi khởi tạo AI: {e}")
    st.stop()

# Khởi tạo trạng thái
if "step" not in st.session_state: st.session_state.step = "config"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "vocab" not in st.session_state: st.session_state.vocab = ""

# Sidebar - Cấu hình
with st.sidebar:
    st.header("Settings")
    level = st.selectbox("Level:", ["A2", "B1", "B2", "C1"])
    topics = ["Restaurant", "Hotel", "Airport", "Shopping", "Pharmacy", "Interview"]
    topic = st.selectbox("Topic:", topics)
    role = st.text_input("Role (e.g. Waiter):")
    if st.button("Reset All"):
        st.session_state.clear()
        st.rerun()

# Luồng logic
if st.session_state.step == "config":
    if st.button("Generate Vocabulary Warm-up"):
        try:
            with st.spinner("AI is thinking..."):
                prompt = f"Provide 5 essential French phrases for {topic} at level {level}. Meaning and short example."
                response = model.generate_content(prompt)
                st.session_state.vocab = response.text
                st.session_state.step = "warmup"
                st.rerun()
        except Exception as e:
            st.error(f"Lỗi gọi AI: {e}")

elif st.session_state.step == "warmup":
    st.subheader(f"💡 Vocabulary for {topic}")
    st.write(st.session_state.vocab)
    if st.button("Start Conversation"):
        st.session_state.step = "chat"
        st.rerun()

elif st.session_state.step == "chat":
    st.header(f"💬 Chatting about {topic}")
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.write(msg["text"])
    
    if user_input := st.chat_input("Type in French..."):
        st.session_state.chat_history.append({"role": "user", "text": user_input})
        with st.chat_message("user"): st.write(user_input)
        
        try:
            ai_reply = model.generate_content(f"Topic: {topic}. Role: {role}. User: {user_input}. Reply in French.")
            st.session_state.chat_history.append({"role": "assistant", "text": ai_reply.text})
            st.rerun()
        except Exception as e:
            st.error(f"Lỗi trò chuyện: {e}")
