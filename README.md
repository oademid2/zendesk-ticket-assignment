# Zendesk Webhook - FastAPI

A simple FastAPI webhook service for Zendesk automation.

## Setup

### 1. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set environment variables
```bash
export ZENDESK_DOMAIN="your-domain.zendesk.com"
export ZENDESK_EMAIL="your-email@example.com"
export ZENDESK_API_TOKEN="your-api-token"
```

### 4. Run locally
```bash
uvicorn main:app --reload
```

## Deployment

This project is ready to deploy to Railway or similar platforms.

### Environment Variables Required:
- `ZENDESK_DOMAIN`
- `ZENDESK_EMAIL`
- `ZENDESK_API_TOKEN`

## Endpoints

- `GET /` - Health check
- `POST /webhook` - Webhook receiver
