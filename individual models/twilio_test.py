from twilio.rest import Client
import os
from dotenv import load_dotenv


load_dotenv()


TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
TO_PHONE_NUMBER = os.getenv("TO_PHONE_NUMBER")

def make_call():
    """Places a test phone call via Twilio."""
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

    call = client.calls.create(
        to=TO_PHONE_NUMBER,
        from_=TWILIO_PHONE_NUMBER,
        twiml='<Response><Say>My name is Mathew and I am your daddy</Say></Response>'
    )

    return call.sid


print("Call SID:", make_call())
