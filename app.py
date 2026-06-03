import streamlit as st
import google.generativeai as genai
import json
from gtts import gTTS
import io

# Setup API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Use the most stable model for your region
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="French Practice App", layout="wide")
st.title("🇫🇷 French Practice App")

# Dictionary
st.sidebar.title("Dictionary")
word = st.sidebar.text_input("Look up:")
if word:
    try:
        res = model.generate_content(f"Define '{word}' for French learners.")
        st.sidebar.info(res.text)
    except Exception as e:
        st.sidebar.error("Model unavailable.")

# UI
col1, col2, col3 = st.columns(3)
level = col1.selectbox("Level:", ["A2", "B1", "B2", "C1"])
role = col2.selectbox("Role:", ["Staff", "Customer", "Friend"])
topic = col3.selectbox("Topic:", ["At the Pharmacy", "Job Interview", "At the Restaurant", "Booking a Hotel"])

if "chat" not in st.session_state: st.session_state["chat"] = []
if "unlocked" not in st.session_state: st.session_state["unlocked"] = False
if "quiz" not in st.session_state: st.session_state["quiz"] = None

# Quiz Generation
if st.button("✨ Generate 20 Questions"):
    try:
        prompt = f"Generate 20 MCQ for {topic}, level {level}. Return ONLY a JSON array with keys: q, a, c."
        res = model.generate_content(prompt)
        text = res.text.replace('json', '').replace('`', '').strip()
        st.session_state["quiz"] = json.loads(text)
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}. Please check your API access.")

if st.session_state["quiz"]:
    answers = [st.radio(f"{i+1}. {q['q']}", q['a'], key=f"q{i}", index=None) for i, q in enumerate(st.session_state["quiz"])]
    if st.button("Submit"):
        if sum(1 for i, q in enumerate(st.session_state["quiz"]) if answers[i] == q['c']) >= 14:
            st.session_state["unlocked"] = True
            st.success("Chat unlocked!")
        else: st.error("Need 14 correct.")

# Chat
if st.session_state["unlocked"]:
    st.header("💬 Chat Room")
    for msg in st.session_state["chat"]:
        with st.chat_message(msg["role"]): st.markdown(msg["text"])
    
    # Text input
    if text := st.chat_input("Type message..."):
        st.session_state["chat"].append({"role": "user", "text": text})
        try:
            res = model.generate_content(f"Role: {role}. Topic: {topic}. User: {text}. Reply in French.")
            st.session_state["chat"].append({"role": "assistant", "text": res.text})
            # Audio output
            tts = gTTS(res.text, lang='fr')
            f = io.BytesIO()
            tts.write_to_fp(f)
            st.audio(f.getvalue(), format='audio/mp3')
        except Exception as e:
            st.session_state["chat"].append({"role": "assistant", "text": "Sorry, model error."})
        st.rerun()
