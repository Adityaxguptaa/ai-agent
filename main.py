from fastapi import FastAPI, BackgroundTasks
from gmail_reader import get_gmail_service, check_latest_email
from whatsapp_sender import send_whatsapp_message
import asyncio

app = FastAPI()
gmail_service = get_gmail_service()

@app.on_event("startup")
async def start_email_polling():
    async def poll_emails():
        while True:
            print("Checking email...")
            snippet = check_latest_email(gmail_service)
            if snippet:
                send_whatsapp_message(f"New Email:\n{snippet}")
            await asyncio.sleep(60)  # Check every 60 seconds

    asyncio.create_task(poll_emails())

@app.get("/")
def root():
    return {"status": "Email-to-WhatsApp agent running"}
