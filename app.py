import streamlit as st
import google.generativeai as genai
import json
from gtts import gTTS
import io

# 1. Cấu hình
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="French Practice App", layout="wide")
st.title("🇫🇷 French Practice App")

# 2. Sidebar Từ điển
st.sidebar.title("🔍 Từ điển AI")
word = st.sidebar.text_input("Tra từ:")
if word:
    res = model.generate_content(f"Define '{word}' for French learners. Provide meaning, pronunciation, examples.")
    st.sidebar.info(res.text)

# 3. Cấu hình chính
c1, c2, c3 = st.columns(3)
level = c1.selectbox("Trình độ:", ["A2", "B1", "B2", "C1"])
role = c2.selectbox("Vai trò:", ["Nhân viên", "Khách hàng", "Bạn bè"])
topics = ["At the Pharmacy", "Job Interview", "At the Restaurant", "Booking a Hotel"]
topic = c3.selectbox("Chủ đề:", topics)

# Trạng thái
if "quiz" not in st.session_state: st.session_state["quiz"] = None
if "unlocked" not in st.session_state: st.session_state["unlocked"] = False
if "chat" not in st.session_state: st.session_state["chat"] = []

# 4. Quiz
if st.button("✨ Tạo bài Test"):
    res = model.generate_content(f"Generate 20 MCQ for {topic}, level {level}. Return raw JSON array [{{'q':'...','a':['...'],'c':'...'}}]")
    st.session_state["quiz"] = json.loads(res.text.replace('
```json','').replace('```','').strip())
    st.rerun()

if st.session_state["quiz"]:
    answers = [st.radio(q['q'], q['a'], key=f"q{i}", index=None) for i, q in enumerate(st.session_state["quiz"])]
    if st.button("Submit"):
        if sum(1 for i, q in enumerate(st.session_state["quiz"]) if answers[i] == q['c']) >= 14:
            st.session_state["unlocked"] = True
            st.success("Mở khóa Chat!")

# 5. Chat & Voice
if st.session_state["unlocked"]:
    st.header("💬 Phòng Chat")
    for msg in st.session_state["chat"]:
        with st.chat_message(msg["role"]): st.write(msg["text"])
    
    # Ghi âm
    audio = st.audio_input("Nói tiếng Pháp:")
    if audio:
        st.info("Đang xử lý giọng nói...")
        transcript = model.generate_content([{"mime_type": "audio/wav", "data": audio.read()}, "Transcribe to text"]).text
        st.session_state["chat"].append({"role": "user", "text": transcript})
    
    # Nhập text
    if text := st.chat_input("Hoặc gõ tin nhắn..."):
        st.session_state["chat"].append({"role": "user", "text": text})

    # AI trả lời
    if st.session_state["chat"] and st.session_state["chat"][-1]["role"] == "user":
        res = model.generate_content(f"Role: {role}. Topic: {topic}. Reply to: {st.session_state['chat'][-1]['text']}")
        st.session_state["chat"].append({"role": "assistant", "text": res.text})
        # Phát âm
        tts = gTTS(res.text, lang='fr')
        f = io.BytesIO()
        tts.write_to_fp(f)
        st.audio(f.getvalue(), format='audio/mp3')
        st.rerun()
