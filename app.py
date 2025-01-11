from flask import Flask, request, jsonify
from twilio.twiml.voice_response import VoiceResponse
import requests
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)

@app.route("/")
def home():
    return "AI Phone Agent is Running! 🚀"

@app.route("/handle_call", methods=["POST"])
def handle_call():
    """Handles incoming Twilio calls, transcribes speech, generates AI response, and plays it back."""
    response = VoiceResponse()
    response.pause(length=1)
    response.say("Hello! Please speak after the beep, and I will respond.")
    response.record(timeout=5, transcribe=False, play_beep=True, action="/process_recording")
    return str(response)

@app.route("/process_recording", methods=["POST"])
def process_recording():
    """Processes the recorded call, transcribes it, generates AI response, and plays the response."""
    response = VoiceResponse()
    recording_url = request.form.get("RecordingUrl")

    if not recording_url:
        response.say("Sorry, I did not receive any audio. Please try again.")
        return str(response)

    print(f"📞 Received Recording URL: {recording_url}")

    transcript = transcribe_audio(recording_url)
    print(f"📝 Transcribed Text: {transcript}")

    ai_response = generate_response(transcript)
    print(f"🤖 AI Response: {ai_response}")

    speech_file = text_to_speech(ai_response)

    if speech_file:
        response.play(speech_file)
    else:
        response.say(ai_response)

    return str(response)

@app.route("/test_tts", methods=["POST"])
def test_tts():
    """Test Text-to-Speech (TTS) using ElevenLabs."""
    data = request.json
    text = data.get("text")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    speech_file = text_to_speech(text)

    if "Error" in speech_file:
        return jsonify({"error": speech_file}), 500

    return jsonify({"message": "TTS success", "audio_file": speech_file})

def transcribe_audio(audio_url):
    """Handles both online and local audio files for transcription."""
    if audio_url.startswith("file://") or os.path.exists(audio_url):
        file_path = audio_url.replace("file://", "")
        print(f"📂 Processing Local File: {file_path}")

        try:
            with open(file_path, "rb") as audio_file:
                audio_data = audio_file.read()
        except FileNotFoundError:
            return "Error: Audio file not found."

        headers = {"Authorization": f"Token {DEEPGRAM_API_KEY}", "Content-Type": "audio/wav"}
        response = requests.post("https://api.deepgram.com/v1/listen", headers=headers, data=audio_data)
    
    else:
        headers = {"Authorization": f"Token {DEEPGRAM_API_KEY}", "Content-Type": "audio/wav"}
        response = requests.get(audio_url, headers=headers)

    if response.status_code == 200:
        return response.json()["results"]["channels"][0]["alternatives"][0]["transcript"]
    else:
        return f"Deepgram Error: {response.text}"

def generate_response(user_input):
    """Generates AI response using Google's Gemini AI."""
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(user_input)
    return response.text

def text_to_speech(text, voice_id="21m00Tcm4TlvDq8ikWAM", output_file="response.mp3"):
    """Converts text to speech using ElevenLabs API."""
    API_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
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
        with open(output_file, "wb") as f:
            f.write(response.content)
        return output_file
    else:
        return f"TTS Error: {response.text}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
