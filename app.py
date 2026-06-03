import streamlit as st
import google.generativeai as genai
import json
from gtts import gTTS
import io

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
# Sử dụng model đúng với quyền truy cập của bạn
model = genai.GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="Lớp học Tiếng Pháp", layout="wide")
st.title("🇫🇷 Application d'Apprentissage du Français")

# Sidebar
st.sidebar.title("📚 Dictionnaire")
word = st.sidebar.text_input("Chercher un mot:")
if word:
    try:
        res = model.generate_content(f"Explique le mot '{word}' en français simple.")
        st.sidebar.info(res.text)
    except: pass

# Cấu hình
col1, col2, col3 = st.columns(3)
level = col1.selectbox("Niveau:", ["A2", "B1", "B2", "C1"])
role = col2.selectbox("Rôle:", ["Employé", "Client", "Ami"])
topics = ["Pharmacy", "Interview", "Restaurant", "Airport", "Hotel", "Shopping", "Gym", "Hobbies", "Museum", "Weather",
          "Directions", "Supermarket", "Doctor", "Bank", "Apartment", "Train", "Post Office", "Clothes", "Library", "Coffee",
          "Hair Salon", "Trip", "Introduction", "Lost Item", "Art Gallery", "Taxi", "Job Review", "Support", "Birthday", "Dinner Plans"]
topic = col3.selectbox("Sujet:", topics)

if "chat" not in st.session_state: st.session_state["chat"] = []
if "unlocked" not in st.session_state: st.session_state["unlocked"] = False
if "quiz" not in st.session_state: st.session_state["quiz"] = None

# Quiz
if st.button("✨ Générer 20 questions"):
    with st.spinner("Génération..."):
        try:
            prompt = f"Generate 20 MCQ for topic '{topic}' at level {level}. Return ONLY a JSON array with keys: q, a, c."
            res = model.generate_content(prompt)
            # Làm sạch JSON an toàn
            st.session_state["quiz"] = json.loads(res.text.replace('json', '').replace('`', '').strip())
            st.rerun()
        except Exception as e: st.error(f"Erreur: {e}")

if st.session_state["quiz"]:
    answers = [st.radio(f"{i+1}. {q['q']}", q['a'], key=f"q{i}", index=None) for i, q in enumerate(st.session_state["quiz"])]
    if st.button("Soumettre"):
        if sum(1 for i, q in enumerate(st.session_state["quiz"]) if answers[i] == q['c']) >= 14:
            st.session_state["unlocked"] = True
            st.success("Accès Chat débloqué !")
        else: st.error("Besoin de 14/20.")

# Chat
if st.session_state["unlocked"]:
    st.header("💬 Salle de Chat")
    for msg in st.session_state["chat"]:
        with st.chat_message(msg["role"]): st.markdown(msg["text"])
    
    audio = st.audio_input("Parlez (Micro):")
    if audio:
        try:
            transcript = model.generate_content([{"mime_type": "audio/wav", "data": audio.read()}, "Transcribe to French"]).text
            st.session_state["chat"].append({"role": "user", "text": transcript})
            st.rerun()
        except: st.error("Erreur.")
    
    if text := st.chat_input("Message..."):
        st.session_state["chat"].append({"role": "user", "text": text})
        st.rerun()

    if st.session_state["chat"] and st.session_state["chat"][-1]["role"] == "user":
        try:
            res = model.generate_content(f"Rôle: {role}. Sujet: {topic}. Répondez en français: {st.session_state['chat'][-1]['text']}")
            st.session_state["chat"].append({"role": "assistant", "text": res.text})
            tts = gTTS(res.text, lang='fr')
            f = io.BytesIO()
            tts.write_to_fp(f)
            st.audio(f.getvalue(), format='audio/mp3')
            st.rerun()
        except: st.error("Erreur IA.")
