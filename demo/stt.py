import requests

DEEPGRAM_API_KEY = "b77dc7018694e9cb0d170f8d1f2a931511e48c06"

def transcribe_audio(audio_url):
    """Converts spoken audio from a call into text."""
    headers = {"Authorization": f"Token {DEEPGRAM_API_KEY}", "Content-Type": "application/json"}
    data = {"url": audio_url}
    
    response = requests.post("https://api.deepgram.com/v1/listen", headers=headers, json=data)
    return response.json()["results"]["channels"][0]["alternatives"][0]["transcript"]

# Example Usage
print(transcribe_audio("https://voiceage.com/wbsamples/in_mono/Adver.wav"))
