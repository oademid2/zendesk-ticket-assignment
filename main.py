from fastapi import FastAPI, Request
import os
import requests
import logging
from ticket_assignment import assign_ticket_with_details
from zendesk_api import assign_ticket_on_zendesk, get_ticket_details

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

ZENDESK_DOMAIN = os.getenv("ZENDESK_DOMAIN")
ZENDESK_EMAIL = os.getenv("ZENDESK_EMAIL")
ZENDESK_API_TOKEN = os.getenv("ZENDESK_API_TOKEN")

@app.get("/")
def health_check():
    return {"status": "running"}

# @app.post("/")
# async def create_webhook(request: Request):
#     data = await request.json()
#     return {"received": data, "status": "processed"}

@app.post("/")
async def webhook(request: Request):
    """
    Webhook endpoint for Zendesk ticket events.
    Extracts ticket info, uses AI to determine best assignee, and assigns the ticket.
    """
    data = await request.json()
    logger.info(f"Received webhook data: {data}")

    # Extract ticket ID from webhook data
    ticket_id = data.get("ticket_id") or data.get("id")
    
    if not ticket_id:
        logger.error("No ticket_id found in webhook data")
        return {"success": False, "error": "No ticket_id provided"}

    # Get full ticket details from Zendesk
    ticket_details = get_ticket_details(ticket_id)
    
    if not ticket_details:
        logger.error(f"Could not fetch details for ticket {ticket_id}")
        return {"success": False, "error": "Could not fetch ticket details"}
    
    # Extract subject and description
    subject = ticket_details.get("subject", "")
    description = ticket_details.get("description", "")
    
    logger.info(f"Processing ticket {ticket_id}: {subject}")
    
    # Prepare ticket for AI assignment
    new_ticket = {
        "subject": subject,
        "description": description
    }
    
    # Use AI to determine best assignee
    assignment_result = assign_ticket_with_details(new_ticket)
    
    # Log full assignment result
    logger.info(f"AI Assignment Result for ticket {ticket_id}:")
    logger.info(f"  - Assignee ID: {assignment_result.get('assignee_id')}")
    logger.info(f"  - Confidence: {assignment_result.get('confidence')}")
    logger.info(f"  - Reasoning: {assignment_result.get('reasoning')}")
    
    # Extract assignee_id
    assignee_id = assignment_result.get("assignee_id")
    
    if not assignee_id:
        logger.warning(f"No assignee determined for ticket {ticket_id}")
        return {
            "success": False,
            "ticket_id": ticket_id,
            "error": "Could not determine assignee",
            "assignment_result": assignment_result
        }
    
    # Assign ticket on Zendesk
    zendesk_result = assign_ticket_on_zendesk(ticket_id, assignee_id)
    
    logger.info(f"Zendesk assignment result: {zendesk_result}")
    
    return {
        "success": zendesk_result.get("success"),
        "ticket_id": ticket_id,
        "assignment_result": assignment_result,
        "zendesk_result": zendesk_result
    }
