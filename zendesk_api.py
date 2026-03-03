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


def get_zendesk_config():
    """Get Zendesk configuration from environment variables."""
    domain = os.getenv("ZENDESK_DOMAIN")
    email = os.getenv("ZENDESK_EMAIL")
    api_token = os.getenv("ZENDESK_API_TOKEN")
    
    # Debug logging
    print(f"DEBUG - Zendesk Config:")
    print(f"  Domain: {domain}")
    print(f"  Email: {email}")
    print(f"  API Token: {api_token[:10] + '...' if api_token else None}")
    
    return {
        'domain': domain,
        'email': email,
        'api_token': api_token
    }


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
    config = get_zendesk_config()
    
    if not all([config['domain'], config['email'], config['api_token']]):
        return {
            "success": False,
            "ticket_id": ticket_id,
            "assignee_id": assignee_id,
            "error": "Missing Zendesk configuration"
        }
    
    url = f"https://{config['domain']}/api/v2/tickets/{ticket_id}"
    auth = HTTPBasicAuth(f"{config['email']}/token", config['api_token'])
    
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
    config = get_zendesk_config()
    
    if not all([config['domain'], config['email'], config['api_token']]):
        return None
    
    url = f"https://{config['domain']}/api/v2/tickets/{ticket_id}"
    auth = HTTPBasicAuth(f"{config['email']}/token", config['api_token'])
    
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
        return None
