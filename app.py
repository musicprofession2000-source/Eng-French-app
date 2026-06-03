import streamlit as st
import google.generativeai as genai
import json
from gtts import gTTS
import io

# Setup
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="French Practice App", layout="wide")
st.title("🇫🇷 French Practice App - Full Features")

# Sidebar Dictionary
st.sidebar.title("Dictionary")
word = st.sidebar.text_input("Look up:")
if word:
    try:
        res = model.generate_content(f"Define '{word}' for French learners.")
        st.sidebar.info(res.text)
    except: pass

# Settings
col1, col2, col3 = st.columns(3)
level = col1.selectbox("Level:", ["A2", "B1", "B2", "C1"])
role = col2.selectbox("Role:", ["Staff", "Customer", "Friend"])
topics = [
    "At the Pharmacy", "Job Interview", "At the Restaurant", "At the Airport", "Booking a Hotel",
    "Asking for Directions", "At the Supermarket", "Doctor's Appointment", "At the Bank", "Renting an Apartment",
    "Buying a Train Ticket", "At the Post Office", "Shopping for Clothes", "At the Gym", "Hobbies",
    "At the Library", "Ordering Coffee", "At the Hair Salon", "Planning a Trip", "Introducing Yourself",
    "Reporting a Lost Item", "At the Museum", "Talking about Weather", "Discussing a Movie", "In a Taxi",
    "Job Review", "Tech Support", "Birthday Party", "Dinner Plans", "Daily Routine"
]
topic = col3.selectbox("Topic:", topics)

# Session States
if "chat" not in st.session_state: st.session_state["chat"] = []
if "unlocked" not in st.session_state: st.session_state["unlocked"] = False
if "quiz" not in st.session_state: st.session_state["quiz"] = None

# Quiz Generation
if st.button("✨ Generate 20 Questions"):
    with st.spinner("Generating..."):
        try:
            prompt = f"Generate 20 MCQ for {topic} at level {level}. Return ONLY a valid JSON array with keys: q, a, c."
            res = model.generate_content(prompt)
            text = res.text.replace('json', '').replace('`', '').strip()
            st.session_state["quiz"] = json.loads(text)
            st.rerun()
        except Exception as e: st.error(f"Error: {e}")

# Quiz Logic
if st.session_state["quiz"]:
    answers = [st.radio(f"{i+1}. {q['q']}", q['a'], key=f"q{i}", index=None) for i, q in enumerate(st.session_state["quiz"])]
    if st.button("Submit Answers"):
        score = sum(1 for i, q in enumerate(st.session_state["quiz"]) if answers[i] == q['c'])
        if score >= 14:
            st.session_state["unlocked"] = True
            st.success("Chat Unlocked!")
        else: st.error("Need 14/20 correct to unlock.")

# Chat Logic
if st.session_state["unlocked"]:
    st.header("💬 Chat & Voice Room")
    for msg in st.session_state["chat"]:
        with st.chat_message(msg["role"]): st.markdown(msg["text"])
    
    # Audio input
    audio = st.audio_input("Speak (Microphone):")
    if audio:
        transcript = model.generate_content([{"mime_type": "audio/wav", "data": audio.read()}, "Transcribe to French"]).text
        st.session_state["chat"].append({"role": "user", "text": transcript})
        st.rerun()
    
    # Text input
    if text := st.chat_input("Enter message..."):
        st.session_state["chat"].append({"role": "user", "text": text})
        st.rerun()

    # AI Reply
    if st.session_state["chat"] and st.session_state["chat"][-1]["role"] == "user":
        res = model.generate_content(f"Role: {role}. Topic: {topic}. User: {st.session_state['chat'][-1]['text']}. Reply in French.")
        st.session_state["chat"].append({"role": "assistant", "text": res.text})
        tts = gTTS(res.text, lang='fr')
        f = io.BytesIO()
        tts.write_to_fp(f)
        st.audio(f.getvalue(), format='audio/mp3')
        st.rerun()
