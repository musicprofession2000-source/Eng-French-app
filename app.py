import streamlit as st
import google.generativeai as genai
import json

# Cấu hình bộ não AI Gemini bằng mã API của bạn
genai.configure(api_key="AQ.Ab8RN6JRsOmxntayqxNpPYGem--6FGxfLsu0MkzTcUm2t5orfA")

st.title("🇫🇷 French Practice App (AI Powered)")
st.write("AI will generate 20 vocabulary questions first to prepare you for the conversation!")

st.markdown("---")

# Chọn chủ đề
topic = st.selectbox(
    "👉 Choose a topic to practice:",
    ["At the Pharmacy", "Job Interview", "At the Restaurant", "At the Airport", "Booking a Hotel"]
)

if "quiz_data" not in st.session_state:
    st.session_state["quiz_data"] = None
if "current_topic" not in st.session_state:
    st.session_state["current_topic"] = topic

# Nếu đổi chủ đề thì xóa dữ liệu cũ để AI tạo bộ đề mới
if st.session_state["current_topic"] != topic:
    st.session_state["current_topic"] = topic
    st.session_state["quiz_data"] = None
    if "submitted" in st.session_state: del st.session_state["submitted"]

# Nút bấm bắt đầu tạo đề bằng AI
if st.button("✨ Generate 20 Questions via AI") or st.session_state["quiz_data"] is not None:
    
    if st.session_state["quiz_data"] is None:
        with st.spinner("AI is generating 20 custom questions for your topic... Please wait..."):
            model = genai.GenerativeModel('gemini-pro')
            # Lệnh bắt AI đẻ đúng 20 câu hỏi phục vụ bài nói chuyện
            prompt = f"""
            Generate exactly 20 multiple-choice questions to test English speakers learning French vocabulary and phrases specifically for the topic: '{topic}'. 
            These 20 questions must serve as a preparation (warm-up) for a real-life conversation roleplay about this topic later.
            Return ONLY a valid JSON array of objects, with no markdown formatting, no ```json tags. 
            Each object must have exactly these keys: 'q' (the question in English), 'a' (list of 4 options in French/English), 'c' (the exact correct option from the list).
            """
            try:
                response = model.generate_content(prompt)
                clean_text = response.text.replace("
```json", "").replace("```", "").strip()
                st.session_state["quiz_data"] = json.loads(clean_text)[:20]
            except Exception as e:
                st.error("AI đang bận một chút, bạn bấm nút Thử lại nhé!")
                st.session_state["quiz_data"] = None

    if st.session_state["quiz_data"]:
        st.subheader(f"📝 Vocabulary Warm-up: {topic}")
        user_answers = []
        
        # Hiện 20 câu hỏi ra màn hình
        for i, item in enumerate(st.session_state["quiz_data"]):
            ans = st.radio(f"Question {i+1}: {item['q']}", item['a'], index=None, key=f"ai_q_{i}")
            user_answers.append(ans)
            st.markdown("---")
            
        if st.button("Submit Answers"):
            st.session_state["submitted"] = True
            
        if st.session_state.get("submitted"):
            score = sum(1 for i, item in enumerate(st.session_state["quiz_data"]) if user_answers[i] == item['c'])
            percentage = (score / len(st.session_state["quiz_data"])) * 100
            st.write(f"### Your Score: {score} / {len(st.session_state['quiz_data'])} ({percentage:.1f}%)")
            
            if percentage >= 70:
                st.success("🎉 Excellent! You passed the vocabulary preparation! The AI Chat Roleplay for this topic is now unlocked below!")
                st.markdown("### 💬 AI Roleplay Chatbot")
                st.info(f"AI will now start a conversation with you about '{topic}' using the vocabulary you just practiced!")
                # Khung chat hội thoại sẽ tự xuất hiện ở đây khi bạn pass bài test
                st.chat_input("Type your French response here...")
            else:
                st.error("❌ You need at least 70% to unlock the conversation. Please check your answers and try again!")
