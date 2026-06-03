import streamlit as st
import google.generativeai as genai
import json

# 1. Cấu hình
genai.configure(api_key="AQ.Ab8RN6JRsOmxntayqxNpPYGem--6FGxfLsu0MkzTcUm2t5orfA")
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="French Practice App", layout="wide")
st.title("🇫🇷 French Practice App - Luyện Tiếng Pháp")

# 2. Các mục chọn
col1, col2, col3 = st.columns(3)
level = col1.selectbox("Trình độ:", ["A1", "A2", "B1", "B2"])
ai_role = col2.selectbox("Vai trò AI:", ["Nhân viên", "Khách hàng", "Bạn bè"])
topics = [
    "At the Pharmacy", "Job Interview", "At the Restaurant", "At the Airport", "Booking a Hotel",
    "Asking for Directions", "At the Supermarket", "Doctor's Appointment", "At the Bank", "Renting an Apartment",
    "Buying a Train Ticket", "At the Post Office", "Shopping for Clothes", "At the Gym", "Hobbies",
    "At the Library", "Ordering Coffee", "At the Hair Salon", "Planning a Trip", "Introducing Yourself",
    "Reporting a Lost Item", "At the Museum", "Talking about Weather", "Discussing a Movie", "In a Taxi",
    "Job Review", "Tech Support", "Birthday Party", "Dinner Plans", "Daily Routine"
]
topic = col3.selectbox("Chủ đề:", topics)

# 3. Trạng thái ứng dụng
if "chat_history" not in st.session_state: st.session_state["chat_history"] = []
if "unlocked" not in st.session_state: st.session_state["unlocked"] = False
if "quiz" not in st.session_state: st.session_state["quiz"] = None

# 4. Tạo bài test
if st.button("✨ Tạo bài Test (20 câu)"):
    with st.spinner("AI đang soạn đề..."):
        try:
            prompt = f"Generate 20 MCQ for topic '{topic}', level {level}. Return ONLY a JSON array like: [{{\"q\":\"...\",\"a\":[\"...\",\"...\"],\"c\":\"...\"}}]"
            res = model.generate_content(prompt)
            st.session_state["quiz"] = json.loads(res.text.replace("
```json","").replace("```",""))
        except: st.error("Lỗi tạo đề, hãy thử lại!")

# 5. Kiểm tra kết quả
if st.session_state["quiz"]:
    answers = [st.radio(f"{i+1}. {q['q']}", q['a'], key=f"q{i}", index=None) for i, q in enumerate(st.session_state["quiz"])]
    if st.button("Kiểm tra kết quả"):
        score = sum(1 for i, q in enumerate(st.session_state["quiz"]) if answers[i] == q['c'])
        if score >= 14:
            st.session_state["unlocked"] = True
            st.success(f"Tuyệt vời! Bạn đúng {score}/20. Phòng Chat đã mở.")
        else: st.error(f"Bạn cần đúng 14/20. Bạn chỉ đúng {score} câu.")

# 6. Phòng Chat
if st.session_state["unlocked"]:
    st.header("💬 Phòng Chat Thực Chiến")
    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
        
    if prompt := st.chat_input("Nhập tin nhắn tiếng Pháp..."):
        st.session_state["chat_history"].append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            res = model.generate_content(f"You are {ai_role}. Topic: {topic}. User: {prompt}. Reply in French and translate.")
            st.session_state["chat_history"].append({"role": "assistant", "content": res.text})
            st.rerun()
