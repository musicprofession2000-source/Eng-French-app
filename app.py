import streamlit as st
import google.generativeai as genai
import json

# Đọc mã từ Secrets của Streamlit (bảo mật tuyệt đối)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("🇫🇷 French Practice App")
topic = st.selectbox("Topic:", ["At the Pharmacy", "Job Interview", "At the Restaurant", "Booking a Hotel"])

if st.button("✨ Generate 20 Questions"):
    with st.spinner("AI is thinking..."):
        try:
            prompt = f"Generate 20 MCQ for topic '{topic}'. Return JSON array with keys q, a, c."
            res = model.generate_content(prompt)
            # Dọn dẹp JSON
            clean_text = res.text.replace('json', '').replace('`', '').strip()
            st.session_state["quiz"] = json.loads(clean_text)
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

if "quiz" in st.session_state and st.session_state["quiz"]:
    for i, q in enumerate(st.session_state["quiz"]):
        st.radio(f"{i+1}. {q['q']}", q['a'], key=f"q{i}")
    if st.button("Submit"):
        st.success("Test submitted!")
