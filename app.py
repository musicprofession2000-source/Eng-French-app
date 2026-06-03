import streamlit as st
import google.generativeai as genai
import json

# Cấu hình
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="App Luyện Tiếng Pháp", layout="wide")
st.title("🇫🇷 Luyện Tiếng Pháp (Chế độ Text)")

# Sidebar
with st.sidebar:
    level = st.selectbox("Niveau:", ["A2", "B1", "B2", "C1"])
    topic = st.selectbox("Sujet:", ["Pharmacy", "Interview", "Restaurant", "Airport", "Hotel"])
    st.markdown("---")
    if st.button("Làm mới bộ đề"):
        st.session_state.quiz = None
        st.rerun()

# 1. Tạo bộ đề (Chỉ dùng Text)
if st.button("✨ Lấy bài tập"):
    prompt = f"Tạo 5 câu hỏi trắc nghiệm (MCQ) bằng tiếng Pháp cho chủ đề '{topic}', trình độ {level}. Trả về JSON: [{'q': 'Câu hỏi', 'a': ['A', 'B', 'C', 'D'], 'c': 'Đáp án đúng'}]"
    res = model.generate_content(prompt)
    st.session_state.quiz = json.loads(res.text.replace('json', '').replace('`', '').strip())
    st.rerun()

# 2. Làm bài
if "quiz" in st.session_state and st.session_state.quiz:
    ans = {}
    for i, q in enumerate(st.session_state.quiz):
        ans[i] = st.radio(f"{i+1}. {q['q']}", q['a'], key=f"q{i}", index=None)
    
    if st.button("Kiểm tra đáp án"):
        score = sum(1 for i, q in enumerate(st.session_state.quiz) if ans[i] == q['c'])
        st.write(f"### Kết quả: {score}/5")
        st.session_state.chat_active = True

# 3. Chat văn bản (Không Audio)
if st.session_state.get("chat_active", False):
    st.markdown("---")
    st.header("💬 Chat với Giáo viên AI")
    if "messages" not in st.session_state: st.session_state.messages = []
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.write(msg["text"])
    
    if text := st.chat_input("Nhập câu trả lời bằng tiếng Pháp..."):
        st.session_state.messages.append({"role": "user", "text": text})
        # AI trả lời văn bản
        res = model.generate_content(f"Bạn là giáo viên tiếng Pháp. Hãy sửa lỗi (nếu có) và trả lời bằng tiếng Pháp ngắn gọn cho câu: {text}")
        st.session_state.messages.append({"role": "assistant", "text": res.text})
        st.rerun()
