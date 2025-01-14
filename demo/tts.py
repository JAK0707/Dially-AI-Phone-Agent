import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get ElevenLabs API Key from .env
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# ElevenLabs API URL
API_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

def text_to_speech(text, voice_id="iWNf11sz1GrUE4ppxTOL", output_file="newoutput.mp3"):
    """Converts text to speech using ElevenLabs API."""
    
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "text": text,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
        "model_id": "eleven_multilingual_v2"
    }

    response = requests.post(API_URL.format(voice_id=voice_id), json=payload, headers=headers)

    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"✅ Speech saved as {output_file}")
        return output_file
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return None

# Example Usage (Using Rachel's correct voice ID)
text_to_speech("Hello I am Joe Biden", voice_id="EXAVITQu4vr4xnSDxMaL")
