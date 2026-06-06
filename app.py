import streamlit as st
import google.generativeai as genai

# Cấu hình trang
st.set_page_config(page_title="French Practice App", layout="wide")
st.title("🇫🇷 French Practice App")

# 1. Kiểm tra API Key và kết nối (Đảm bảo không bị lỗi xác thực 401)
try:
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("LỖI: Bạn chưa dán GEMINI_API_KEY vào phần Secrets của Streamlit!")
        st.stop()
    
    # Lấy key và cấu hình
    api_key = st.secrets["GEMINI_API_KEY"].strip()
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Lỗi khởi tạo API: {e}")
    st.stop()

# 2. Khởi tạo trạng thái ứng dụng
if "step" not in st.session_state: st.session_state.step = "config"
if "messages" not in st.session_state: st.session_state.messages = []
if "vocab" not in st.session_state: st.session_state.vocab = ""

# 3. Sidebar (Cấu hình)
with st.sidebar:
    st.header("Settings")
    level = st.selectbox("Select Level:", ["A2", "B1", "B2", "C1"])
    topics = ["Pharmacy", "Interview", "Restaurant", "Airport", "Hotel", "Shopping", "Transportation", "Bank", "Hospital", "School"]
    topic = st.selectbox("Select Topic:", topics)
    role = st.text_input("Enter your role:")
    if st.button("Reset Session"):
        st.session_state.clear()
        st.rerun()

# 4. Các bước thực hiện
if st.session_state.step == "config":
    if st.button("Generate Vocabulary Warm-up"):
        with st.spinner('AI is generating phrases...'):
            try:
                # Prompt đơn giản để tránh lỗi định dạng
                prompt = f"Provide 5 essential French phrases for topic '{topic}' at level {level}. Meaning in English and short example."
                res = model.generate_content(prompt)
                st.session_state.vocab = res.text
                st.session_state.step = "warmup"
                st.rerun()
            except Exception as e:
                st.error(f"Lỗi khi gọi AI: {e}. (Lưu ý: Nếu lỗi 401, hãy kiểm tra lại Key trong Secrets!)")

elif st.session_state.step == "warmup":
    st.subheader(f"💡 Vocabulary for {topic}")
    st.write(st.session_state.vocab)
    if st.button("Start Conversation"):
        st.session_state.step = "chat"
        st.rerun()

elif st.session_state.step == "chat":
    st.header(f"💬 Chat with AI")
    if not st.session_state.messages:
        st.session_state.messages = [{"role": "assistant", "content": f"Bonjour! You are a {role}. Let's discuss {topic}."}]
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.write(msg["content"])
    
    if prompt := st.chat_input("Type your message..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        try:
            res = model.generate_content(f"Topic: {topic}. Role: {role}. User: {prompt}. Reply in French.")
            st.session_state.messages.append({"role": "assistant", "content": res.text})
            st.rerun()
        except Exception as e:
            st.error(f"Lỗi khi chat: {e}")
