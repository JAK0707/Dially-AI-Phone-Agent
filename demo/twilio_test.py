from twilio.rest import Client

TWILIO_SID = "AC7c43722a154dca5cfed13b8547682c8c"
TWILIO_AUTH_TOKEN = "b77a135a9f699335c471283a27ccf84f"
TWILIO_PHONE_NUMBER = "+16086056957"  # Your Twilio number
TO_PHONE_NUMBER = "+918955045316"  # Your personal number

def make_call():
    """Places a test phone call via Twilio."""
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

    call = client.calls.create(
        to=TO_PHONE_NUMBER,
        from_=TWILIO_PHONE_NUMBER,
        twiml='<Response><Say>My name is Mathew and I am your daddy</Say></Response>'
    )

    return call.sid

# Test by making a call
print("Call SID:", make_call())
