import streamlit as st
import google.generativeai as genai
import json

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("French Practice App")

level = st.selectbox("Level:", ["A2", "B1", "B2", "C1"])
role = st.selectbox("Role:", ["Staff", "Customer", "Friend"])
topic = st.selectbox("Topic:", ["Pharmacy", "Interview", "Restaurant", "Airport"])

if "quiz" not in st.session_state: st.session_state["quiz"] = None
if "unlocked" not in st.session_state: st.session_state["unlocked"] = False

if st.button("Generate Quiz"):
    res = model.generate_content(f"Generate 5 MCQ for {topic} at level {level}. Return raw JSON array with keys q, a, c")
    st.session_state["quiz"] = json.loads(res.text.strip().replace("```", "").replace("json", ""))
    st.rerun()

if st.session_state["quiz"]:
    for i, q in enumerate(st.session_state["quiz"]):
        st.radio(q["q"], q["a"], key=f"q{i}")
    if st.button("Submit"):
        st.session_state["unlocked"] = True
        st.success("Chat Unlocked!")

if st.session_state["unlocked"]:
    msg = st.chat_input("Chat in French:")
    if msg:
        rep = model.generate_content(f"Role: {role}. Topic: {topic}. User: {msg}. Reply in French.")
        st.write(rep.text)
