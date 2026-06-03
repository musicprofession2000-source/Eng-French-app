import streamlit as st
import google.generativeai as genai
import json
from gtts import gTTS
import io

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="Apprentissage du Français", layout="wide")
st.title("🇫🇷 Application d'Apprentissage du Français")

# Cấu hình
col1, col2, col3 = st.columns(3)
level = col1.selectbox("Niveau:", ["A2", "B1", "B2", "C1"])
role = col2.selectbox("Rôle:", ["Employé", "Client", "Ami"])
topic = col3.selectbox("Sujet:", ["Pharmacy", "Interview", "Restaurant", "Airport", "Hotel", "Shopping", "Gym", "Hobbies", "Museum", "Weather"])

if "quiz" not in st.session_state: st.session_state["quiz"] = None
if "resultats" not in st.session_state: st.session_state["resultats"] = None

# Quiz Generation
if st.button("✨ Générer 20 questions"):
    with st.spinner("Génération..."):
        prompt = f"Générez 20 questions MCQ en FRANÇAIS pour le sujet '{topic}', niveau {level}. Retournez UNIQUEMENT un JSON array avec clés: q, a (liste de 4), c (réponse correcte)."
        res = model.generate_content(prompt)
        st.session_state["quiz"] = json.loads(res.text.replace('json', '').replace('`', '').strip())
        st.session_state["resultats"] = None
        st.rerun()

# Hiển thị bài test
if st.session_state["quiz"]:
    user_answers = {}
    for i, q in enumerate(st.session_state["quiz"]):
        user_answers[i] = st.radio(f"{i+1}. {q['q']}", q['a'], key=f"q{i}", index=None)

    if st.button("Soumettre et voir les résultats"):
        st.session_state["resultats"] = user_answers
        st.rerun()

    # Hiển thị kết quả chi tiết
    if st.session_state["resultats"]:
        score = 0
        for i, q in enumerate(st.session_state["quiz"]):
            ans = st.session_state["resultats"].get(i)
            if ans == q['c']:
                st.success(f"Câu {i+1} Đúng: {ans}")
                score += 1
            else:
                st.error(f"Câu {i+1} Sai. Bạn chọn: {ans}. Đáp án đúng: {q['c']}")
        
        st.write(f"### Score Final: {score}/20")
        if score >= 10:
            st.success("Accès Chat débloqué !")
            # Logic Chat ở đây...
        else:
            st.warning("Réessayez pour améliorer votre score.")
