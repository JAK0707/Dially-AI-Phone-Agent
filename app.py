from flask import Flask, request, jsonify, Response, send_from_directory
import requests
import os
from dotenv import load_dotenv
import google.generativeai as genai
from time import sleep

# Load environment variables
load_dotenv()

# API Keys and Credentials
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EXOTEL_SID = os.getenv("EXOTEL_SID")
EXOTEL_API_KEY = os.getenv("EXOTEL_API_KEY")
EXOTEL_API_TOKEN = os.getenv("EXOTEL_API_TOKEN")
EXOTEL_PHONE_NUMBER = os.getenv("EXOTEL_PHONE_NUMBER")

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)
os.makedirs("static", exist_ok=True)  # Ensure static directory exists

@app.route("/")
def home():
    return "AI Phone Agent (Exotel) is Running! 🚀"

@app.route("/static/<path:filename>")
def serve_static(filename):
    """Serve static files (for audio playback)"""
    return send_from_directory("static", filename)

@app.route("/handle_call", methods=["GET", "POST"])
def handle_call():
    """
    Handles incoming Exotel calls.
    Exotel will send `CallSid`, `From`, `To`, `Direction`, `RecordingUrl`
    """
    call_sid = request.args.get("CallSid", "Unknown")
    caller_number = request.args.get("From", "Unknown")
    recording_url = request.args.get("RecordingUrl", None)
    status = request.args.get("CallType", "Unknown")

    print(f"📞 Incoming Call - Caller: {caller_number}, Status: {status}")

    if recording_url:
        print(f"🎤 Received Recording: {recording_url}")

        # Transcribe the audio
        transcript = transcribe_audio(recording_url)
        print(f"📝 Transcribed Text: {transcript}")

        if "Error" in transcript:
            return generate_exotel_xml("Sorry, I had trouble understanding that. Please try again.")

        # Generate AI response
        ai_response = generate_response(transcript)
        print(f"🤖 AI Response: {ai_response}")

        # Convert to speech
        speech_file = text_to_speech(ai_response)

        if speech_file and not "Error" in speech_file:
            return generate_exotel_xml(f"{request.url_root}{speech_file}")
        else:
            return generate_exotel_xml(ai_response)

    return generate_exotel_xml("Hello! Please speak after the beep, and I will respond.")

def generate_exotel_xml(message):
    """Generates XML response for Exotel"""
    xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Say>{message}</Say>
    </Response>"""
    return Response(xml_response, mimetype="text/xml")

def transcribe_audio(audio_url):
    """Transcribes audio using Deepgram API"""
    if not audio_url:
        return "Error: No audio URL provided"

    try:
        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": "audio/wav"
        }

        response = requests.post(
            "https://api.deepgram.com/v1/listen",
            headers=headers,
            data=requests.get(audio_url).content
        )

        if response.status_code == 200:
            return response.json()["results"]["channels"][0]["alternatives"][0]["transcript"]
        
        return "Error: Failed to transcribe"
    except Exception as e:
        return f"Transcription Error: {str(e)}"

def generate_response(user_input):
    """Generates AI response using Gemini AI"""
    try:
        model = genai.GenerativeModel("gemini-pro")
        prompt = f"""You are a helpful AI phone assistant. 
        Respond to the following user input concisely and naturally: {user_input}
        Keep your response under 100 words and maintain a conversational tone."""
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def text_to_speech(text, voice_id="EXAVITQu4vr4xnSDxMaL"):
    """Converts text to speech using ElevenLabs API"""
    try:
        API_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            },
            "model_id": "eleven_multilingual_v2"
        }

        response = requests.post(API_URL, json=payload, headers=headers)

        if response.status_code == 200:
            output_file = "static/response.mp3"
            with open(output_file, "wb") as f:
                f.write(response.content)
            return output_file
        return f"Error: {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
