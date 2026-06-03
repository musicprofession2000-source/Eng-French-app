import streamlit as st
import google.generativeai as genai
import json

genai.configure(api_key="AQ.Ab8RN6JRsOmxntayqxNpPYGem--6FGxfLsu0MkzTcUm2t5orfA")
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="French Practice App", layout="wide")
st.title("🇫🇷 French Practice App")

col1, col2, col3 = st.columns(3)
level = col1.selectbox("Level:", ["A1", "A2", "B1", "B2"])
ai_role = col2.selectbox("Role:", ["Nhân viên", "Khách hàng", "Bạn bè"])
topics = ["At the Pharmacy", "Job Interview", "At the Restaurant", "At the Airport", "Booking a Hotel",
          "Asking for Directions", "At the Supermarket", "Doctor's Appointment", "At the Bank", "Renting an Apartment"]
topic = col3.selectbox("Topic:", topics)

if "chat_history" not in st.session_state: st.session_state["chat_history"] = []
if "unlocked" not in st.session_state: st.session_state["unlocked"] = False
if "quiz" not in st.session_state: st.session_state["quiz"] = None

if st.button("✨ Generate 20 Questions"):
    with st.spinner("Generating..."):
        try:
            prompt = f"Generate 20 MCQ for topic '{topic}', level {level}. Return ONLY a JSON array with keys: q, a, c."
            res = model.generate_content(prompt)
            # Thay the cach lam sach bang cach khong dung dau gach nguoc
            text = res.text.replace('`', '').replace('json', '', 1).strip()
            st.session_state["quiz"] = json.loads(text)
        except: st.error("Error generating, please try again.")

if st.session_state["quiz"]:
    answers = [st.radio(f"{i+1}. {q['q']}", q['a'], key=f"q{i}", index=None) for i, q in enumerate(st.session_state["quiz"])]
    if st.button("Submit Answers"):
        score = sum(1 for i, q in enumerate(st.session_state["quiz"]) if answers[i] == q['c'])
        if score >= 14:
            st.session_state["unlocked"] = True
            st.success(f"Score: {score}/20. Chat unlocked!")
        else: st.error(f"Score: {score}/20. Need 14 to unlock.")

if st.session_state["unlocked"]:
    st.header("💬 AI Chat")
    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    if prompt := st.chat_input("Message..."):
        st.session_state["chat_history"].append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            res = model.generate_content(f"Role: {ai_role}. Topic: {topic}. User: {prompt}. Reply in French and translate.")
            st.session_state["chat_history"].append({"role": "assistant", "content": res.text})
            st.rerun()
