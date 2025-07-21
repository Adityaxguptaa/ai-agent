from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

def send_whatsapp_message(body: str):
    client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
    message = client.messages.create(
        from_=os.getenv("TWILIO_FROM"),
        to=os.getenv("TWILIO_TO"),
        body=body
    )
    print("WhatsApp message sent:", message.sid)
