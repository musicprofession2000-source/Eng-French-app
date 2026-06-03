import streamlit as st
import google.generativeai as genai
import json

# Configure API Key
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="French Practice App", layout="wide")
st.title("🇫🇷 French Practice App")

# UI Settings
col1, col2, col3 = st.columns(3)
level = col1.selectbox("Level:", ["A2", "B1", "B2", "C1"])
ai_role = col2.selectbox("AI Role:", ["Staff", "Customer", "Friend"])
topics = [
    "At the Pharmacy", "Job Interview", "At the Restaurant", "At the Airport", "Booking a Hotel",
    "Asking for Directions", "At the Supermarket", "Doctor's Appointment", "At the Bank", "Renting an Apartment",
    "Buying a Train Ticket", "At the Post Office", "Shopping for Clothes", "At the Gym", "Hobbies",
    "At the Library", "Ordering Coffee", "At the Hair Salon", "Planning a Trip", "Introducing Yourself",
    "Reporting a Lost Item", "At the Museum", "Talking about Weather", "Discussing a Movie", "In a Taxi",
    "Job Review", "Tech Support", "Birthday Party", "Dinner Plans", "Daily Routine"
]
topic = col3.selectbox("Topic:", topics)

# Session State
if "chat_history" not in st.session_state: st.session_state["chat_history"] = []
if "unlocked" not in st.session_state: st.session_state["unlocked"] = False
if "quiz" not in st.session_state: st.session_state["quiz"] = None

# Quiz Generation
if st.button("✨ Generate Quiz"):
    with st.spinner("Generating 20 questions..."):
        try:
            prompt = f"Generate 20 MCQ for topic '{topic}', level {level}. Return ONLY a JSON array with keys: q, a, c."
            res = model.generate_content(prompt)
            # Remove any markdown formatting
            text = res.text.replace('
```json', '').replace('```', '').strip()
            st.session_state["quiz"] = json.loads(text)
            st.rerun()
        except Exception as e:
            st.error(f"Generation error: {e}")

# Quiz Display
if st.session_state["quiz"]:
    st.subheader(f"Quiz: {topic} ({level})")
    answers = [st.radio(f"{i+1}. {q['q']}", q['a'], key=f"q{i}", index=None) for i, q in enumerate(st.session_state["quiz"])]
    if st.button("Check Results"):
        score = sum(1 for i, q in enumerate(st.session_state["quiz"]) if answers[i] == q['c'])
        if score >= 14:
            st.session_state["unlocked"] = True
            st.success(f"Score: {score}/20. Chat unlocked!")
        else:
            st.error(f"Score: {score}/20. Need 14 or more to unlock.")

# Chat Room
if st.session_state["unlocked"]:
    st.header("💬 Chat Room")
    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
        
    if prompt := st.chat_input("Enter your French response..."):
        st.session_state["chat_history"].append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            res = model.generate_content(f"Role: {ai_role}. Topic: {topic}. User: {prompt}. Reply in French and translate.")
            st.session_state["chat_history"].append({"role": "assistant", "content": res.text})
            st.rerun()
