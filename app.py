import openai
import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import pygame
import re
import io
import time
import base64
import os

# Initialize pygame for text-to-speech playback
pygame.mixer.init()

# OpenAI API setup
API_KEY = "Set OpenAPI Key"
SYSTEM_PROMPT = """
You are a friendly and supportive AI. Your goal is to uplift and encourage users.
If a user expresses an emotion (e.g., sad, happy, angry, frustrated), ask them why.
If they explain, respond with kindness, motivation, humor, or uplifting words.
"""

EMOTIONS = ["sad", "happy", "angry", "frustrated", "excited", "depressed", "anxious", "worried", "stressed", "lonely", "nervous", "bored", "confused"]

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# --------------------------- Utility Functions --------------------------- #

def encode_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# Load Images
bot_image_path = "bot.jpg"
user_image_path = "user.png"
bot_img_base64 = encode_image(bot_image_path)
user_img_base64 = encode_image(user_image_path)

# Text-to-Speech Function
def text_to_speech(text):    
    tts = gTTS(text=text, lang="en")
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)  
    pygame.mixer.music.load(audio_buffer, "mp3")  
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue  

# Speech-to-Text Function
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand that."
    except sr.RequestError:
        return "Could not request results. Please check your internet connection."

# Emotion Detection
def detect_emotion(user_input):
    for emotion in EMOTIONS:
        if re.search(rf"\b{emotion}\b", user_input, re.IGNORECASE):
            return emotion
    return None

# Get Chatbot Response
def get_response(user_input):
    client = openai.Client(api_key=API_KEY)

    detected_emotion = detect_emotion(user_input)
    if detected_emotion:
        response = f"I'm here for you! I noticed you're feeling {detected_emotion}. Can you tell me why?"
        st.session_state.messages.append({"role": "assistant", "content": response})
        return response

    st.session_state.messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4",
        messages=st.session_state.messages
    )

    ai_response = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": ai_response})  
    return ai_response

# --------------------------- UI Design --------------------------- #
st.markdown(
    """
    <style>
        body {
            background-color: #f4f7f9;
        }
        .chat-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            max-width: 700px;
            margin: auto;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
        }
        .message {
            padding: 10px;
            border-radius: 10px;
            margin: 10px 0;            
            align-items: center;
            justify-content: space-between;
        }
        .user-message {
            background: #007bff;
            color: white;
            border-radius: 10px 10px 0 10px;
            padding: 10px 15px;
            max-width: 70%;
        }
        .bot-message {
            background: #f1f1f1;
            color: black;
            border-radius: 10px 10px 10px 0;
            padding: 10px 15px;
            max-width: 70%;
        }
        .bot-avatar, .user-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<h1 style='text-align: center; color: #007bff;'>🤖 Empathetic Chatbot</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>A chatbot that listens, understands, and uplifts you! 💙</p>", unsafe_allow_html=True)

# Show Chat Messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f"""
            <div class="message">
                <span class="user-message">{msg['content']}</span>
                <img src="data:image/png;base64,{user_img_base64}" class="user-avatar">
            </div>
            """,
            unsafe_allow_html=True
        )
    elif msg["role"] == "assistant":
        st.markdown(
            f"""
            <div class="message">
                <img src="data:image/png;base64,{bot_img_base64}" class="bot-avatar">
                <span class="bot-message">{msg['content']}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

# User Input Box
user_text = st.text_input("💬 Type your message:")

# Speak Button
if st.button("🎤 Speak"):
    user_text = speech_to_text()
    st.text(f"You said: {user_text}")

# Show typing animation
if user_text:
    time.sleep(1.5)  # Simulate a short typing delay
    response = get_response(user_text)
    st.text_area("Chatbot Response:", value=response, height=100)
    st.session_state["user_input"] = ""

    if st.button("🔊 Listen to Response"):
        text_to_speech(response)
