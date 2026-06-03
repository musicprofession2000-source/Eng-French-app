import streamlit as st
import google.generativeai as genai

# Cấu hình AI
genai.configure(api_key="AQ.Ab8RN6JRsOmxntayqxNpPYGem--6FGxfLsu0MkzTcUm2t5orfA")
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("🇫🇷 App Luyện Tiếng Pháp")

# Chọn cấu hình
topic = st.selectbox("Chọn chủ đề:", ["At the Pharmacy", "Job Interview", "At the Restaurant"])
if st.button("Bắt đầu trò chuyện"):
    st.session_state["chat"] = True

if st.session_state.get("chat"):
    st.write("Chào bạn! Hãy gõ tiếng Pháp để luyện tập nhé:")
    if "messages" not in st.session_state: st.session_state["messages"] = []
    
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]): st.write(msg["text"])
        
    user_text = st.chat_input("Gõ tại đây...")
    if user_text:
        st.session_state["messages"].append({"role": "user", "text": user_text})
        res = model.generate_content(f"Talk about {topic}. Reply in French and translate to English. User said: {user_text}")
        st.session_state["messages"].append({"role": "assistant", "text": res.text})
        st.rerun()
