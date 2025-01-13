from flask import Flask, request, jsonify, send_from_directory
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
import requests
import os
import threading
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# API Keys and Credentials
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

# Initialize Twilio Client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)
os.makedirs("static", exist_ok=True)  # Ensure static directory exists

@app.route("/")
def home():
    return "AI Phone Agent is Running! 🚀"

@app.route("/static/<path:filename>")
def serve_static(filename):
    """Serve static files (for audio playback)"""
    return send_from_directory("static", filename)

@app.route("/handle_call", methods=["POST"])
def handle_call():
    """Handles incoming Twilio calls"""
    response = VoiceResponse()
    response.say("Hello! Please speak after the beep, and I will respond.")
    response.record(
        timeout=10,
        transcribe=False,
        play_beep=True,
        action="/process_recording",
        maxLength=30,
        trim='trim-silence',
        recordingFormat='wav'
    )
    return str(response)

@app.route("/process_recording", methods=["POST"])
def process_recording():
    """Processes the recorded call and generates AI response"""
    response = VoiceResponse()
    recording_url = request.form.get("RecordingUrl")

    if not recording_url:
        response.say("Sorry, I did not receive any audio. Please try again.")
        return str(response)

    print(f"📞 Received Recording URL: {recording_url}")

    # Parallelize transcription and AI response
    transcript = [None]
    
    def transcribe():
        transcript[0] = transcribe_audio(recording_url)
    
    transcribe_thread = threading.Thread(target=transcribe)
    transcribe_thread.start()
    transcribe_thread.join()  # Wait for transcription to complete

    if not transcript[0] or "Error" in transcript[0]:
        response.say("Sorry, I had trouble understanding that. Please try again.")
        return str(response)

    print(f"📝 Transcribed Text: {transcript[0]}")

    # Generate AI response
    ai_response = generate_response(transcript[0])
    print(f"🤖 AI Response: {ai_response}")

    # Convert AI response to speech
    speech_file = text_to_speech(ai_response)

    if speech_file and not "Error" in speech_file:
        base_url = request.url_root.rstrip('/')
        audio_url = f"{base_url}/{speech_file}"
        response.play(audio_url)
    else:
        response.say(ai_response)

    # Prompt user for another question
    response.pause(length=2)
    response.say("You can speak again after the beep for another question.")
    response.record(
        timeout=10,
        transcribe=False,
        play_beep=True,
        action="/process_recording",
        maxLength=30,
        trim='trim-silence'
    )

    return str(response)

def transcribe_audio(audio_url):
    """Transcribes audio directly from Twilio recording URL using Deepgram"""
    if not audio_url:
        return "Error: No audio URL provided"

    try:
        headers = {"Authorization": f"Token {DEEPGRAM_API_KEY}"}
        params = {"url": audio_url, "model": "whisper", "tier": "enhanced"}
        
        response = requests.post("https://api.deepgram.com/v1/listen", headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()["results"]["channels"][0]["alternatives"][0]["transcript"]
        else:
            return "Error: Failed to transcribe audio"
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
        return f"Sorry, I encountered an error: {str(e)}"

def text_to_speech(text, voice_id="EXAVITQu4vr4xnSDxMaL"):
    """Converts text to speech using ElevenLabs API with streaming for faster processing"""
    try:
        API_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}
        payload = {
            "text": text,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
            "model_id": "eleven_multilingual_v2"
        }

        response = requests.post(API_URL, json=payload, headers=headers, stream=True)
        
        if response.status_code == 200:
            output_file = "static/response.mp3"
            with open(output_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return output_file
        else:
            return f"TTS Error: {response.text}"
    except Exception as e:
        return f"TTS Error: {str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
