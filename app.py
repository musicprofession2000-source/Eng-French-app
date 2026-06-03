import streamlit as st
import google.generativeai as genai
import json
from gtts import gTTS
import io

# Cấu hình API Key từ Secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="French Practice App", layout="wide")
st.title("🇫🇷 French Practice App")

# Cấu hình
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

# Session State
if "chat" not in st.session_state: st.session_state["chat"] = []
if "unlocked" not in st.session_state: st.session_state["unlocked"] = False
if "quiz" not in st.session_state: st.session_state["quiz"] = None

# Quiz Generation
if st.button("✨ Generate Quiz"):
    with st.spinner("Generating..."):
        try:
            prompt = f"Generate 20 MCQ for {topic}, level {level}. Return ONLY a JSON array with keys: q, a, c."
            res = model.generate_content(prompt)
            # Dọn dẹp phản hồi để tránh lỗi
            text = res.text.replace('json', '').replace('`', '').strip()
            st.session_state["quiz"] = json.loads(text)
            st.rerun()
        except Exception as e:
            st.error(f"Generation error: {e}")

if st.session_state["quiz"]:
    answers = [st.radio(f"{i+1}. {q['q']}", q['a'], key=f"q{i}", index=None) for i, q in enumerate(st.session_state["quiz"])]
    if st.button("Submit Answers"):
        if sum(1 for i, q in enumerate(st.session_state["quiz"]) if answers[i] == q['c']) >= 14:
            st.session_state["unlocked"] = True
            st.success("Chat Unlocked!")
        else: st.error("Need 14/20 to unlock.")

# Chat
if st.session_state["unlocked"]:
    st.header("💬 Chat Room")
    for msg in st.session_state["chat"]:
        with st.chat_message(msg["role"]): st.markdown(msg["text"])
    
    if prompt := st.chat_input("Enter your message..."):
        st.session_state["chat"].append({"role": "user", "text": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            res = model.generate_content(f"Role: {role}. Topic: {topic}. User: {prompt}. Reply in French.")
            st.session_state["chat"].append({"role": "assistant", "text": res.text})
            # Audio
            tts = gTTS(res.text, lang='fr')
            f = io.BytesIO()
            tts.write_to_fp(f)
            st.audio(f.getvalue(), format='audio/mp3')
            st.rerun()
