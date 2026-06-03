import streamlit as st
import google.generativeai as genai
import json

# Setup
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("🇫🇷 French Practice App")

# Cấu hình
level = st.selectbox("Select Level:", ["A2", "B1", "B2", "C1"])
role = st.selectbox("Select Role:", ["Staff", "Customer", "Friend"])
topic = st.selectbox("Select Topic:", ["Pharmacy", "Interview", "Restaurant", "Airport", "Hotel"])

if "chat_history" not in st.session_state: st.session_state["chat_history"] = []
if "unlocked" not in st.session_state: st.session_state["unlocked"] = False
if "quiz" not in st.session_state: st.session_state["quiz"] = None

# Quiz
if st.button("Generate Quiz"):
    with st.spinner("Generating..."):
        try:
            prompt = f"Generate 5 MCQ for {topic} at level {level}. Return ONLY valid JSON array with keys: q, a, c"
            res = model.generate_content(prompt)
            st.session_state["quiz"] = json.loads(res.text.replace('json', '').replace('`', '').strip())
            st.rerun()
        except Exception as e: st.error(f"Error: {e}")

if st.session_state["quiz"]:
    for i, q in enumerate(st.session_state["quiz"]):
        st.radio(q['q'], q['a'], key=f"q{i}")
    if st.button("Submit"):
        st.session_state["unlocked"] = True
        st.success("Chat Unlocked!")

# Chat
if st.session_state["unlocked"]:
    st.header("💬 Chat Room")
    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]): st.write(msg["content"])
    
    if prompt := st.chat_input("Enter your message in French:"):
        st.session_state["chat_history"].append({"role": "user", "content": prompt})
        res = model.generate_content(f"Role: {role}. Topic: {topic}. User said: {prompt}. Reply in French.")
        st.session_state["chat_history"].append({"role": "assistant", "content": res.text})
        st.rerun()
