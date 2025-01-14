import streamlit as st
import requests
import os
import sounddevice as sd
import numpy as np
import wave
import tempfile
from dotenv import load_dotenv
import google.generativeai as genai
import time

# Load environment variables
load_dotenv()

# API Keys
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

# Streamlit UI
st.title("🎙️ AI Phone Agent")
st.write("Talk live or upload an audio file, and the AI will respond!")

# Option to upload an audio file or record live
option = st.radio("Choose Input Method:", ["🎤 Live Recording", "📂 Upload File"])

# Temporary file to store audio
temp_audio_file = None

if option == "🎤 Live Recording":
    duration = st.slider("Select Recording Duration (seconds):", 3, 15, 5)
    start_recording = st.button("🎙️ Start Recording")

    if start_recording:
        st.write("🔴 Recording... Speak now!")

        fs = 44100  # Sample rate
        seconds = duration

        recording = sd.rec(int(seconds * fs), samplerate=fs, channels=2, dtype=np.int16)
        sd.wait()  # Wait until recording is finished

        # Save the recording as a WAV file
        temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        with wave.open(temp_audio_file.name, "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(fs)
            wf.writeframes(recording.tobytes())

        st.success("✅ Recording complete! Processing your speech...")

elif option == "📂 Upload File":
    uploaded_file = st.file_uploader("Upload an audio file (WAV/MP3)", type=["wav", "mp3"])
    if uploaded_file:
        temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_audio_file.write(uploaded_file.read())
        st.success("✅ File uploaded successfully!")

# Process the audio if available
if temp_audio_file:
    # Transcribe the audio using Deepgram API
    def transcribe_audio(file_path):
        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": "audio/wav"
        }
        with open(file_path, "rb") as audio_file:
            response = requests.post("https://api.deepgram.com/v1/listen", headers=headers, data=audio_file)
        
        if response.status_code == 200:
            return response.json()["results"]["channels"][0]["alternatives"][0]["transcript"]
        return "Error: Could not transcribe audio."

    transcript = transcribe_audio(temp_audio_file.name)
    st.write("📝 **Transcribed Text:**", transcript)

    # Generate AI response
    def generate_response(user_input):
        try:
            model = genai.GenerativeModel("gemini-pro")
            prompt = f"Respond concisely and naturally: {user_input}"
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"

    ai_response = generate_response(transcript)
    st.write("🤖 **AI Response:**", ai_response)

    # Convert AI response to speech
    def text_to_speech(text):
        API_URL = f"https://api.elevenlabs.io/v1/text-to-speech/EXAVITQu4vr4xnSDxMaL"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
            "model_id": "eleven_multilingual_v2"
        }
        response = requests.post(API_URL, json=payload, headers=headers)

        if response.status_code == 200:
            audio_output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            with open(audio_output.name, "wb") as f:
                f.write(response.content)
            return audio_output.name
        return None

    audio_response_file = text_to_speech(ai_response)

    if audio_response_file:
        st.audio(audio_response_file, format="audio/mp3")
        st.download_button(label="⬇️ Download AI Response", data=open(audio_response_file, "rb"), file_name="ai_response.mp3")

st.write("🔹 Speak again or upload another file to continue the conversation!")
