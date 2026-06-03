import streamlit as st
import google.generativeai as genai
import json

# Setup
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="French Practice App", layout="wide")
st.title("🇫🇷 French Practice App")

# Sidebar
with st.sidebar:
    level = st.selectbox("Level:", ["A2", "B1", "B2", "C1"])
    topic = st.selectbox("Topic:", ["Pharmacy", "Interview", "Restaurant", "Airport", "Hotel"])
    if st.button("Reset Quiz"):
        st.session_state.quiz = None
        st.rerun()

# 1. Generate Quiz (Đã sửa cú pháp dấu ngoặc)
if st.button("✨ Generate Quiz"):
    # Dùng {{ và }} để thoát dấu ngoặc, giúp Python không hiểu nhầm
    prompt = f"Create 5 French MCQ for topic '{topic}' at level {level}. Return ONLY valid JSON format: [{{'q': 'Question', 'a': ['A', 'B', 'C', 'D'], 'c': 'Correct answer'}}]"
    res = model.generate_content(prompt)
    
    # Làm sạch chuỗi trước khi chuyển sang JSON
    clean_text = res.text.replace('json', '').replace('```', '').strip()
    st.session_state.quiz = json.loads(clean_text)
    st.rerun()

# 2. Display Quiz
if "quiz" in st.session_state and st.session_state.quiz:
    ans = {}
    for i, q in enumerate(st.session_state.quiz):
        ans[i] = st.radio(f"{i+1}. {q['q']}", q['a'], key=f"q{i}", index=None)
    
    if st.button("Check Answers"):
        score = sum(1 for i, q in enumerate(st.session_state.quiz) if ans[i] == q['c'])
        st.write(f"### Score: {score}/5")
        st.session_state.chat_active = True

# 3. Chat
if st.session_state.get("chat_active", False):
    st.markdown("---")
    st.header("💬 Chat with AI Teacher")
    if "messages" not in st.session_state: st.session_state.messages = []
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.write(msg["text"])
    
    if text := st.chat_input("Type your message in French..."):
        st.session_state.messages.append({"role": "user", "text": text})
        res = model.generate_content(f"You are a French teacher. Reply in French: {text}")
        st.session_state.messages.append({"role": "assistant", "text": res.text})
        st.rerun()
