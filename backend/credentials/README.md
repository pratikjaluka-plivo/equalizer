# Credentials Setup Guide

This folder contains credentials for the Live Escalation feature.

## Files in this folder

| File | Purpose | Required? |
|------|---------|-----------|
| `gmail_credentials.json` | Google OAuth client credentials | For real emails |
| `gmail_token.json` | Generated access token (auto-created) | Auto-generated |
| `generate_gmail_token.py` | Helper script to generate token | Utility |

---

## Gmail Setup (for real email sending)

### Step 1: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Note your project ID

### Step 2: Enable Gmail API
1. Go to **APIs & Services** > **Library**
2. Search for "Gmail API"
3. Click **Enable**

### Step 3: Create OAuth Credentials
1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth Client ID**
3. If prompted, configure OAuth consent screen:
   - User Type: External
   - App name: "The Equalizer"
   - Add your email as test user
4. Application type: **Desktop app**
5. Click **Create**
6. Click **Download JSON**

### Step 4: Update gmail_credentials.json
Replace the contents of `gmail_credentials.json` with your downloaded JSON file.

### Step 5: Generate Token
```bash
cd /Users/pratikjaluka/equalizer/backend/credentials
python3 generate_gmail_token.py
```
This opens a browser - sign in and authorize. `gmail_token.json` will be created.

---

## Plivo Setup (for WhatsApp messages)

### Step 1: Create Plivo Account
1. Go to [Plivo](https://www.plivo.com/) and sign up
2. Verify your account

### Step 2: Get API Credentials
1. Go to [Plivo Console](https://console.plivo.com/)
2. Find your **Auth ID** and **Auth Token** on the dashboard

### Step 3: Enable WhatsApp (Optional)
1. Go to **Messaging** > **WhatsApp**
2. Follow Plivo's WhatsApp Business API setup

### Step 4: Update .env
Edit `/Users/pratikjaluka/equalizer/backend/.env`:
```
PLIVO_AUTH_ID=your_actual_auth_id
PLIVO_AUTH_TOKEN=your_actual_auth_token
PLIVO_WHATSAPP_NUMBER=+your_whatsapp_number
```

---

## Going Live

Once credentials are set up, change `DEMO_MODE` in `.env`:
```
DEMO_MODE=false
```

Then restart the backend:
```bash
# Kill existing
lsof -ti:8000 | xargs kill -9

# Restart
cd /Users/pratikjaluka/equalizer/backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Staying in Demo Mode

If you want to keep the dramatic "holy shit" effect without sending real emails:
- Leave `DEMO_MODE=true` in `.env`
- The UI will show all the animations and progress
- No actual emails/messages will be sent
