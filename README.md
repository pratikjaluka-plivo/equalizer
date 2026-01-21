# THE EQUALIZER 🏥⚖️

**Medical Bill Fighter for India**

Every negotiation you've lost, you lost because they knew more than you. Not anymore.

![The Equalizer](https://img.shields.io/badge/status-demo%20ready-green)

## What It Does

The Equalizer exposes the information asymmetry between hospitals and patients:

1. **CGHS/PMJAY Rate Comparison** - Shows what the government pays for the same procedure
2. **Hospital Intelligence** - NABH status, complaints, charity care obligations
3. **Leverage Analysis** - Identifies all pressure points against the hospital
4. **Negotiation Scripts** - Ready-to-use emails, phone scripts, legal templates
5. **Outcome Prediction** - Expected savings and success probability

## Quick Start

### 1. Set up your API key

```bash
cd backend
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 2. Run the application

```bash
./start.sh
```

Or run manually:

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### 3. Open http://localhost:3000

## Demo Flow

1. **Intro Screen** - Dramatic stats about medical overcharging
2. **Bill Input** - Enter hospital, procedure, amount
3. **Analysis** - System finds CGHS rates, hospital intel, leverage
4. **The Reveal** - Split screen showing what YOU see vs what THEY know
5. **Arsenal** - All your weapons: emails, scripts, legal templates

## Tech Stack

**Backend:**
- Python 3.12 + FastAPI
- Claude API for bill parsing and script generation
- CGHS/PMJAY rate database

**Frontend:**
- Next.js 14 + TypeScript
- Tailwind CSS (dark theme)
- Framer Motion (animations)

## Data Sources

All public/free:
- CGHS Rate Lists (cghs.gov.in)
- PMJAY/Ayushman Bharat Rates
- NABH Hospital Directory
- Consumer Protection Act, 2019
- State Healthcare Laws

## Project Structure

```
equalizer/
├── backend/
│   └── app/
│       ├── main.py                 # FastAPI entry
│       ├── parsers/                # Bill parsing
│       ├── intelligence/           # Pricing, hospital intel
│       └── strategy/               # Script generation
├── frontend/
│   └── src/
│       └── app/
│           ├── page.tsx            # Main app
│           └── components/         # UI components
└── start.sh                        # Run both servers
```

## The Holy Shit Moment

When you see the split screen:

**LEFT: What You See**
```
Amount Due: ₹47,832
```

**RIGHT: What They Know**
```
├── CGHS Rate: ₹4,847
├── They accept this from govt employees
├── Overcharge: 887%
├── This is a charitable trust
│   └── MUST provide subsidized care
└── 34 consumer complaints this year
```

## License

MIT - Fight your bills, share with others.

---

Built for Demo Day 🚀
