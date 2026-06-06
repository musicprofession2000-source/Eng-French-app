import streamlit as st
import google.generativeai as genai
import os

# 1. Cấu hình
st.set_page_config(page_title="French Practice App", layout="wide")
st.title("🇫🇷 French Practice App")

# Kiểm tra API Key từ Streamlit Secrets
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Lỗi: Không tìm thấy 'GEMINI_API_KEY' trong phần Secrets của Streamlit. Vui lòng kiểm tra lại cấu hình!")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Khởi tạo trạng thái
if "step" not in st.session_state: st.session_state.step = "config"
if "messages" not in st.session_state: st.session_state.messages = []

# Danh sách 30 chủ đề
topics = [
    "Pharmacy", "Interview", "Restaurant", "Airport", "Hotel", "Shopping", 
    "Transportation", "Bank", "Hospital", "School", "Supermarket", "Tourism",
    "Office", "Weather", "Family", "Hobbies", "Cooking", "Technology",
    "Fashion", "Sports", "Cinema", "Health", "Art", "Music", "Environment",
    "Politics", "History", "Science", "Education", "Real Estate"
]

# 3. Giao diện Sidebar
with st.sidebar:
    st.header("Settings")
    level = st.selectbox("Select Level:", ["A2", "B1", "B2", "C1"])
    topic = st.selectbox("Select Topic:", topics)
    role = st.text_input("Enter your role (e.g., Client, Student):")
    
    if st.button("Reset App"):
        st.session_state.clear()
        st.rerun()

# 4. Logic từng bước
if st.session_state.step == "config":
    if st.button("Generate Vocabulary Warm-up"):
        try:
            prompt = f"Act as a French teacher. Provide 5 essential phrases for topic '{topic}' at level {level}. Format: Phrase - Meaning - Example."
            res = model.generate_content(prompt)
            st.session_state.vocab = res.text
            st.session_state.step = "warmup"
            st.rerun()
        except Exception as e:
            st.error(f"Lỗi khi gọi AI: {e}")

elif st.session_state.step == "warmup":
    st.subheader(f"💡 Vocabulary for {topic}")
    st.write(st.session_state.vocab)
    if st.button("Start Conversation"):
        st.session_state.step = "chat"
        st.rerun()

elif st.session_state.step == "chat":
    st.header(f"💬 Conversation: {topic}")
    if not st.session_state.messages:
        st.session_state.messages = [{"role": "assistant", "content": f"Bonjour! Let's practice. You are a {role}. How can I help you?"}]
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.write(msg["content"])
    
    if prompt := st.chat_input("Type your message in French..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        try:
            ai_prompt = f"Role: {role}. Topic: {topic}. Level: {level}. User said: {prompt}. Reply in French."
            res = model.generate_content(ai_prompt)
            st.session_state.messages.append({"role": "assistant", "content": res.text})
            st.rerun()
        except Exception as e:
            st.error(f"Lỗi khi chat: {e}")
