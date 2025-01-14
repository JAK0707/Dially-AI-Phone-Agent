import google.generativeai as genai
import os
from dotenv import load_dotenv


load_dotenv()


api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("❌ Missing Google Gemini API key! Set it in the .env file.")

# Configure the API
genai.configure(api_key=api_key)

def generate_response(user_input):
    """Generates AI response using Google's Gemini AI."""
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(user_input)
    return response.text

# Example Usage
print("AI Response:", generate_response("Tell me about donald trump"))
