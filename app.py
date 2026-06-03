import streamlit as st
import google.generativeai as genai
import json
from gtts import gTTS
import io

# Cấu hình API Key từ Secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Apprentissage du Français", layout="wide")
st.title("🇫🇷 Application d'Apprentissage du Français")

# 1. Cấu hình
col1, col2, col3 = st.columns(3)
level = col1.selectbox("Niveau:", ["A2", "B1", "B2", "C1"])
role = col2.selectbox("Rôle de l'IA:", ["Employé", "Client", "Ami"])
topic = col3.selectbox("Sujet:", [
    "At the Pharmacy", "Job Interview", "At the Restaurant", "At the Airport", "Booking a Hotel",
    "Asking for Directions", "At the Supermarket", "Doctor's Appointment", "At the Bank", "Renting an Apartment"
])

# 2. Khởi tạo
if "chat" not in st.session_state: st.session_state["chat"] = []
if "unlocked" not in st.session_state: st.session_state["unlocked"] = False
if "quiz" not in st.session_state: st.session_state["quiz"] = None

# 3. Tạo Quiz (Sửa lại lệnh prompt cho chặt chẽ)
if st.button("✨ Générer 20 questions (selon le sujet et niveau)"):
    with st.spinner("Génération..."):
        try:
            # Lệnh nghiêm ngặt hơn
            prompt = f"Tu es un professeur de français. Crée exactement 20 questions à choix multiples (MCQ) pour le sujet '{topic}' au niveau '{level}'. Tu dois utiliser le vocabulaire approprié au contexte où l'IA joue le rôle de '{role}'. Retourne UNIQUEMENT un tableau JSON strict avec les clés: 'q' (question), 'a' (liste de 4 réponses), 'c' (la bonne réponse)."
            res = model.generate_content(prompt)
            clean_text = res.text.replace('json', '').replace('`', '').strip()
            st.session_state["quiz"] = json.loads(clean_text)
            st.rerun()
        except Exception as e: st.error(f"Erreur de génération : {e}")

if st.session_state["quiz"]:
    st.subheader(f"Quiz sur : {topic} ({level})")
    answers = [st.radio(f"{i+1}. {q['q']}", q['a'], key=f"q{i}", index=None) for i, q in enumerate(st.session_state["quiz"])]
    if st.button("Soumettre"):
        score = sum(1 for i, q in enumerate(st.session_state["quiz"]) if answers[i] == q['c'])
        if score >= 14:
            st.session_state["unlocked"] = True
            st.success("Bravo ! Chat débloqué.")
        else: st.error(f"Score: {score}/20. Il faut 14 pour débloquer.")

# 4. Chat & Voice
if st.session_state["unlocked"]:
    st.header("💬 Salle de Chat & Voix")
    for msg in st.session_state["chat"]:
        with st.chat_message(msg["role"]): st.markdown(msg["text"])
    
    # Ghi âm
    audio = st.audio_input("Parlez (Microphone):")
    if audio:
        transcript = model.generate_content([{"mime_type": "audio/wav", "data": audio.read()}, "Transcribe to French text"]).text
        st.session_state["chat"].append({"role": "user", "text": transcript})
        st.rerun()
    
    # Chat văn bản
    if text := st.chat_input("Tapez votre message..."):
        st.session_state["chat"].append({"role": "user", "text": text})
        st.rerun()

    # AI Phản hồi
    if len(st.session_state["chat"]) > 0 and st.session_state["chat"][-1]["role"] == "user":
        with st.spinner("L'IA réfléchit..."):
            res = model.generate_content(f"Rôle: {role}. Sujet: {topic}. Utilisateur a dit: {st.session_state['chat'][-1]['text']}. Répondez en français.")
            st.session_state["chat"].append({"role": "assistant", "text": res.text})
            # Phát âm
            tts = gTTS(res.text, lang='fr')
            f = io.BytesIO()
            tts.write_to_fp(f)
            st.audio(f.getvalue(), format='audio/mp3')
            st.rerun()
