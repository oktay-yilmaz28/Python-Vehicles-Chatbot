# Chatbot - Ai Assistant

import streamlit as st
import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# --------------------------------------------------
# ENV & Config
# --------------------------------------------------
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")   # Gizlilik !
HF_API_KEY = os.getenv("HF_API_KEY")           # Gizlilik !
genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="Araç LLM Chatbot", layout="centered")

# --------------------------------------------------
st.markdown("""
    <style>
        /* Model seçiciyi sabitleme */
        [data-testid="stVerticalBlock"] > div:has(div.model-header) {
            position: sticky;
            top: 2.8rem;
            background-color: white;
            z-index: 999;
            padding-bottom: 10px;
            border-bottom: 1px solid #ddd;
        }

        /* Kullanıcı mesajlarını sağa yasla */
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
            flex-direction: row-reverse;
            text-align: right;
            background-color: #DCF8C6; 
            border-radius: 15px 0px 15px 15px;
            margin-left: auto;
            width: fit-content;
            max-width: 80%;
        }

        /* Robot mesajlarını sola yasla */
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
            background-color: #F0F2F6; 
            border-radius: 0px 15px 15px 15px;
            margin-right: auto;
            width: fit-content;
            max-width: 80%;
        }

        [data-testid="stChatMessage"] {
            padding: 1rem;
            margin-bottom: 0.5rem;
        }

        @media (prefers-color-scheme: dark) {
            [data-testid="stVerticalBlock"] > div:has(div.model-header) { background-color: #0E1117; }
            [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) { background-color: #056162; color: white; }
            [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) { background-color: #262730; }
        }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------------
#  İlk Mesaj ve Geçmiş
# --------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Merhaba, ben bir robotum, size araçlar hakkında nasıl yardımcı olabilirim?"}
    ]

if "selected_model" not in st.session_state:
    st.session_state.selected_model = "Gemini"

# --------------------------------------------------
# Header
# --------------------------------------------------
header_container = st.container()
with header_container:
    st.markdown('<div class="model-header">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; font-size: 22px; margin-bottom:0;'>🚗 Araç Chatbot 🚗</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.session_state.selected_model = st.segmented_control(
            "Model Seç", ["Gemini", "Hugging Face"],
            default=st.session_state.selected_model,
            label_visibility="collapsed"
        )
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# Sohbet Alanı
# --------------------------------------------------
chat_placeholder = st.container()

with chat_placeholder:
    for msg in st.session_state.messages:
        # Avatar parametresini kaldırdık, varsayılan (ikonlu) hale döndü
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --------------------------------------------------
# LLM Fonksiyonları
# --------------------------------------------------
#GEMINI
def ask_gemini(prompt):
    try:
        
        generation_config = {
            "temperature": 0.4,       # Daha kısa cevaplar için düşük değer.(yaratıcılık)
            "max_output_tokens": 150, # Hugging Face'teki max_tokens ile aynı mantık
            "top_p": 0.8,
            "top_k": 40
        }
        
        model = genai.GenerativeModel(
            model_name="models/gemini-flash-latest",
            generation_config=generation_config
        )
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e: 
        return f"Gemini Hatası: {str(e)}"
    
#HUGGINGFACE
def ask_huggingface(prompt):
    API_URL = "https://router.huggingface.co/v1/chat/completions"
    headers = {"Authorization": f"Bearer {HF_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "deepseek-ai/DeepSeek-R1:fastest",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4, "max_tokens": 300
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        return response.json()["choices"][0]["message"]["content"]
    except: return "Hata oluştu."

# --------------------------------------------------
# Mesaj Gönderme
# --------------------------------------------------
user_input = st.chat_input("Mesajınızı buraya yazın...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    if st.session_state.selected_model == "Gemini":
        answer = ask_gemini(user_input)
    else:
        answer = ask_huggingface(user_input)
        
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()