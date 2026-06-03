import streamlit as st
import google.generativeai as genai

st.title("Debugging API Key")

# Kiểm tra xem Secrets đã có chưa
if "GEMINI_API_KEY" in st.secrets:
    st.success("API Key đã được tìm thấy trong Secrets!")
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Kiểm tra xem có lấy được danh sách model không
        models = [m.name for m in genai.list_models()]
        st.write("Các model AI bạn có quyền truy cập là:", models)
    except Exception as e:
        st.error(f"Lỗi khi kết nối tới Google AI: {e}")
else:
    st.error("Chưa tìm thấy API Key trong phần Secrets! Bạn hãy vào Settings -> Secrets dán lại mã nhé.")
