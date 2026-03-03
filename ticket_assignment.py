"""
Ticket Assignment System using OpenAI API
This module assigns new tickets to employees based on similarity to their previous work.
"""

import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, List, Any

# Load environment variables
load_dotenv()

# Initialize OpenAI client lazily
_client = None

def get_openai_client():
    """Get or create OpenAI client instance."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        _client = OpenAI(api_key=api_key)
    return _client


def load_tickets(ticket_file: str = "ticket_data.json") -> List[Dict[str, Any]]:
    """
    Load tickets from JSON file.
    
    Args:
        ticket_file: Path to the ticket data JSON file
        
    Returns:
        List of ticket dictionaries
    """
    with open(ticket_file, 'r') as f:
        return json.load(f)


def get_employee_ticket_history(tickets: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group tickets by assigned employee.
    
    Args:
        tickets: List of all tickets
        
    Returns:
        Dictionary mapping employee IDs to their assigned tickets
    """
    employee_history = {}
    
    for ticket in tickets:
        assignee_id = ticket.get('assignee_id')
        if assignee_id:
            if assignee_id not in employee_history:
                employee_history[assignee_id] = []
            employee_history[assignee_id].append(ticket)
    
    return employee_history


def create_employee_expertise_summary(employee_tickets: List[Dict[str, Any]]) -> str:
    """
    Create a summary of an employee's expertise based on their ticket history.
    
    Args:
        employee_tickets: List of tickets assigned to an employee
        
    Returns:
        String summary of employee's expertise
    """
    summaries = []
    for ticket in employee_tickets[:10]:  # Limit to last 10 tickets to avoid token limits
        subject = ticket.get('subject', 'No subject')
        description = ticket.get('description', 'No description')
        summaries.append(f"Subject: {subject}\nDescription: {description[:200]}")
    
    return "\n\n".join(summaries)


def assign_ticket_to_employee(
    new_ticket: Dict[str, Any],
    existing_tickets: List[Dict[str, Any]],
    model: str = "gpt-4o-mini"
) -> Dict[str, Any]:
    """
    Assign a new ticket to the most suitable employee using OpenAI API.
    
    Args:
        new_ticket: The new ticket to assign (must have 'subject' and 'description')
        existing_tickets: List of existing tickets with assignee information
        model: OpenAI model to use for matching
        
    Returns:
        Dictionary containing:
            - assignee_id: The recommended employee ID
            - confidence: Confidence score (0-1)
            - reasoning: Explanation for the assignment
    """
    # Get employee ticket history
    employee_history = get_employee_ticket_history(existing_tickets)
    
    if not employee_history:
        return {
            "assignee_id": None,
            "confidence": 0.0,
            "reasoning": "No employee history found in existing tickets"
        }
    
    # Extract new ticket information
    new_subject = new_ticket.get('subject', '')
    new_description = new_ticket.get('description', '')
    
    # Build employee expertise profiles
    employee_profiles = {}
    for employee_id, tickets in employee_history.items():
        employee_profiles[employee_id] = {
            "ticket_count": len(tickets),
            "expertise_summary": create_employee_expertise_summary(tickets)
        }
    
    # Create prompt for OpenAI
    prompt = f"""You are an expert ticket assignment system. Analyze the new support ticket and match it to the most suitable employee based on their previous work.

NEW TICKET:
Subject: {new_subject}
Description: {new_description}

EMPLOYEE EXPERTISE PROFILES:
"""
    
    for emp_id, profile in employee_profiles.items():
        prompt += f"\n\nEmployee ID: {emp_id} (Total tickets handled: {profile['ticket_count']})\n"
        prompt += f"Previous tickets:\n{profile['expertise_summary']}\n"
    
    prompt += """

Based on the new ticket's subject and description, which employee would be best suited to handle this ticket?

Respond in JSON format with:
{
    "assignee_id": <employee_id>,
    "confidence": <0.0-1.0>,
    "reasoning": "<brief explanation of why this employee is the best match>"
}
"""
    
    try:
        # Get OpenAI client
        client = get_openai_client()
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a ticket assignment expert. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        # Parse response
        result = json.loads(response.choices[0].message.content)
        
        # Convert assignee_id to int if it's a string
        if isinstance(result.get('assignee_id'), str):
            try:
                result['assignee_id'] = int(result['assignee_id'])
            except (ValueError, TypeError):
                pass
        
        return result
        
    except Exception as e:
        return {
            "assignee_id": None,
            "confidence": 0.0,
            "reasoning": f"Error during assignment: {str(e)}"
        }


def assign_ticket_with_details(
    new_ticket: Dict[str, Any],
    ticket_file: str = "ticket_data.json",
    model: str = "gpt-4o-mini"
) -> Dict[str, Any]:
    """
    Convenience function to assign a ticket using existing ticket data file.
    
    Args:
        new_ticket: The new ticket to assign
        ticket_file: Path to existing tickets JSON file
        model: OpenAI model to use
        
    Returns:
        Assignment result dictionary
    """
    existing_tickets = load_tickets(ticket_file)
    return assign_ticket_to_employee(new_ticket, existing_tickets, model)


if __name__ == "__main__":
    # Example usage
    new_ticket = {
        "subject": "Cannot login to my mortgage account",
        "description": "I've been trying to access my mortgage account for the past hour but keep getting an error message saying 'Invalid credentials'. I'm sure my password is correct. Please help!"
    }
    
    print("Assigning new ticket...")
    print(f"Subject: {new_ticket['subject']}\n")
    
    result = assign_ticket_with_details(new_ticket)
    
    print("Assignment Result:")
    print(f"Recommended Assignee ID: {result['assignee_id']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Reasoning: {result['reasoning']}")
