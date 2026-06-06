import streamlit as st
import google.generativeai as genai

# 1. Cấu hình
st.set_page_config(page_title="French Practice App", layout="wide")
st.title("🇫🇷 French Practice App")

# Cấu hình API key
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
# Đổi model sang tên này cho ổn định
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
    role = st.text_input("Enter your role:")
    if st.button("Reset App"): st.session_state.clear(); st.rerun()

# 4. Logic
if st.session_state.step == "config":
    if st.button("Generate Vocabulary Warm-up"):
        # Thử gọi model đơn giản hơn
        prompt = f"Provide 5 essential phrases for topic '{topic}' at level {level}. Format: Phrase - Meaning - Example."
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
        st.session_state.messages = [{"role": "assistant", "content": "Bonjour! Let's practice."}]
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.write(msg["content"])
    
    if prompt := st.chat_input("Type your message..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        res = model.generate_content(f"Topic: {topic}. Role: {role}. Reply in French: {prompt}")
        st.session_state.messages.append({"role": "assistant", "content": res.text})
        st.rerun()
