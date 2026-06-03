import streamlit as st
import google.generativeai as genai
import json
from gtts import gTTS
import io

# 1. Cấu hình
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="Apprentissage du Français", layout="wide")
st.title("🇫🇷 Application d'Apprentissage du Français")

# 2. Cấu hình Lớp học (Sidebar)
with st.sidebar:
    st.header("⚙️ Configuration")
    level = st.selectbox("Niveau:", ["A2", "B1", "B2", "C1"])
    role = st.selectbox("Rôle:", ["Employé", "Client", "Ami"])
    topic = st.selectbox("Sujet:", ["Pharmacy", "Interview", "Restaurant", "Airport", "Hotel", "Shopping", "Gym", "Hobbies"])
    st.markdown("---")
    st.header("📚 Dictionnaire")
    word = st.text_input("Chercher un mot:")
    if word:
        res = model.generate_content(f"Explique '{word}' en français.")
        st.info(res.text)

# 3. Quản lý trạng thái
if "quiz" not in st.session_state: st.session_state["quiz"] = None
if "results" not in st.session_state: st.session_state["results"] = None
if "chat_active" not in st.session_state: st.session_state["chat_active"] = False

# 4. Phần Quiz
if st.button("✨ Générer 20 questions"):
    prompt = f"Générez 20 questions MCQ en FRANÇAIS pour le sujet '{topic}', niveau {level}. Retournez UNIQUEMENT un JSON array avec clés: q, a, c."
    res = model.generate_content(prompt)
    st.session_state["quiz"] = json.loads(res.text.replace('json', '').replace('`', '').strip())
    st.session_state["results"] = None
    st.session_state["chat_active"] = False
    st.rerun()

if st.session_state["quiz"]:
    ans = {}
    for i, q in enumerate(st.session_state["quiz"]):
        ans[i] = st.radio(f"{i+1}. {q['q']}", q['a'], key=f"q{i}", index=None)
    
    if st.button("Soumettre"):
        st.session_state["results"] = ans
        st.rerun()

if st.session_state["results"]:
    score = sum(1 for i, q in enumerate(st.session_state["quiz"]) if st.session_state["results"][i] == q['c'])
    st.write(f"### Score: {score}/20")
    
    if score >= 10:
        st.success("Accès Chat débloqué !")
        st.session_state["chat_active"] = True
    else:
        if st.button("🔄 Réessayer"): st.rerun()

# 5. Phần Luyện nói
if st.session_state["chat_active"]:
    st.header("💬 Salle de Chat & Voix")
    if "messages" not in st.session_state: st.session_state["messages"] = []
    
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]): st.markdown(msg["text"])
    
    audio = st.audio_input("Parlez (Micro):")
    if audio:
        txt = model.generate_content([{"mime_type": "audio/wav", "data": audio.read()}, "Transcribe to French"]).text
        st.session_state["messages"].append({"role": "user", "text": txt})
        st.rerun()
        
    if text := st.chat_input("Message..."):
        st.session_state["messages"].append({"role": "user", "text": text})
        st.rerun()

    if st.session_state["messages"] and st.session_state["messages"][-1]["role"] == "user":
        res = model.generate_content(f"Rôle: {role}. Sujet: {topic}. Répondez en français: {st.session_state['messages'][-1]['text']}")
        st.session_state["messages"].append({"role": "assistant", "text": res.text})
        tts = gTTS(res.text, lang='fr')
        f = io.BytesIO()
        tts.write_to_fp(f)
        st.audio(f.getvalue(), format='audio/mp3')
        st.rerun()
