# EnCode-2025 - AI Phone Agent

https://github.com/user-attachments/assets/7e001673-8f60-4fa3-a830-e908cf4369e5

<video width="100%" controls>
  <source src="https://github.com/YOUR_GITHUB_USERNAME/EnCode-2025/blob/main/tutorial.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

## Overview
This project is an AI-powered phone agent that can handle incoming calls, transcribe user speech, generate AI-driven responses, and convert text responses back to speech for real-time communication. It integrates multiple APIs, including **Twilio, Deepgram, Google Gemini, and ElevenLabs**, to create a natural and dynamic conversational experience.

🚀 **The service is deployed on Render** for seamless cloud-based operation.

📞 **Call this number to use our service:** `‪+1 575-577-7527‬`

---

## Features
- **Handles Incoming Calls:** Uses **Twilio** to receive phone calls.
- **Speech Transcription:** Utilizes **Deepgram** for accurate and fast voice-to-text conversion.
- **AI-Powered Response Generation:** Employs **Google Gemini** to generate human-like responses.
- **Text-to-Speech Conversion:** Uses **ElevenLabs** to generate realistic voice responses.
- **Error Handling & Retries:** Implements robust error handling with request retries.
- **Supports Multiple Conversations:** Allows continuous interactions during a single call.

---

## How It Works - Step-by-Step
1. **Handling Incoming Calls:** Twilio receives calls and records user speech.
2. **Processing the Recording:** The recording URL is fetched and prepared for processing.
3. **Transcribing Speech to Text:** The recorded speech is transcribed using **Deepgram**.
4. **Generating AI Response:** The transcribed text is passed to **Google Gemini** for response generation.
5. **Converting AI Response to Speech:** **ElevenLabs** generates a realistic speech response.
6. **Playing the Response Back:** The generated speech is played back to the caller using **Twilio**.
7. **Continuing the Conversation:** The user can continue the interaction until they hang up.

---

## Flowchart of the Working Model
![image alt](https://github.com/JAK0707/EnCode-2025/blob/01ee1a77421e9fec785ce947cd245872e43de222/flowchart.png)

---

## Technologies Used

| Component          | Technology Used        |
|--------------------|-----------------------|
| Call Handling     | Twilio Voice API       |
| Speech-to-Text    | Deepgram API          |
| AI Responses      | Google Gemini         |
| Text-to-Speech    | ElevenLabs API        |
| Web Framework     | Flask                 |
| Error Handling    | Requests Retry Logic  |
| Deployment        | Render                |

---

## Setup Instructions

### 1️⃣ Clone the Repository
```sh
git clone https://github.com/JAK0707/EnCode-2025.git
cd EnCode-2025
```

### 2️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

### 3️⃣ Set Up Environment Variables
Create a `.env` file and add the following credentials:
```sh
DEEPGRAM_API_KEY=your_deepgram_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
GEMINI_API_KEY=your_gemini_api_key
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
```

### 4️⃣ Run the Flask App
```sh
python app.py
```

### 5️⃣ Expose the Flask App to the Internet
Use **ngrok** to expose the local server for **Twilio** callbacks:
```sh
ngrok http 5000
```
Copy the **ngrok** URL and update your **Twilio webhook** settings.

---

## API Endpoints

| Route                 | Method | Description                  |
|----------------------|--------|------------------------------|
| `/`                 | GET    | Health check endpoint        |
| `/handle_call`      | POST   | Handles incoming calls       |
| `/process_recording`| POST   | Processes recorded audio     |
| `/recording_status` | POST   | Logs recording status updates |
| `/static/<filename>`| GET    | Serves speech files          |


---

## Conclusion
This **AI Phone Agent** is designed for **EnCode-2025** and demonstrates advanced **AI-powered voice automation**. 🚀

