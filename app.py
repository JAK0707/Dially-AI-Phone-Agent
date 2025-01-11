from flask import Flask, request
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

@app.route("/handle_call", methods=["POST"])
def handle_call():
    """Handles incoming Twilio calls, transcribes speech, generates AI response, and plays it back."""
    response = VoiceResponse()

    # Ensure Twilio doesn't wait for user input
    response.pause(length=1)

    # Tell caller to start speaking
    response.say("Hello! Please speak after the beep, and I will respond.")
    response.record(timeout=5, transcribe=False, play_beep=True, action="/process_recording")

    return str(response)

@app.route("/process_recording", methods=["POST"])
def process_recording():
    """Processes the recorded call, transcribes it, generates AI response, and plays the response."""
    response = VoiceResponse()

    # Extract Twilio Recording URL
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

def transcribe_audio(audio_url):
    """Converts spoken audio into text using Deepgram with Twilio Authentication."""
    
    # Twilio Credentials (needed to access the recording)
    TWILIO_SID = os.getenv("TWILIO_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

    # Ensure Twilio authentication is included in the URL request
    response = requests.get(audio_url, auth=(TWILIO_SID, TWILIO_AUTH_TOKEN))
    
    if response.status_code != 200:
        return f"Twilio Error: Unable to fetch recording. Status Code: {response.status_code}"

    # Send the audio to Deepgram for transcription
    headers = {"Authorization": f"Token {DEEPGRAM_API_KEY}", "Content-Type": "audio/wav"}
    deepgram_response = requests.post("https://api.deepgram.com/v1/listen", headers=headers, data=response.content)

    if deepgram_response.status_code == 200:
        return deepgram_response.json()["results"]["channels"][0]["alternatives"][0]["transcript"]
    else:
        return f"Deepgram Error: {deepgram_response.text}"


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
