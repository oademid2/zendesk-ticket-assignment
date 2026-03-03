from fastapi import FastAPI, Request
import os
import requests

app = FastAPI()

ZENDESK_DOMAIN = os.getenv("ZENDESK_DOMAIN")
ZENDESK_EMAIL = os.getenv("ZENDESK_EMAIL")
ZENDESK_API_TOKEN = os.getenv("ZENDESK_API_TOKEN")

@app.get("/")
def health_check():
    return {"status": "running"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    print("Received webhook:", data)

    # Example: extract ticket ID
    ticket_id = data.get("ticket_id")

    # Example assignment logic placeholder
    # (Replace with your real logic)
    if ticket_id:
        url = f"https://{ZENDESK_DOMAIN}/api/v2/tickets/{ticket_id}.json"
        auth = (f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN)

        requests.put(
            url,
            json={"ticket": {"assignee_id": 123456789}},
            auth=auth
        )

    return {"success": True}
