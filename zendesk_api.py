"""
Zendesk API Helper Functions
Functions for interacting with Zendesk API including ticket assignment.
"""

import os
import requests
from requests.auth import HTTPBasicAuth
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ZENDESK_DOMAIN = os.getenv("ZENDESK_DOMAIN")
ZENDESK_EMAIL = os.getenv("ZENDESK_EMAIL")
ZENDESK_API_TOKEN = os.getenv("ZENDESK_API_TOKEN")


def assign_ticket_on_zendesk(ticket_id: int, assignee_id: int) -> Dict[str, Any]:
    """
    Assign a ticket to an employee on Zendesk.
    
    Args:
        ticket_id: The Zendesk ticket ID to assign
        assignee_id: The employee ID to assign the ticket to
        
    Returns:
        Dictionary with assignment result:
            - success: Boolean indicating if assignment was successful
            - ticket_id: The ticket ID that was assigned
            - assignee_id: The employee ID assigned to
            - error: Error message if assignment failed
    """
    if not all([ZENDESK_DOMAIN, ZENDESK_EMAIL, ZENDESK_API_TOKEN]):
        return {
            "success": False,
            "ticket_id": ticket_id,
            "assignee_id": assignee_id,
            "error": "Missing Zendesk configuration"
        }
    
    url = f"https://{ZENDESK_DOMAIN}/api/v2/tickets/{ticket_id}.json"
    auth = HTTPBasicAuth(f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN)
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "ticket": {
            "assignee_id": assignee_id
        }
    }
    
    try:
        response = requests.put(url, json=payload, auth=auth, headers=headers)
        response.raise_for_status()
        
        return {
            "success": True,
            "ticket_id": ticket_id,
            "assignee_id": assignee_id,
            "response": response.json()
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "ticket_id": ticket_id,
            "assignee_id": assignee_id,
            "error": str(e)
        }


def get_ticket_details(ticket_id: int) -> Optional[Dict[str, Any]]:
    """
    Get ticket details from Zendesk.
    
    Args:
        ticket_id: The Zendesk ticket ID
        
    Returns:
        Dictionary with ticket details or None if request fails
    """
    if not all([ZENDESK_DOMAIN, ZENDESK_EMAIL, ZENDESK_API_TOKEN]):
        return None
    
    url = f"https://{ZENDESK_DOMAIN}/api/v2/tickets/{ticket_id}.json"
    auth = HTTPBasicAuth(f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN)
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, auth=auth, headers=headers)
        response.raise_for_status()
        return response.json().get('ticket')
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching ticket details: {e}")
        return None
