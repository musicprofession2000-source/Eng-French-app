import streamlit as st
import google.generativeai as genai
import json
from gtts import gTTS
import io

# Setup API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.0-pro')

st.set_page_config(page_title="French Practice App", layout="wide")
st.title("🇫🇷 French Practice App - Full Version")

# 1. Sidebar Dictionary
st.sidebar.title("Dictionary")
word = st.sidebar.text_input("Look up:")
if word:
    try:
        res = model.generate_content(f"Define '{word}' for French learners.")
        st.sidebar.info(res.text)
    except: pass

# 2. Configs
c1, c2, c3 = st.columns(3)
level = c1.selectbox("Level:", ["A2", "B1", "B2", "C1"])
role = c2.selectbox("Role:", ["Staff", "Customer", "Friend"])
topics = ["Pharmacy", "Interview", "Restaurant", "Airport", "Hotel", "Shopping", "Gym", "Hobbies", "Museum", "Weather"]
topic = c3.selectbox("Topic:", topics)

# Session States
if "chat" not in st.session_state: st.session_state["chat"] = []
if "unlocked" not in st.session_state: st.session_state["unlocked"] = False
if "quiz" not in st.session_state: st.session_state["quiz"] = None

# 3. Quiz Logic
if st.button("✨ Generate 20 Questions"):
    try:
        prompt = f"Generate 20 MCQ for {topic} at level {level}. Return ONLY a JSON array with keys: q, a, c."
        res = model.generate_content(prompt)
        text = res.text.replace('json', '').replace('`', '').strip()
        st.session_state["quiz"] = json.loads(text)
        st.rerun()
    except Exception as e: st.error(f"Error: {e}")

if st.session_state["quiz"]:
    answers = [st.radio(f"{i+1}. {q['q']}", q['a'], key=f"q{i}", index=None) for i, q in enumerate(st.session_state["quiz"])]
    if st.button("Submit Answers"):
        if sum(1 for i, q in enumerate(st.session_state["quiz"]) if answers[i] == q['c']) >= 14:
            st.session_state["unlocked"] = True
            st.success("Chat Unlocked!")
        else: st.error("Need 14/20 to unlock.")

# 4. Chat & Voice
if st.session_state["unlocked"]:
    st.header("💬 Chat & Voice Room")
    for msg in st.session_state["chat"]:
        with st.chat_message(msg["role"]): st.markdown(msg["text"])
    
    audio = st.audio_input("Speak (Microphone):")
    if audio:
        transcript = model.generate_content([{"mime_type": "audio/wav", "data": audio.read()}, "Transcribe to French text"]).text
        st.session_state["chat"].append({"role": "user", "text": transcript})
        st.rerun()

    if text := st.chat_input("Type message..."):
        st.session_state["chat"].append({"role": "user", "text": text})
        st.rerun()

    if st.session_state["chat"] and st.session_state["chat"][-1]["role"] == "user":
        res = model.generate_content(f"Role: {role}. Topic: {topic}. User: {st.session_state['chat'][-1]['text']}. Reply in French.")
        st.session_state["chat"].append({"role": "assistant", "text": res.text})
        tts = gTTS(res.text, lang='fr')
        f = io.BytesIO()
        tts.write_to_fp(f)
        st.audio(f.getvalue(), format='audio/mp3')
        st.rerun()
