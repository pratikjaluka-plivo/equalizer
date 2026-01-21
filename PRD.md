# Product Requirements Document (PRD)
# THE EQUALIZER - Medical Bill Fighter for India

**Version:** 1.0
**Date:** January 2025
**Author:** Product Team
**Status:** Demo Ready

---

## 1. Executive Summary

### 1.1 Problem Statement
Indian patients face massive information asymmetry when dealing with hospital bills. Hospitals know exactly what government rates are (CGHS, PMJAY), their own cost structures, and what they can legally charge - but patients have no access to this information. This leads to:

- **₹47,000 Crore** lost annually to medical overcharging in India
- Medical debt as the **#1 cause of financial distress** for Indian families
- Patients paying **300-1000% more** than government-approved rates for the same procedures
- No accessible tools for patients to verify if they're being overcharged

### 1.2 Solution
**The Equalizer** is a web application that eliminates information asymmetry by:
1. Comparing hospital bills against official CGHS and PMJAY government rates
2. Exposing hospital vulnerabilities (NABH status, charitable obligations, complaint history)
3. Finding real court cases where patients won against similar hospitals
4. Generating ready-to-use negotiation scripts (emails, phone scripts, legal complaints)
5. Predicting likely outcomes based on similar cases

### 1.3 Target Users
- Indian patients who received hospital bills they believe are excessive
- Family members handling medical bills for relatives
- Patient advocacy groups
- Healthcare journalists and researchers

---

## 2. Product Vision

### 2.1 Vision Statement
> "Every negotiation you've lost, you lost because they knew more than you. Not anymore."

### 2.2 Success Metrics
| Metric | Target |
|--------|--------|
| Average bill reduction achieved | 40-70% |
| User success rate (any reduction) | 75%+ |
| Time to generate analysis | < 10 seconds |
| User satisfaction score | 4.5/5 |

---

## 3. User Journey

### 3.1 Flow Overview
```
[Landing Page] → [Bill Input] → [Analysis] → [The Reveal] → [Evidence Wall] → [Arsenal]
```

### 3.2 Detailed Flow

#### Stage 1: Landing Page
- Dramatic statistics about medical overcharging in India
- Clear value proposition
- Single CTA: "FIGHT YOUR BILL"

#### Stage 2: Bill Input
User enters:
- Hospital name
- Hospital city & state
- Procedure description
- Total amount billed
- (Optional) Patient income
- (Optional) Itemized charges

#### Stage 3: Analysis Animation
System displays progress:
- "Verifying hospital with NABH registry..."
- "Comparing CGHS & PMJAY government rates..."
- "Searching Indian Kanoon for court cases..."
- "Finding similar case outcomes..."
- "Building bulletproof evidence package..."

#### Stage 4: The Reveal (Holy Shit Moment)
Split-screen dramatic reveal:

**LEFT SIDE: "What You See"**
```
Amount Due: ₹3,20,000
```

**RIGHT SIDE: "What They Know"**
```
├── CGHS Rate: ₹35,000
├── They accept this from govt employees
├── Overcharge: 814%
├── NABH Accredited Hospital
│   └── Bound by standard rates
├── Consumer complaints on record
└── YOUR LEVERAGE: Maximum
```

#### Stage 5: Evidence Wall
Verifiable proof with clickable source links:
- Hospital NABH verification status
- Government rate documents (CGHS, PMJAY)
- Real court cases from Indian Kanoon
- Similar case outcomes with success rates
- Legal rights under Consumer Protection Act

#### Stage 6: Arsenal (Your Weapons)
Ready-to-use scripts:
- Email to hospital billing department
- Escalation email to hospital administrator
- Phone negotiation script with rebuttals
- Consumer court complaint draft
- Social media post (last resort)

---

## 4. Features & Requirements

### 4.1 Core Features

#### F1: Bill Analysis Engine
| Requirement | Priority | Status |
|-------------|----------|--------|
| Parse hospital name and identify in database | P0 | Done |
| Match procedure to CGHS/PMJAY codes | P0 | Done |
| Calculate overcharge percentage | P0 | Done |
| Identify hospital type (private/charitable/govt) | P1 | Done |

#### F2: Price Comparison
| Requirement | Priority | Status |
|-------------|----------|--------|
| CGHS rates for NABH hospitals | P0 | Done |
| CGHS rates for non-NABH hospitals | P0 | Done |
| PMJAY (Ayushman Bharat) rates | P0 | Done |
| Fair market rate range | P1 | Done |

