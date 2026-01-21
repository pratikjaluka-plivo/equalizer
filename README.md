# The Equalizer - Medical Bill Fighter

> **Exposing Information Asymmetry. Empowering Patients.**

An AI-powered platform that helps patients fight medical bill overcharging by revealing what hospitals already know but patients don't - government-mandated rates, legal leverage points, and evidence-based negotiation strategies.

![Status](https://img.shields.io/badge/status-production%20ready-green)
![License](https://img.shields.io/badge/license-MIT-blue)

---

## Table of Contents

- [Overview](#overview)
- [Use Cases](#use-cases)
- [Features](#features)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [Frontend Components](#frontend-components)
- [Deployment](#deployment)
- [Environment Variables](#environment-variables)

---

## Overview

**The Problem**: Indian patients lose ₹47,000+ Crore annually to medical bill overcharging. Hospitals exploit information asymmetry - they know government rates (CGHS, PMJAY) but charge 200-500% more, knowing patients don't have access to this information.

**The Solution**: The Equalizer levels the playing field by:
1. **Revealing the Truth** - Shows government-mandated rates vs. what you're being charged
2. **Building Evidence** - Compiles court cases, legal sections, and verification data
3. **Providing Weapons** - Pre-written scripts, legal filings, and escalation pathways
4. **Automating Pressure** - Multi-channel escalation across 7+ government portals
5. **Real-Time Assistance** - AI-powered negotiation support during live calls

### The Holy Shit Moment

When you see the split screen:

**LEFT: What You See**
```
Amount Due: ₹5,00,000
```

**RIGHT: What They Know**
```
├── CGHS Rate: ₹35,000
├── They accept this from govt employees
├── Overcharge: 1,329%
├── This is a charitable trust
│   └── MUST provide subsidized care
└── 34 consumer complaints this year
```

---

## Use Cases

### Use Case 1: Medical Bill Dispute

**Scenario**: You received a ₹5,00,000 bill for an appendectomy. You suspect overcharging.

**How Equalizer Helps**:
1. Enter hospital name, procedure, and bill amount
2. Get instant comparison: "CGHS Rate: ₹35,000 | Your Bill: ₹5,00,000 | **Overcharge: 1,329%**"
3. See hospital's vulnerabilities (NABH violations, complaint history, charity obligations)
4. Get pre-written email scripts citing legal sections
5. One-click escalation to Consumer Court, RTI, CPGRAMS

**Expected Outcome**: 40-80% bill reduction based on similar cases

---

### Use Case 2: Live Negotiation Support

**Scenario**: Hospital billing manager calls you to discuss the bill.

**How Equalizer Helps**:
1. Start a "Negotiation Arena" session
2. Share link with the other party for video call
3. As they speak, AI analyzes their claims in real-time
4. You see transparent overlay cards showing:
   - Whether their statement is TRUE/FALSE/MISLEADING
   - Counter-arguments to use
   - Evidence to cite
   - Questions to ask them

**Result**: You never get caught off-guard. Every claim is fact-checked instantly.

---

### Use Case 3: Automated Multi-Channel Escalation

**Scenario**: Hospital ignores your emails and refuses to negotiate.

**How Equalizer Helps**:
1. Create an escalation case
2. System automatically escalates through 8 stages over 30 days:

| Day | Action |
|-----|--------|
| 1 | Email to billing department |
| 3 | Escalate to hospital administrator |
| 5 | Grievance cell complaint |
| 7 | Consumer Court (e-Jagriti) filing |
| 10 | RTI request for hospital's rate card |
| 14 | CPGRAMS central government grievance |
| 21 | Alert healthcare journalists |
| 30 | Social media campaign |

**Result**: Consistent pressure from multiple angles forces response.

---

### Use Case 4: Social Pressure Campaign

**Scenario**: All formal channels have failed. You need public pressure.

**How Equalizer Helps**:
1. Generate AI video with your face exposing the overcharging
2. Get pre-written Twitter threads with relevant hashtags
3. Auto-identify healthcare journalists covering your city
4. Extract Twitter handles of health ministry officials
5. One-click posting across platforms

**Result**: Public visibility often triggers rapid hospital response.

---

### Use Case 5: Valid Bill - Need Financial Help

**Scenario**: Bill is fairly priced but you can't afford it.

**How Equalizer Helps**:
1. System detects bill is at/below government rates
2. Instead of fighting, provides assistance options:
   - Local NGOs that help with medical expenses
   - Government schemes (Ayushman Bharat, ESI, CGHS)
   - Insurance recommendations
   - Crowdfunding platforms

**Result**: Get financial help without unnecessary conflict.

---

### Use Case 6: Crowdsourced Price Intelligence

**Scenario**: You want to know if a hospital's quote is reasonable before treatment.

**How Equalizer Helps**:
1. Search the anonymous price network
2. See what others paid for the same procedure at that hospital
3. Compare across hospitals in your city
4. View percentile rankings (25th, 50th, 75th percentile prices)

**Result**: Make informed decisions before committing to treatment.

---

## Features

### Core Analysis Engine

| Feature | Description |
|---------|-------------|
| **Price Comparison** | CGHS, PMJAY, and market rate comparison |
| **Overcharge Detection** | Classifies bills (Fair → Severe Overcharge) |
| **Hospital Intelligence** | NABH status, complaints, charity obligations |
| **Leverage Analysis** | 20+ vulnerability points scored by severity |
| **Strategy Selection** | Optimal approach based on bill characteristics |
| **Outcome Prediction** | Success probability and expected savings |

### Evidence Building

| Feature | Description |
|---------|-------------|
| **Court Cases** | Real cases from Indian Kanoon |
| **Legal Sections** | Applicable Consumer Protection Act sections |
| **Similar Cases** | Outcomes of comparable disputes |
| **Verification** | NABH registry validation |
| **Evidence Export** | Court-ready Markdown/JSON packages |

### Escalation Tools

| Feature | Description |
|---------|-------------|
| **Auto-Escalation** | 8-stage 30-day automated pipeline |
| **Grievance Blitz** | One-click complaints on 7 portals |
| **Live Escalation** | Real-time streaming actions |
| **Script Generator** | Email, phone, and legal scripts |

### AI-Powered Features

| Feature | Description |
|---------|-------------|
| **Negotiation Arena** | Real-time counter-arguments during video calls |
| **Viral Video Generator** | AI videos with fact-checking (Veo 3.1) |
| **Social Intelligence** | Journalist matching, handle extraction |
| **Dual-LLM Validation** | OpenAI creates, Gemini validates |

### Financial Assistance

| Feature | Description |
|---------|-------------|
| **NGO Database** | City-wise medical assistance NGOs |
| **Government Schemes** | Ayushman Bharat, ESI, CGHS eligibility |
| **Insurance Options** | Recommendations based on profile |
| **Crowdfunding** | Platform suggestions |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│                    (Next.js + React)                            │
├─────────────────────────────────────────────────────────────────┤
│  Landing Page  │  Negotiation Arena  │  Live Escalation         │
│  Bill Input    │  WebRTC Video Call  │  Real-time Streaming     │
│  Results View  │  AI Counter Cards   │  Progress Updates        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND                                  │
│                    (FastAPI + Python)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Analysis   │  │ Intelligence │  │  Strategy    │          │
│  │   Engine     │  │   Modules    │  │  Selector    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐      │
│  │                  INTEGRATIONS                         │      │
│  ├──────────────┬──────────────┬──────────────┬────────┤      │
│  │ Escalation   │ Price        │ Viral Video  │ Live   │      │
│  │ Pipeline     │ Network      │ Generator    │ Actions│      │
│  ├──────────────┼──────────────┼──────────────┼────────┤      │
│  │ Grievance    │ Evidence     │ Social       │ Nego-  │      │
│  │ Blitz        │ Compiler     │ Intelligence │ tiation│      │
│  └──────────────┴──────────────┴──────────────┴────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                             │
├─────────────┬─────────────┬─────────────┬─────────────┬────────┤
│   OpenAI    │   Google    │  Anthropic  │   Plivo     │ Govt   │
│   GPT-4     │   Gemini    │   Claude    │   SMS/WA    │ Portals│
│   DALL-E    │   Veo 3.1   │             │             │        │
└─────────────┴─────────────┴─────────────┴─────────────┴────────┘
```

### Project Structure

```
equalizer/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI entry (40+ endpoints)
│   │   ├── config.py                  # Settings management
│   │   ├── parsers/
│   │   │   └── bill_parser.py         # PDF/image bill parsing
│   │   ├── intelligence/
│   │   │   ├── pricing_engine.py      # CGHS/PMJAY rate comparison
│   │   │   ├── hospital_intel.py      # Hospital vulnerability analysis
│   │   │   ├── leverage_finder.py     # 20+ leverage point detection
│   │   │   ├── real_data.py           # Court cases, evidence
│   │   │   └── financial_assistance.py # NGOs, schemes
│   │   ├── strategy/
│   │   │   ├── strategy_selector.py   # Optimal approach selection
│   │   │   ├── script_generator.py    # Email/phone script generation
│   │   │   └── outcome_predictor.py   # Success probability
│   │   └── integrations/
│   │       ├── escalation_pipeline.py # 8-stage auto-escalation
│   │       ├── price_network.py       # Crowdsourced pricing
│   │       ├── grievance_blitz.py     # Multi-portal complaints
│   │       ├── evidence_compiler.py   # Court-ready packages
│   │       ├── social_intelligence.py # Journalist matching
│   │       ├── live_escalation.py     # Real-time actions
│   │       ├── viral_video.py         # AI video generation
│   │       └── negotiation_arena.py   # Real-time AI assistance
│   ├── requirements.txt
│   └── Procfile                       # Deployment config
├── frontend/
│   ├── src/app/
│   │   ├── page.tsx                   # Main landing page
│   │   ├── call/[peerId]/page.tsx     # Video call join page
│   │   └── components/
│   │       ├── BillInput.tsx          # Bill entry form
│   │       ├── AsymmetryReveal.tsx    # "What they know" reveal
│   │       ├── EvidenceWall.tsx       # Court cases display
│   │       ├── Arsenal.tsx            # Scripts & templates
│   │       ├── PredictionPanel.tsx    # Success prediction
│   │       ├── LiveEscalation.tsx     # Real-time streaming
│   │       ├── NegotiationArena.tsx   # Video call + AI cards
│   │       └── ValidBillAssistance.tsx # Financial help
│   ├── package.json
│   └── .env.local
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- API Keys (optional - graceful fallback if not configured):
  - OpenAI API Key
  - Google Gemini API Key
  - Plivo credentials (for SMS/WhatsApp)
  - Gmail OAuth credentials (for email sending)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your API keys

# Run server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set environment variables
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
echo "NEXT_PUBLIC_WS_URL=ws://localhost:8000" >> .env.local

# Run development server
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## API Reference

### Core Endpoints

#### Analyze Bill
```http
POST /api/analyze
Content-Type: application/json

{
  "hospital_name": "Apollo Hospital",
  "hospital_city": "Mumbai",
  "hospital_state": "Maharashtra",
  "procedure_description": "Appendectomy",
  "total_amount": 500000,
  "patient_income": 600000,
  "patient_state": "Maharashtra"
}
```

**Response**: Complete analysis with price comparison, leverage points, strategies, scripts, and evidence.

#### Health Check
```http
GET /health
```

---

### Escalation Endpoints

#### Create Escalation Case
```http
POST /api/escalation/create
Content-Type: application/json

{
  "hospital_name": "Apollo Hospital",
  "hospital_city": "Mumbai",
  "patient_name": "John Doe",
  "patient_email": "john@example.com",
  "procedure": "Appendectomy",
  "billed_amount": 500000,
  "fair_price": 35000,
  "evidence_summary": "CGHS rate is ₹35,000..."
}
```

#### Get Pending Actions
```http
GET /api/escalation/{case_id}/pending
```

#### Record Hospital Response
```http
POST /api/escalation/{case_id}/response
Content-Type: application/json

{
  "response_type": "partial_refund",
  "details": "Hospital offered 20% reduction"
}
```

---

### Negotiation Arena Endpoints

#### Create Room
```http
POST /api/negotiation/create-room
Content-Type: application/json

{
  "topic": "Medical bill dispute",
  "your_position": "Hospital overcharged 300% above CGHS rates"
}
```

**Response**:
```json
{
  "room_id": "A1B2C3D4",
  "topic": "Medical bill dispute",
  "websocket_url": "/api/negotiation/ws/A1B2C3D4"
}
```

#### WebSocket Connection
```javascript
const ws = new WebSocket('wss://your-backend/api/negotiation/ws/{room_id}');

// Send opponent's statement
ws.send(JSON.stringify({
  type: 'transcript',
  speaker: 'them',
  text: 'Our rates are standard for the industry'
}));

// Receive counter-argument card
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // data.card contains:
  // - verdict: "FALSE" | "MISLEADING" | "PARTIALLY_TRUE" | "TRUE"
  // - counter_argument: "Actually, CGHS rates show..."
  // - evidence: ["CGHS 2024 rate card", "Consumer Court ruling"]
  // - suggested_questions: ["Can you show me your rate card?"]
};
```

#### Get Transcript
```http
GET /api/negotiation/{room_id}/transcript
```

#### Get Summary
```http
GET /api/negotiation/{room_id}/summary
```

---

### Price Network Endpoints

#### Submit Price (Anonymous)
```http
POST /api/prices/submit
Content-Type: application/json

{
  "hospital_name": "Apollo Hospital",
  "city": "Mumbai",
  "procedure": "Appendectomy",
  "amount_charged": 450000,
  "year": 2024
}
```

#### Compare Prices
```http
GET /api/prices/compare?hospital=Apollo Hospital&procedure=Appendectomy
```

#### City Overview
```http
GET /api/prices/city/Mumbai
```

#### Network Stats
```http
GET /api/prices/network-stats
```

---

### Grievance Blitz Endpoints

#### Generate All Complaints
```http
POST /api/grievance-blitz/generate
Content-Type: application/json

{
  "hospital_name": "Apollo Hospital",
  "hospital_city": "Mumbai",
  "patient_name": "John Doe",
  "procedure": "Appendectomy",
  "billed_amount": 500000,
  "fair_price": 35000,
  "evidence_summary": "..."
}
```

**Response**: Pre-filled complaints for e-Jagriti, CPGRAMS, RTI, State Health Dept, NABH, IRDAI.

---

### Viral Video Endpoints

#### Generate Video
```http
POST /api/viral-video/generate
Content-Type: application/json

{
  "hospital_name": "Apollo Hospital",
  "procedure": "Appendectomy",
  "billed_amount": 500000,
  "fair_price": 35000,
  "patient_name": "Anonymous",
  "city": "Mumbai"
}
```

#### Check Status
```http
GET /api/viral-video/status/{video_id}
```

---

### Live Escalation Endpoints

#### Start Session
```http
POST /api/live-escalation/start
Content-Type: application/json

{
  "hospital_name": "Apollo Hospital",
  "hospital_city": "Mumbai",
  "hospital_email": "billing@apollo.com",
  "patient_name": "John Doe",
  "patient_phone": "+919876543210",
  "procedure": "Appendectomy",
  "billed_amount": 500000,
  "fair_price": 35000,
  "evidence_summary": "..."
}
```

#### Stream Updates (Server-Sent Events)
```http
GET /api/live-escalation/{session_id}/stream
```

---

### Financial Assistance Endpoints

#### Get Assistance Options
```http
POST /api/financial-assistance
Content-Type: application/json

{
  "city": "Mumbai",
  "state": "Maharashtra",
  "annual_income": 400000,
  "bill_amount": 200000
}
```

#### Get NGOs by City
```http
GET /api/financial-assistance/ngos/Mumbai
```

#### Get Government Schemes
```http
GET /api/financial-assistance/government-schemes
```

---

## Frontend Components

| Component | File | Purpose |
|-----------|------|---------|
| `BillInput` | `BillInput.tsx` | Form for entering bill details |
| `AsymmetryReveal` | `AsymmetryReveal.tsx` | Animated "what they know" reveal |
| `EvidenceWall` | `EvidenceWall.tsx` | Court cases and verification data |
| `Arsenal` | `Arsenal.tsx` | Tabbed scripts, filings, social posts |
| `PredictionPanel` | `PredictionPanel.tsx` | Success probability visualization |
| `LiveEscalation` | `LiveEscalation.tsx` | Real-time escalation streaming UI |
| `NegotiationArena` | `NegotiationArena.tsx` | Video call with AI counter-argument overlay |
| `ValidBillAssistance` | `ValidBillAssistance.tsx` | Financial assistance for fair bills |

---

## Deployment

### Frontend (Vercel)

1. Push code to GitHub
2. Import project in Vercel
3. Set environment variables:
   - `NEXT_PUBLIC_API_URL` = `https://your-backend.onrender.com`
   - `NEXT_PUBLIC_WS_URL` = `wss://your-backend.onrender.com`
4. Deploy

### Backend (Render)

1. Push code to GitHub
2. Create new Web Service on Render
3. Configure:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables:
   - `OPENAI_API_KEY`
   - `GEMINI_API_KEY`
5. Deploy

---

## Environment Variables

### Backend (.env)

```env
# Required for AI features
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AI...

# Optional - for live actions
PLIVO_AUTH_ID=...
PLIVO_AUTH_TOKEN=...
PLIVO_WHATSAPP_NUMBER=...

# Optional - for email sending
GMAIL_CREDENTIALS_PATH=./credentials/gmail_credentials.json
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 14, React, TypeScript, Tailwind CSS, Framer Motion, PeerJS |
| **Backend** | FastAPI, Python 3.11, Pydantic, WebSocket, SSE |
| **AI/ML** | OpenAI GPT-4, Google Gemini, Anthropic Claude |
| **Video** | Google Veo 3.1, DALL-E (fallback) |
| **Real-time** | WebSocket, Server-Sent Events, WebRTC |
| **Communications** | Gmail API, Plivo (SMS/WhatsApp), Twitter API |

---

## Data Sources

All public/free:
- CGHS Rate Lists (cghs.gov.in)
- PMJAY/Ayushman Bharat Rates
- NABH Hospital Directory
- Indian Kanoon (Court Cases)
- Consumer Protection Act, 2019
- State Healthcare Laws

---

## Legal Disclaimer

This tool is designed to help patients understand their rights and navigate legitimate dispute resolution channels. It:

- Uses only publicly available government rate information
- References real legal sections and court precedents
- Facilitates filing through official government portals
- Does not encourage any illegal activity

Users are responsible for verifying information and using the tool ethically.

---

## License

MIT License - See LICENSE file for details.

---

## Contributing

Contributions welcome! Please open an issue or pull request.

---

## Support

- **Issues**: https://github.com/pratikjaluka-plivo/equalizer/issues

---

**Built with determination to expose information asymmetry and empower patients.**

*Every negotiation you've lost, you lost because they knew more than you. Not anymore.*
