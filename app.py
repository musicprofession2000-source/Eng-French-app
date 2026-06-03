import streamlit as st
import google.generativeai as genai
import json
from gtts import gTTS
import io

# Setup
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-pro')

st.set_page_config(page_title="French Practice App", layout="wide")
st.title("🇫🇷 French Practice App")

# Sidebar Dictionary
st.sidebar.title("Dictionary")
word = st.sidebar.text_input("Look up a word:")
if word:
    try:
        def_res = model.generate_content(f"Define '{word}' in English and French.")
        st.sidebar.info(def_res.text)
    except: pass

# Settings
col1, col2, col3 = st.columns(3)
level = col1.selectbox("Level:", ["A2", "B1", "B2", "C1"])
role = col2.selectbox("Role:", ["Staff", "Customer", "Friend"])
topics = ["At the Pharmacy", "Job Interview", "At the Restaurant", "At the Airport", "Booking a Hotel",
          "Asking for Directions", "At the Supermarket", "Doctor's Appointment", "At the Bank", "Renting an Apartment",
          "Buying a Train Ticket", "At the Post Office", "Shopping for Clothes", "At the Gym", "Hobbies",
          "At the Library", "Ordering Coffee", "At the Hair Salon", "Planning a Trip", "Introducing Yourself",
          "Reporting a Lost Item", "At the Museum", "Talking about Weather", "Discussing a Movie", "In a Taxi",
          "Job Review", "Tech Support", "Birthday Party", "Dinner Plans", "Daily Routine"]
topic = col3.selectbox("Topic:", topics)

# State
if "history" not in st.session_state: st.session_state["history"] = []
if "unlocked" not in st.session_state: st.session_state["unlocked"] = False
if "quiz" not in st.session_state: st.session_state["quiz"] = None

# Quiz
if st.button("Generate Quiz"):
    try:
        prompt = f"Generate 20 MCQ for {topic} at level {level}. Return ONLY a JSON array with keys q, a, c."
        res = model.generate_content(prompt)
        text = res.text.replace("json", "").replace("`", "").strip()
        st.session_state["quiz"] = json.loads(text)
        st.rerun()
    except Exception as e: st.error(f"Error: {e}")

if st.session_state["quiz"]:
    answers = [st.radio(f"{q['q']}", q['a'], key=f"q{i}", index=None) for i, q in enumerate(st.session_state["quiz"])]
    if st.button("Submit"):
        score = sum(1 for i, q in enumerate(st.session_state["quiz"]) if answers[i] == q['c'])
        if score >= 14:
            st.session_state["unlocked"] = True
            st.success("Chat Unlocked!")
        else: st.error("Need 14 correct.")

# Chat
if st.session_state["unlocked"]:
    st.header("Chat Room")
    for msg in st.session_state["history"]:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    
    # Text input
    if prompt := st.chat_input("Message:"):
        st.session_state["history"].append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            res = model.generate_content(f"Role: {role}. Topic: {topic}. User said: {prompt}. Reply in French.")
            st.session_state["history"].append({"role": "assistant", "content": res.text})
            st.rerun()