#### F3: Hospital Intelligence
| Requirement | Priority | Status |
|-------------|----------|--------|
| NABH accreditation verification | P0 | Done |
| CGHS empanelment status | P1 | Done |
| PMJAY empanelment status | P1 | Done |
| Charitable trust identification | P1 | Done |
| Complaint history | P2 | Done |

#### F4: Evidence Package
| Requirement | Priority | Status |
|-------------|----------|--------|
| All claims with verifiable sources | P0 | Done |
| Clickable links to official documents | P0 | Done |
| Real court cases from Indian Kanoon | P0 | Done |
| Similar case outcomes | P1 | Done |
| Legal basis citations | P1 | Done |

#### F5: Script Generation
| Requirement | Priority | Status |
|-------------|----------|--------|
| Email to billing department | P0 | Done |
| Escalation email | P0 | Done |
| Phone script with rebuttals | P0 | Done |
| Consumer court complaint draft | P1 | Done |
| Social media post template | P2 | Done |

#### F6: Outcome Prediction
| Requirement | Priority | Status |
|-------------|----------|--------|
| Success probability | P1 | Done |
| Expected discount range | P1 | Done |
| Expected final amount | P1 | Done |
| Time to resolution estimate | P2 | Done |

### 4.2 Data Sources (All Public/Free)

| Source | Data | URL |
|--------|------|-----|
| CGHS | Government-approved rates | https://cghs.gov.in/ |
| PMJAY | Ayushman Bharat rates | https://pmjay.gov.in/ |
| NABH | Hospital accreditation | https://nabh.co/find-a-healthcare-organisation/ |
| Indian Kanoon | Court judgments | https://indiankanoon.org/ |
| Consumer Affairs | Consumer Protection Act | https://consumeraffairs.gov.in/ |
| Consumer Helpline | Filing complaints | http://consumerhelpline.gov.in/public/ |

### 4.3 Verified Legal References

| Case/Law | Citation | URL |
|----------|----------|-----|
| Indian Medical Association vs V.P. Shantha | (1995) 6 SCC 651 | https://indiankanoon.org/doc/723973/ |
| Spring Meadows Hospital vs Harjol Ahluwalia | (1998) 4 SCC 39 | https://indiankanoon.org/doc/1715546/ |
| Consumer Protection Act, 2019 | Act No. 35 of 2019 | https://consumeraffairs.gov.in/pages/consumer-protection-acts |

---

## 5. Technical Architecture

### 5.1 System Overview
```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                            │
│                   (Next.js 14 + TypeScript)                 │
│                                                             │
│  ┌─────────┐  ┌──────────────┐  ┌─────────┐  ┌──────────┐  │
│  │ Bill    │  │ Asymmetry    │  │Evidence │  │ Arsenal  │  │
│  │ Input   │  │ Reveal       │  │ Wall    │  │          │  │
│  └────┬────┘  └──────┬───────┘  └────┬────┘  └────┬─────┘  │
│       │              │               │            │         │
└───────┼──────────────┼───────────────┼────────────┼─────────┘
        │              │               │            │
        └──────────────┴───────┬───────┴────────────┘
                               │
                         REST API
                               │
┌──────────────────────────────┴──────────────────────────────┐
│                         BACKEND                             │
│                    (FastAPI + Python)                       │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Bill Parser │  │ Pricing     │  │ Hospital Intel      │  │
│  │             │  │ Engine      │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Leverage    │  │ Strategy    │  │ Script Generator    │  │
│  │ Finder      │  │ Selector    │  │ (Claude API)        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    Real Data Layer                      ││
│  │  • NABH Verification  • Court Case Search               ││
│  │  • Evidence Builder   • Similar Cases Finder            ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, Framer Motion |
| Backend | Python 3.12, FastAPI, Pydantic |
| AI/LLM | Claude API (script generation) |
| Deployment | Local (Demo) / Vercel + Railway (Production) |

### 5.3 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/api/analyze` | POST | Main analysis endpoint |
| `/api/parse-bill` | POST | Parse uploaded bill (PDF/image) |
| `/api/hospitals/search` | GET | Search hospital database |
| `/api/cghs-rates/{code}` | GET | Get CGHS rate for procedure |

