import streamlit as st
import google.generativeai as genai

# 1. Cấu hình
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
# Sử dụng model 'gemini-1.5-flash' vì đây là model cực kỳ ổn định và ít lỗi quota nhất
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="French Practice App", layout="wide")
st.title("🇫🇷 French Practice App")

# Hàm lưu trữ từ vựng để không bao giờ gọi API thừa
@st.cache_data(ttl=3600)
def get_vocab(topic, level):
    prompt = f"Act as a French teacher. Provide 5 essential phrases for topic '{topic}' at level {level}. Format: Phrase - Meaning - Example."
    res = model.generate_content(prompt)
    return res.text

# 2. Khởi tạo trạng thái
if "step" not in st.session_state: st.session_state.step = "config"
if "messages" not in st.session_state: st.session_state.messages = []

# Danh sách chủ đề
topics = ["Pharmacy", "Interview", "Restaurant", "Airport", "Hotel", "Shopping", "Transportation", "Bank", "Hospital", "School"]

with st.sidebar:
    level = st.selectbox("Select Level:", ["A2", "B1", "B2", "C1"])
    topic = st.selectbox("Select Topic:", topics)
    role = st.text_input("Your role:")
    if st.button("Reset"): st.session_state.clear(); st.rerun()

# 3. Logic
if st.session_state.step == "config":
    if st.button("Generate Vocabulary Warm-up"):
        # Gọi hàm có cache
        st.session_state.vocab = get_vocab(topic, level)
        st.session_state.step = "warmup"
        st.rerun()

elif st.session_state.step == "warmup":
    st.subheader(f"💡 Vocabulary for {topic}")
    st.write(st.session_state.vocab)
    if st.button("Start Conversation"):
        st.session_state.step = "chat"
        st.rerun()

elif st.session_state.step == "chat":
    # Phần chat giữ nguyên...
    if not st.session_state.messages:
        st.session_state.messages = [{"role": "assistant", "content": "Bonjour! Let's practice."}]
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.write(msg["content"])
    
    if prompt := st.chat_input("Message..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        # AI response không nên cache vì mỗi lần chat là một nội dung khác nhau
        res = model.generate_content(f"Topic: {topic}. Reply in French: {prompt}")
        st.session_state.messages.append({"role": "assistant", "content": res.text})
        st.rerun()
