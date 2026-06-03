import streamlit as st
import google.generativeai as genai
import json
from gtts import gTTS
import io

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="Apprentissage du Français", layout="wide")
st.title("🇫🇷 Application d'Apprentissage du Français")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    level = st.selectbox("Niveau:", ["A2", "B1", "B2", "C1"])
    role = st.selectbox("Rôle:", ["Employé", "Client", "Ami"])
    topic = st.selectbox("Sujet:", ["Pharmacy", "Interview", "Restaurant", "Airport", "Hotel"])

# Logic Trạng thái
if "quiz" not in st.session_state: st.session_state["quiz"] = None
if "results" not in st.session_state: st.session_state["results"] = None
if "show_chat" not in st.session_state: st.session_state["show_chat"] = False

# 1. Quiz
if st.button("✨ Générer 20 questions"):
    prompt = f"Générez 20 questions MCQ en FRANÇAIS pour le sujet '{topic}', niveau {level}. Retournez UNIQUEMENT un JSON array avec clés: q, a, c."
    res = model.generate_content(prompt)
    st.session_state["quiz"] = json.loads(res.text.replace('json', '').replace('`', '').strip())
    st.session_state["results"] = None
    st.session_state["show_chat"] = False
    st.rerun()

if st.session_state["quiz"]:
    ans = {}
    for i, q in enumerate(st.session_state["quiz"]):
        ans[i] = st.radio(f"{i+1}. {q['q']}", q['a'], key=f"q{i}", index=None)
    
    if st.button("Soumettre"):
        st.session_state["results"] = ans
        st.rerun()

# 2. Kết quả & Lựa chọn tự do
if st.session_state["results"]:
    score = sum(1 for i, q in enumerate(st.session_state["quiz"]) if st.session_state["results"][i] == q['c'])
    st.write(f"### Votre score: {score}/20")
    
    # Nút bấm tự do: Làm lại hoặc Đi tiếp
    col_a, col_b = st.columns(2)
    if col_a.button("🔄 Réessayer"): 
        st.session_state["results"] = None
        st.rerun()
    if col_b.button("🗣️ Accéder au Chat"): 
        st.session_state["show_chat"] = True
        st.rerun()

# 3. Phần Luyện nói (Chat)
if st.session_state["show_chat"]:
    st.markdown("---")
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