### 5.4 Data Models

#### BillInput
```typescript
interface BillInput {
  hospital_name: string;
  hospital_city: string;
  hospital_state: string;
  procedure_description: string;
  total_amount: number;
  itemized_charges?: Record<string, number>;
  patient_income?: number;
  patient_state: string;
}
```

#### AnalysisResult
```typescript
interface AnalysisResult {
  bill_data: BillData;
  price_comparison: PriceComparison;
  hospital_intel: HospitalIntel;
  leverage_points: LeveragePoints;
  recommended_strategy: Strategy;
  scripts: Scripts;
  predicted_outcome: Prediction;
  verification: Verification;      // NABH status
  evidence: EvidencePackage;       // Verifiable claims
  court_cases: CourtCases;         // Real judgments
  similar_cases: SimilarCases;     // Outcome data
}
```

---

## 6. UI/UX Requirements

### 6.1 Design Principles
1. **Dark theme** - Professional, serious tone
2. **Dramatic reveals** - Build tension before showing information asymmetry
3. **Trust through transparency** - Every claim has a clickable source
4. **Action-oriented** - Clear CTAs, copy-to-clipboard for all scripts

### 6.2 Color Palette
| Color | Hex | Usage |
|-------|-----|-------|
| Background | #000000 | Primary background |
| Text | #FFFFFF | Primary text |
| Success/Your Advantage | #00FF88 | Positive outcomes, your leverage |
| Info/Action | #00D4FF | Links, CTAs, informational |
| Warning/Their Hidden Info | #FF3366 | Overcharge amounts, alerts |
| Muted | #6B7280 | Secondary text |

### 6.3 Key Animations
- **Asymmetry Reveal**: Split-screen animation revealing information gap
- **Evidence Items**: Staggered fade-in for credibility
- **Court Cases**: Cards sliding in with "PATIENT WON" badges
- **Progress Steps**: Sequential checkmarks during analysis

---

## 7. Security & Compliance

### 7.1 Data Privacy
- No user data stored permanently
- No login required
- All analysis done in real-time
- No PII collected beyond session

### 7.2 Legal Disclaimer
- Tool provides information, not legal advice
- Users responsible for verifying information
- Court case summaries are simplified, full judgments linked

### 7.3 Source Attribution
- All data sources clearly cited
- Links to original documents provided
- No proprietary data used

---

## 8. Future Roadmap

### Phase 2 (Post-Demo)
- [ ] Bill upload via PDF/image with OCR
- [ ] User accounts to track cases
- [ ] Integration with actual NABH API
- [ ] Live court case search from Indian Kanoon
- [ ] Multi-language support (Hindi, Tamil, etc.)

### Phase 3 (Scale)
- [ ] Mobile app (React Native)
- [ ] WhatsApp bot integration
- [ ] Partnership with consumer advocacy groups
- [ ] Community forum for sharing outcomes
- [ ] Success story database

### Phase 4 (Expand)
- [ ] Insurance claim disputes
- [ ] Diagnostic lab overcharging
- [ ] Pharmacy price comparison
- [ ] Medical tourism pricing

---

## 9. Success Stories (Expected Outcomes)

### Example Case
**Input:**
- Hospital: Fortis Memorial, Gurgaon
- Procedure: Appendectomy
- Billed: ₹3,20,000

**Output:**
- CGHS Rate: ₹35,000
- Overcharge: 814%
- Similar cases: 74% average discount achieved
- Court precedent: Patients won in similar cases
- Predicted outcome: ₹40,000 - ₹80,000 final payment

**Result:** Patient saves ₹2,40,000 - ₹2,80,000

---

## 10. Appendix

### A. Glossary
| Term | Definition |
|------|------------|
| CGHS | Central Government Health Scheme - government health insurance for central govt employees |
| PMJAY | Pradhan Mantri Jan Arogya Yojana - Ayushman Bharat health insurance for poor |
| NABH | National Accreditation Board for Hospitals and Healthcare Providers |
| NCDRC | National Consumer Disputes Redressal Commission |

### B. Reference Documents
1. Consumer Protection Act, 2019
2. Clinical Establishments Act, 2010
3. CGHS Rate List Circulars
4. PMJAY Health Benefit Packages

### C. Contact
For questions about this PRD, contact the product team.

---

**Document End**
