import os
import requests
from flask import Flask, request, jsonify
from twilio.twiml.voice_response import VoiceResponse
import google.generativeai as genai
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables from .env file
load_dotenv()

# API Keys
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Configure Google Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)

# Twilio Client
client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)


def transcribe_audio(audio_url):
    """Converts spoken audio into text using Deepgram."""
    headers = {"Authorization": f"Token {DEEPGRAM_API_KEY}", "Content-Type": "application/json"}
    data = {"url": audio_url}

    response = requests.post("https://api.deepgram.com/v1/listen", headers=headers, json=data)
    
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


@app.route("/")
def home():
    return "AI Phone Agent is Running Locally 🚀"


@app.route("/test_stt", methods=["POST"])
def test_stt():
    """Test Speech-to-Text (Deepgram)"""
    data = request.json
    audio_url = data.get("audio_url")

    if not audio_url:
        return jsonify({"error": "No audio URL provided"}), 400

    transcript = transcribe_audio(audio_url)
    return jsonify({"transcript": transcript})


@app.route("/test_nlp", methods=["POST"])
def test_nlp():
    """Test NLP Response (Google Gemini)"""
    data = request.json
    user_input = data.get("text")

    if not user_input:
        return jsonify({"error": "No input text provided"}), 400

    ai_response = generate_response(user_input)
    return jsonify({"response": ai_response})


@app.route("/test_tts", methods=["POST"])
def test_tts():
    """Test Text-to-Speech (ElevenLabs)"""
    data = request.json
    text = data.get("text")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    speech_file = text_to_speech(text)

    if "Error" in speech_file:
        return jsonify({"error": speech_file}), 500

    return jsonify({"message": "TTS success", "audio_file": speech_file})


@app.route("/test_call", methods=["POST"])
def test_call():
    """Test Outgoing Twilio Call"""
    data = request.json
    to_number = data.get("to_number")

    if not to_number:
        return jsonify({"error": "No recipient number provided"}), 400

    call = client.calls.create(
        to=to_number,
        from_=TWILIO_PHONE_NUMBER,
        twiml='<Response><Say>Hello my name is Bunty</Say></Response>'
    )
    
    return jsonify({"message": "Call initiated", "call_sid": call.sid})


@app.route("/handle_call", methods=["POST"])
def handle_call():
    """Handles incoming Twilio calls, processes speech, and plays AI response."""
    response = VoiceResponse()

    # Extract Recording URL from Twilio request
    recording_url = request.form.get("RecordingUrl")

    if not recording_url:
        response.say("Sorry, I did not receive any audio. Please try again.")
        return str(response)

    print(f"📞 Received Recording URL: {recording_url}")

    # Convert speech to text (STT - Deepgram)
    transcript = transcribe_audio(recording_url)
    print(f"📝 Transcribed Text: {transcript}")

    # Generate AI response (NLP - Google Gemini)
    ai_response = generate_response(transcript)
    print(f"🤖 AI Response: {ai_response}")

    # Convert AI response to speech (TTS - ElevenLabs)
    speech_file = text_to_speech(ai_response)

    if speech_file:
        response.play(speech_file)
    else:
        response.say(ai_response)

    return str(response)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
