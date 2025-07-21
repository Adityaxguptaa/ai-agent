from fastapi import FastAPI
from gmail_reader import get_gmail_service, check_latest_email
from whatsapp_sender import send_whatsapp_message
import asyncio

app = FastAPI()
gmail_service = get_gmail_service()
last_email_id = None  # Global tracker

@app.on_event("startup")
async def start_email_polling():
    async def poll_emails():
        global last_email_id
        while True:
            print("Checking email...")
            email_id, content = check_latest_email(gmail_service)
            if email_id and email_id != last_email_id:
                last_email_id = email_id
                print("New email detected, sending...")
                send_whatsapp_message(content)
            else:
                print("No new email.")
            await asyncio.sleep(60)  # check every 60 seconds

    asyncio.create_task(poll_emails())

@app.get("/")
def root():
    return {"status": "Email-to-WhatsApp agent running"}
