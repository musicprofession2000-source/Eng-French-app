import streamlit as st
import google.generativeai as genai

# 1. Cấu hình
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.0-flash')

st.set_page_config(page_title="French Practice App", layout="wide")
st.title("🇫🇷 French Practice App")

# 2. Khởi tạo trạng thái ứng dụng
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

# 4. Logic theo từng bước
if st.session_state.step == "config":
    if st.button("Generate Vocabulary Warm-up"):
        prompt = f"Act as a French teacher. Provide 5 essential phrases for topic '{topic}' at level {level}. Format: Phrase - Meaning - Example."
        res = model.generate_content(prompt)
        st.session_state.vocab = res.text
        st.session_state.step = "warmup"
        st.rerun()

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
        
        # AI Phản hồi
        ai_prompt = f"Role: {role}. Topic: {topic}. Level: {level}. User said: {prompt}. Reply in French."
        res = model.generate_content(ai_prompt)
        
        st.session_state.messages.append({"role": "assistant", "content": res.text})
        st.rerun()
