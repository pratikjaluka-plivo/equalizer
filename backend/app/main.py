from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import json
import asyncio
import uuid

from app.config import get_settings
from app.parsers.bill_parser import parse_bill, BillData
from app.intelligence.pricing_engine import get_price_comparison
from app.intelligence.hospital_intel import get_hospital_intelligence
from app.intelligence.leverage_finder import find_all_leverage
from app.intelligence.real_data import (
    verify_hospital_nabh,
    search_court_cases,
    build_evidence_package,
    find_similar_cases,
    CGHS_RATE_DOCUMENTS,
    PMJAY_RATE_DOCUMENTS
)
from app.strategy.strategy_selector import select_strategy
from app.strategy.script_generator import generate_scripts
from app.strategy.outcome_predictor import predict_outcome
from app.intelligence.financial_assistance import get_financial_assistance, get_ngos_by_city, get_all_government_schemes

# NEW: Multi-system integrations
from app.integrations.escalation_pipeline import escalation_pipeline, EscalationState
from app.integrations.price_network import price_network, PriceSubmission
from app.integrations.grievance_blitz import grievance_blitz
from app.integrations.evidence_compiler import evidence_compiler
from app.integrations.social_intelligence import social_intelligence
from app.integrations.live_escalation import live_escalation_engine
from app.integrations.viral_video import generate_viral_video, VideoRequest, check_video_status
from app.integrations.negotiation_arena import (
    create_session as create_negotiation_session,
    get_session as get_negotiation_session,
    analyze_statement,
    get_transcript,
    get_session_summary,
    transcribe_audio
)
from app.intelligence.smart_analyzer import full_bill_analysis

app = FastAPI(title="The Equalizer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ManualBillInput(BaseModel):
    hospital_name: str
    hospital_city: str
    hospital_state: str
    procedure_description: str
    total_amount: float
    itemized_charges: Optional[dict] = None
    patient_income: Optional[float] = None
    patient_state: str = "Maharashtra"


class AnalysisResponse(BaseModel):
    bill_data: dict
    price_comparison: dict
    hospital_intel: dict
    leverage_points: dict
    recommended_strategy: dict
    scripts: dict
    predicted_outcome: dict
    # NEW: Bulletproof evidence
    verification: dict  # NABH verification, hospital validation
    evidence: dict  # All evidence with sources
    court_cases: dict  # Real court cases
    similar_cases: dict  # Similar cases with outcomes
    # NEW: Financial assistance for valid bills
    financial_assistance: Optional[dict] = None  # NGOs, schemes, insurance when bill is valid


@app.get("/")
def read_root():
    return {"message": "The Equalizer - Medical Bill Fighter", "status": "ready"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_bill(bill_input: ManualBillInput):
    """
    Main analysis endpoint - takes a bill and returns complete intelligence + strategy
    """
    try:
        # Step 1: Structure the bill data
        bill_data = BillData(
            hospital_name=bill_input.hospital_name,
            hospital_city=bill_input.hospital_city,
            hospital_state=bill_input.hospital_state,
            procedure_description=bill_input.procedure_description,
            total_amount=bill_input.total_amount,
            itemized_charges=bill_input.itemized_charges or {},
            patient_income=bill_input.patient_income,
            patient_state=bill_input.patient_state,
        )

        # Step 2: Get price comparison (CGHS, PMJAY, market rates)
        price_comparison = await get_price_comparison(bill_data)

        # Step 3: Get hospital intelligence (NABH status, complaints, ownership)
        hospital_intel = await get_hospital_intelligence(
            bill_data.hospital_name,
            bill_data.hospital_city,
            bill_data.hospital_state
        )

        # Step 4: Find all leverage points
        leverage_points = find_all_leverage(
            bill_data, price_comparison, hospital_intel
        )

        # Step 5: Select optimal strategy
        recommended_strategy = select_strategy(
            bill_data, price_comparison, hospital_intel, leverage_points
        )

        # Step 6: Generate scripts (emails, phone scripts)
        scripts = await generate_scripts(
            bill_data, price_comparison, hospital_intel,
            leverage_points, recommended_strategy
        )

        # Step 7: Predict outcome
        predicted_outcome = predict_outcome(
            bill_data, price_comparison, hospital_intel,
            leverage_points, recommended_strategy
        )

        # Step 8: BULLETPROOF DATA - Verification and evidence
        verification = await verify_hospital_nabh(
            bill_data.hospital_name,
            bill_data.hospital_city
        )

        # Step 9: Build evidence package with sources
        evidence = build_evidence_package(
            procedure=bill_data.procedure_description,
            hospital_name=bill_data.hospital_name,
            billed_amount=bill_data.total_amount,
            cghs_rate=price_comparison.get("cghs_rate_nabh", 0),
            pmjay_rate=price_comparison.get("pmjay_rate", 0),
            hospital_state=bill_data.hospital_state
        )

        # Step 10: Find real court cases
        court_cases = await search_court_cases(bill_data.hospital_name)

        # Step 11: Find similar cases
        similar_cases = await find_similar_cases(
            bill_data.hospital_name,
            bill_data.procedure_description,
            bill_data.total_amount
        )

        # Step 12: Get financial assistance if bill is valid/fair (no dispute needed)
        financial_assistance = None
        if not price_comparison.get("dispute_recommended", True):
            financial_assistance = await get_financial_assistance(
                city=bill_data.hospital_city,
                hospital_name=bill_data.hospital_name,
                bill_amount=bill_data.total_amount,
                procedure=bill_data.procedure_description,
                patient_income=bill_data.patient_income
            )

        return AnalysisResponse(
            bill_data=bill_data.model_dump(),
            price_comparison=price_comparison,
            hospital_intel=hospital_intel,
            leverage_points=leverage_points,
            recommended_strategy=recommended_strategy,
            scripts=scripts,
            predicted_outcome=predicted_outcome,
            verification=verification,
            evidence=evidence,
            court_cases=court_cases,
            similar_cases=similar_cases,
            financial_assistance=financial_assistance,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/parse-bill")
async def parse_bill_file(file: UploadFile = File(...)):
    """
    Parse an uploaded bill (PDF or image) and extract structured data
    """
    try:
        contents = await file.read()
        bill_data = await parse_bill(contents, file.filename)
        return {"success": True, "bill_data": bill_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# SMART BILL ANALYZER - LLM-powered, works for EVERYONE (not just govt employees)
# =============================================================================

@app.post("/api/smart-analyze")
async def smart_analyze_bill(
    file: UploadFile = File(...),
    hospital_name: Optional[str] = None
):
    """
    Smart Bill Analysis - Complete LLM-powered bill analysis.

    This endpoint:
    1. Parses the bill using AI vision (supports PDF and images)
    2. Identifies the procedure, hospital, and all charges
    3. Estimates fair prices using PMJAY rates and market data (NOT CGHS)
    4. Detects billing errors, duplicates, and suspicious charges
    5. Generates negotiation strategy and next steps

    Works for ANY patient - not limited to government employees.

    Parameters:
    - file: Bill image (JPG, PNG) or PDF
    - hospital_name: Optional - pre-selected hospital name for validation

    Returns complete analysis with:
    - Parsed bill data
    - Fair price estimates from multiple sources
    - Overcharge analysis
    - Specific billing issues found
    - Negotiation points
    - Legal references
    - Next steps
    """
    try:
        contents = await file.read()
        result = await full_bill_analysis(
            file_contents=contents,
            filename=file.filename,
            hospital_name=hospital_name
        )
        return {"success": True, **result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/api/pricing-info")
async def get_pricing_info():
    """
    Get information about pricing benchmarks used.

    Returns explanation of different pricing sources and what they mean.
    Helps users understand that CGHS is NOT the only benchmark.
    """
    return {
        "benchmarks": {
            "pmjay": {
                "name": "PMJAY (Ayushman Bharat)",
                "description": "Government health insurance scheme covering 50 crore Indians",
                "who_its_for": "Below Poverty Line families, but rates serve as baseline for all",
                "coverage": "1,950+ procedures with fixed package rates",
                "why_relevant": "Shows what hospitals ACCEPT as payment for procedures",
                "website": "https://pmjay.gov.in"
            },
            "cghs": {
                "name": "CGHS (Central Government Health Scheme)",
                "description": "Health scheme for central government employees and pensioners",
                "who_its_for": "ONLY government employees - NOT for private patients",
                "coverage": "Comprehensive medical coverage",
                "why_relevant": "Often cited but legally only applicable to govt employees",
                "website": "https://cghs.gov.in"
            },
            "market_rates": {
                "name": "Market Average Rates",
                "description": "What hospitals typically charge across different tiers",
                "categories": {
                    "budget": "1.5x PMJAY - Economy/budget hospitals",
                    "standard": "2.5x PMJAY - Regular private hospitals",
                    "premium": "4x PMJAY - Corporate/premium hospitals",
                    "super_premium": "6x PMJAY - Top-tier hospitals (Max, Medanta, Apollo flagship)"
                }
            },
            "insurance_rates": {
                "name": "Insurance TPA Rates",
                "description": "What insurance companies typically approve",
                "typical": "Around 2x PMJAY rates",
                "why_relevant": "Private patients shouldn't pay much more than insured patients"
            }
        },
        "state_regulations": {
            "price_capped_states": ["West Bengal", "Maharashtra (partial)", "Rajasthan"],
            "explanation": "Some states have Clinical Establishments Act rules that cap prices",
            "action": "Check if your state has price regulation"
        },
        "legal_protection": {
            "consumer_protection_act": "Covers medical services, overcharging is unfair trade practice",
            "clinical_establishments_act": "Requires hospitals to display rates, comply with standards",
            "medical_council": "Can complain about unethical practices"
        }
    }


@app.get("/api/pmjay-rates")
async def get_pmjay_rates(procedure: Optional[str] = None):
    """
    Get PMJAY (Ayushman Bharat) rates for procedures.

    These are the baseline rates that hospitals accept under government insurance.
    Useful reference for what procedures SHOULD cost.
    """
    from app.intelligence.smart_analyzer import PMJAY_RATES_2024, _normalize_procedure

    if procedure:
        normalized = _normalize_procedure(procedure)
        rate_data = PMJAY_RATES_2024.get(normalized)
        if rate_data:
            return {
                "procedure": procedure,
                "normalized": normalized,
                "pmjay_rate": rate_data["rate"],
                "package_code": rate_data["code"],
                "typical_stay_days": rate_data["days"],
                "market_estimates": {
                    "budget_hospital": rate_data["rate"] * 1.5,
                    "standard_hospital": rate_data["rate"] * 2.5,
                    "premium_hospital": rate_data["rate"] * 4.0
                }
            }
        else:
            return {"procedure": procedure, "message": "Rate not found in database", "available_procedures": list(PMJAY_RATES_2024.keys())}

    # Return all rates
    return {
        "rates": PMJAY_RATES_2024,
        "note": "PMJAY rates are package rates including room, surgery, medicines, and consumables",
        "source": "National Health Authority (NHA)"
    }


@app.get("/api/hospitals/search")
async def search_hospitals(query: str, city: Optional[str] = None, state: Optional[str] = None):
    """
    Search for hospitals in the database
    """
    from app.data.hospitals import search_hospitals as search_fn
    results = search_fn(query, city, state)
    return {"hospitals": results}


@app.get("/api/cghs-rates/{procedure_code}")
async def get_cghs_rate(procedure_code: str):
    """
    Get CGHS rate for a procedure
    """
    from app.data.cghs_rates import get_rate
    rate = get_rate(procedure_code)
    return {"procedure_code": procedure_code, "rate": rate}


# =============================================================================
# MULTI-SYSTEM INTEGRATION ENDPOINTS
# =============================================================================

# --- Escalation Pipeline ---

class EscalationCreateRequest(BaseModel):
    hospital_name: str
    hospital_city: str
    procedure: str
    billed_amount: float
    fair_amount: float
    patient_email: Optional[str] = None
    patient_name: Optional[str] = None
    hospital_email: Optional[str] = None


@app.post("/api/escalation/create")
async def create_escalation(request: EscalationCreateRequest):
    """
    Create a new auto-escalation case.
    Returns case ID and scheduled actions timeline.
    """
    state = escalation_pipeline.create_case(
        hospital_name=request.hospital_name,
        hospital_city=request.hospital_city,
        procedure=request.procedure,
        billed_amount=request.billed_amount,
        fair_amount=request.fair_amount,
        patient_email=request.patient_email,
        patient_name=request.patient_name,
        hospital_email=request.hospital_email,
    )
    return {
        "success": True,
        "case_id": state.case_id,
        "message": f"Escalation case created. Auto-escalation will begin in 24 hours.",
        "timeline": [
            {"stage": a.stage, "scheduled": a.scheduled_date.isoformat()}
            for a in state.actions
        ],
    }


@app.get("/api/escalation/{case_id}")
async def get_escalation_status(case_id: str):
    """Get status of an escalation case"""
    return escalation_pipeline.get_case_status(case_id)


@app.get("/api/escalation/{case_id}/pending")
async def get_pending_actions(case_id: str):
    """Get pending actions ready for execution"""
    return escalation_pipeline.get_pending_actions(case_id)


@app.get("/api/escalation/{case_id}/n8n-webhook")
async def get_n8n_webhook_payload(case_id: str):
    """Get payload for n8n webhook integration"""
    return escalation_pipeline.get_n8n_webhook_payload(case_id)


@app.post("/api/escalation/{case_id}/pause")
async def pause_escalation(case_id: str, reason: str = "User requested pause"):
    """Pause escalation (e.g., during active negotiation)"""
    return escalation_pipeline.pause_escalation(case_id, reason)


class ResponseRecordRequest(BaseModel):
    response_content: str
    settlement_offered: Optional[float] = None


@app.post("/api/escalation/{case_id}/response")
async def record_response(case_id: str, request: ResponseRecordRequest):
    """Record a response from the hospital"""
    return escalation_pipeline.record_response(
        case_id=case_id,
        response_content=request.response_content,
        settlement_offered=request.settlement_offered,
    )


# --- Crowdsourced Price Network ---

@app.post("/api/prices/submit")
async def submit_price(submission: PriceSubmission):
    """Submit anonymous price data to the network"""
    return price_network.submit_price(submission)


@app.get("/api/prices/compare")
async def compare_prices(
    procedure: str,
    city: str,
    hospital: Optional[str] = None,
    amount: Optional[float] = None,
):
    """Get price comparison from the network"""
    return price_network.get_price_comparison(
        procedure=procedure,
        city=city,
        hospital=hospital,
        amount=amount,
    )


@app.get("/api/prices/city/{city}")
async def get_city_prices(city: str):
    """Get all procedure prices for a city"""
    return price_network.get_city_overview(city)


@app.get("/api/prices/network-stats")
async def get_network_stats():
    """Get overall network statistics"""
    return price_network.get_network_stats()


# --- Multi-Portal Grievance Blitz ---

class GrievanceBlitzRequest(BaseModel):
    hospital_name: str
    hospital_city: str
    hospital_state: str
    procedure: str
    billed_amount: float
    fair_amount: float
    patient_name: str
    patient_address: str
    patient_email: str
    patient_phone: str
    treatment_date: str
    bill_date: str
    has_insurance: bool = False
    insurance_company: Optional[str] = None
    doctor_name: Optional[str] = None
    is_nabh_accredited: bool = True


@app.post("/api/grievance-blitz/generate")
async def generate_grievance_blitz(request: GrievanceBlitzRequest):
    """
    Generate pre-filled grievance filings for multiple platforms.
    One-click generation for e-Jagriti, CPGRAMS, RTI, State Health, NABH, IRDAI.
    """
    return grievance_blitz.generate_blitz(
        hospital_name=request.hospital_name,
        hospital_city=request.hospital_city,
        hospital_state=request.hospital_state,
        procedure=request.procedure,
        billed_amount=request.billed_amount,
        fair_amount=request.fair_amount,
        patient_name=request.patient_name,
        patient_address=request.patient_address,
        patient_email=request.patient_email,
        patient_phone=request.patient_phone,
        treatment_date=request.treatment_date,
        bill_date=request.bill_date,
        has_insurance=request.has_insurance,
        insurance_company=request.insurance_company,
        doctor_name=request.doctor_name,
        is_nabh_accredited=request.is_nabh_accredited,
    )


# --- Evidence Dossier Compiler ---

class EvidenceDossierRequest(BaseModel):
    patient_name: str
    hospital_name: str
    hospital_city: str
    hospital_state: str
    procedure: str
    billed_amount: float
    cghs_rate: float
    pmjay_rate: float
    is_nabh_accredited: bool = True
    is_cghs_empanelled: bool = True
    is_charitable_trust: bool = False


@app.post("/api/evidence/compile")
async def compile_evidence_dossier(request: EvidenceDossierRequest):
    """
    Compile a comprehensive evidence dossier.
    Returns court-ready evidence package with all sources.
    """
    # Get hospital intel for the dossier
    hospital_intel = await get_hospital_intelligence(
        request.hospital_name,
        request.hospital_city,
        request.hospital_state,
    )

    court_cases = await search_court_cases(request.hospital_name)
    similar_cases = await find_similar_cases(
        request.hospital_name,
        request.procedure,
        request.billed_amount,
    )

    dossier = evidence_compiler.compile_dossier(
        patient_name=request.patient_name,
        hospital_name=request.hospital_name,
        hospital_city=request.hospital_city,
        hospital_state=request.hospital_state,
        procedure=request.procedure,
        billed_amount=request.billed_amount,
        cghs_rate=request.cghs_rate,
        pmjay_rate=request.pmjay_rate,
        hospital_intel=hospital_intel,
        court_cases=court_cases.get("hospital_specific_cases", []),
        similar_cases=similar_cases.get("cases", []),
        is_nabh_accredited=request.is_nabh_accredited,
        is_cghs_empanelled=request.is_cghs_empanelled,
        is_charitable_trust=request.is_charitable_trust,
    )

    return dossier.model_dump()


@app.post("/api/evidence/compile/markdown", response_class=PlainTextResponse)
async def compile_evidence_markdown(request: EvidenceDossierRequest):
    """
    Compile evidence dossier and return as markdown.
    Can be downloaded or converted to PDF.
    """
    hospital_intel = await get_hospital_intelligence(
        request.hospital_name,
        request.hospital_city,
        request.hospital_state,
    )

    court_cases = await search_court_cases(request.hospital_name)
    similar_cases = await find_similar_cases(
        request.hospital_name,
        request.procedure,
        request.billed_amount,
    )

    dossier = evidence_compiler.compile_dossier(
        patient_name=request.patient_name,
        hospital_name=request.hospital_name,
        hospital_city=request.hospital_city,
        hospital_state=request.hospital_state,
        procedure=request.procedure,
        billed_amount=request.billed_amount,
        cghs_rate=request.cghs_rate,
        pmjay_rate=request.pmjay_rate,
        hospital_intel=hospital_intel,
        court_cases=court_cases.get("hospital_specific_cases", []),
        similar_cases=similar_cases.get("cases", []),
        is_nabh_accredited=request.is_nabh_accredited,
        is_cghs_empanelled=request.is_cghs_empanelled,
        is_charitable_trust=request.is_charitable_trust,
    )

    return evidence_compiler.export_to_markdown(dossier)


# --- Social Intelligence ---

@app.get("/api/social/hospital-reputation")
async def get_hospital_reputation(hospital_name: str, city: Optional[str] = None):
    """Get aggregated reputation data for a hospital"""
    return social_intelligence.get_hospital_reputation(hospital_name, city).model_dump()


@app.get("/api/social/generate-posts")
async def generate_social_posts(
    hospital_name: str,
    procedure: str,
    billed_amount: float,
    fair_amount: float,
):
    """Generate pre-formatted social media posts"""
    posts = social_intelligence.generate_social_posts(
        hospital_name=hospital_name,
        procedure=procedure,
        billed_amount=billed_amount,
        fair_amount=fair_amount,
    )
    return {"posts": [p.model_dump() for p in posts]}


@app.get("/api/social/similar-patients")
async def find_similar_patients_endpoint(
    hospital_name: str,
    procedure: str,
    city: Optional[str] = None,
):
    """Find other patients with similar disputes"""
    return social_intelligence.find_similar_patients(hospital_name, procedure, city)


@app.get("/api/social/journalists")
async def get_journalist_matches(hospital_name: str, city: str):
    """Find journalists who cover healthcare issues"""
    return social_intelligence.get_journalist_matches(hospital_name, city)


# --- Live Escalation (THE HOLY SHIT MOMENT) ---

class LiveEscalationRequest(BaseModel):
    hospital_name: str
    hospital_city: str
    procedure: str
    billed_amount: float
    fair_amount: float
    patient_name: str
    patient_email: str
    patient_phone: Optional[str] = None
    hospital_email: Optional[str] = None


@app.post("/api/live-escalation/start")
async def start_live_escalation(request: LiveEscalationRequest):
    """
    Start a live escalation session.
    Returns session ID for streaming updates.
    """
    session = live_escalation_engine.create_session(
        hospital_name=request.hospital_name,
        hospital_city=request.hospital_city,
        procedure=request.procedure,
        billed_amount=request.billed_amount,
        fair_amount=request.fair_amount,
        patient_name=request.patient_name,
        patient_email=request.patient_email,
        patient_phone=request.patient_phone,
        hospital_email=request.hospital_email,
    )

    return {
        "session_id": session.session_id,
        "steps": [s.model_dump() for s in session.steps],
        "stream_url": f"/api/live-escalation/{session.session_id}/stream",
    }


@app.get("/api/live-escalation/{session_id}/stream")
async def stream_escalation(session_id: str):
    """
    Stream live escalation updates via Server-Sent Events.
    This is where the magic happens - real-time updates on screen.
    """
    session = live_escalation_engine.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    async def event_generator():
        """Generate SSE events for live escalation"""
        session.status = "running"
        session.started_at = __import__('datetime').datetime.now()

        # Send initial event
        yield f"data: {json.dumps({'type': 'session_started', 'session_id': session_id, 'total_steps': len(session.steps)})}\n\n"

        for i, step in enumerate(session.steps):
            # Step starting
            step.status = "in_progress"
            yield f"data: {json.dumps({'type': 'step_starting', 'step_index': i, 'step_id': step.id, 'step_name': step.name, 'description': step.description})}\n\n"

            # Execute the step
            result = await live_escalation_engine.execute_step(session_id, i)

            # Step completed
            yield f"data: {json.dumps({'type': 'step_completed', 'step_index': i, 'step_id': step.id, 'result': result})}\n\n"

            # Small pause for dramatic effect
            await asyncio.sleep(0.3)

        # Session completed
        session.status = "completed"
        yield f"data: {json.dumps({'type': 'session_completed', 'session_id': session_id})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )


@app.get("/api/live-escalation/{session_id}/status")
async def get_escalation_session_status(session_id: str):
    """Get current status of an escalation session"""
    session = live_escalation_engine.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return session.model_dump()


@app.post("/api/live-escalation/{session_id}/execute-step/{step_index}")
async def execute_single_step(session_id: str, step_index: int):
    """Execute a single escalation step (for manual control)"""
    result = await live_escalation_engine.execute_step(session_id, step_index)
    return result


@app.post("/api/live-escalation/set-demo-mode")
async def set_demo_mode(enabled: bool = True):
    """Toggle demo mode (simulated vs real API calls)"""
    live_escalation_engine.set_demo_mode(enabled)
    return {"demo_mode": enabled}


# =============================================================================
# FINANCIAL ASSISTANCE ENDPOINTS (For Valid Bills)
# =============================================================================

class FinancialAssistanceRequest(BaseModel):
    city: str
    hospital_name: str
    bill_amount: float
    procedure: str
    patient_income: Optional[float] = None


@app.post("/api/financial-assistance")
async def get_financial_help(request: FinancialAssistanceRequest):
    """
    Get financial assistance options for a patient.
    Returns NGOs, government schemes, insurance options, and crowdfunding platforms.
    """
    assistance = await get_financial_assistance(
        city=request.city,
        hospital_name=request.hospital_name,
        bill_amount=request.bill_amount,
        procedure=request.procedure,
        patient_income=request.patient_income
    )
    return assistance


@app.get("/api/financial-assistance/ngos/{city}")
async def get_city_ngos(city: str):
    """Get NGOs that provide medical financial assistance in a specific city"""
    ngos = get_ngos_by_city(city)
    return {
        "city": city,
        "ngos": ngos,
        "national_helplines": [
            {"name": "PM Relief Fund", "contact": "Apply online at pmnrf.gov.in"},
            {"name": "Ayushman Bharat Helpline", "contact": "14555"},
            {"name": "Health Ministry Helpline", "contact": "1800-180-1104"},
        ]
    }


@app.get("/api/financial-assistance/government-schemes")
async def get_govt_schemes():
    """Get all government health schemes"""
    schemes = get_all_government_schemes()
    return {
        "schemes": schemes,
        "note": "Eligibility varies. Check individual scheme websites for detailed criteria.",
        "quick_check": {
            "ayushman_bharat": "mera.pmjay.gov.in",
            "esi": "esic.nic.in",
            "cghs": "cghs.gov.in"
        }
    }


@app.get("/api/financial-assistance/insurance-options")
async def get_insurance_options_endpoint(
    coverage_needed: Optional[float] = None,
    age: Optional[int] = None
):
    """Get health insurance recommendations"""
    from app.intelligence.financial_assistance import INSURANCE_RECOMMENDATIONS

    recommendations = INSURANCE_RECOMMENDATIONS
    if coverage_needed:
        # Filter by coverage amount
        recommendations = [
            r for r in recommendations
            if any(coverage_needed <= 5000000 for _ in r.get("plans", []))  # Simplified filter
        ]

    return {
        "recommendations": recommendations,
        "tax_benefits": {
            "section_80D": "Deduction up to Rs 25,000 for self (Rs 50,000 for senior citizens)",
            "family_coverage": "Additional Rs 25,000 for parents' premium",
            "preventive_checkup": "Rs 5,000 additional for health checkups"
        },
        "tips": [
            "Compare coverage, not just premium",
            "Check network hospitals in your city",
            "Look for no-claim bonus features",
            "Consider family floater for better value",
            "Check waiting periods for pre-existing conditions"
        ]
    }


# =============================================================================
# VIRAL VIDEO GENERATOR ENDPOINTS (AI-Generated Threat Videos for X/Twitter)
# =============================================================================

class ViralVideoRequest(BaseModel):
    user_photo_base64: str  # Base64 encoded user photo from webcam
    patient_name: str
    hospital_name: str
    hospital_city: str
    procedure: str
    billed_amount: float
    fair_amount: float
    overcharge_percentage: float


@app.post("/api/viral-video/generate")
async def create_viral_video(request: ViralVideoRequest):
    """
    Generate an AI video with the user's face threatening legal action.
    Optimized for virality on X/Twitter.

    Uses D-ID for video generation (free tier available).
    Falls back to viral poster image if video fails.
    """
    video_request = VideoRequest(
        user_photo_base64=request.user_photo_base64,
        patient_name=request.patient_name,
        hospital_name=request.hospital_name,
        hospital_city=request.hospital_city,
        procedure=request.procedure,
        billed_amount=request.billed_amount,
        fair_amount=request.fair_amount,
        overcharge_percentage=request.overcharge_percentage,
    )

    result = await generate_viral_video(video_request)

    return {
        "success": result.success,
        "video_url": result.video_url,
        "video_id": result.video_id,
        "script": result.script,
        "thumbnail_url": result.thumbnail_url,
        "twitter_text": result.twitter_text,
        "fallback_used": result.fallback_used,
        "error": result.error,
        "tip": "Download the video and upload directly to X/Twitter for best engagement"
    }


@app.get("/api/viral-video/status/{video_id}")
async def get_video_status(video_id: str):
    """Check the status of a video generation request"""
    status = await check_video_status(video_id)
    return status


@app.get("/api/viral-video/config")
async def get_viral_video_config():
    """Get configuration status for viral video generation"""
    import os
    return {
        "did_configured": bool(os.getenv("DID_API_KEY")),
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "dual_llm_active": bool(os.getenv("OPENAI_API_KEY")) and bool(os.getenv("GEMINI_API_KEY")),
        "video_engine": "D-ID (Primary) + Veo 3.1 (Fallback)",
        "video_flow": {
            "1_primary": "D-ID - Talking head video from your photo (RECOMMENDED)",
            "2_secondary": "Veo 3.1 - AI video generation (if D-ID fails)",
            "3_fallback": "DALL-E - Viral poster image (if all video fails)"
        },
        "script_flow": {
            "1_generate": "OpenAI GPT-4 creates viral script",
            "2_validate": "Gemini verifies all facts & numbers",
            "3_correct": "Auto-corrects any hallucinations"
        },
        "features": {
            "did_video": "D-ID animates your photo into a talking head video",
            "veo_video": "Veo 3.1 generates AI video (fallback)",
            "dual_llm": "OpenAI + Gemini prevents hallucination",
            "twitter_text": "Pre-written viral post with hashtags",
            "poster_fallback": "DALL-E poster if video fails"
        },
        "setup": {
            "did_api_key": "Get from https://studio.d-id.com/ (free tier available)",
            "gemini_api_key": "Get from https://aistudio.google.com/",
            "openai_api_key": "Get from https://platform.openai.com/"
        }
    }


# =============================================================================
# NEGOTIATION ARENA - Real-time AI-powered video call assistant
# =============================================================================

# Store active WebSocket connections
active_connections: Dict[str, List[WebSocket]] = {}


class NegotiationCreateRequest(BaseModel):
    topic: str  # e.g., "Medical bill negotiation", "Salary negotiation", "Vendor contract"
    your_position: str  # e.g., "The bill is overcharged by 300%"


class TranscriptMessage(BaseModel):
    speaker: str  # "you" or "them"
    text: str


@app.post("/api/negotiation/create-room")
async def create_negotiation_room(request: NegotiationCreateRequest):
    """
    Create a new negotiation room.
    Returns room_id for WebRTC signaling and AI assistance.
    """
    room_id = str(uuid.uuid4())[:8].upper()

    session = create_negotiation_session(
        room_id=room_id,
        topic=request.topic,
        your_position=request.your_position
    )

    return {
        "room_id": room_id,
        "topic": session.topic,
        "your_position": session.your_position,
        "websocket_url": f"/api/negotiation/ws/{room_id}",
        "join_url": f"/negotiation/{room_id}",
        "instructions": {
            "1": "Share the room_id with the other party for video call",
            "2": "Connect via WebSocket for real-time AI counter-arguments",
            "3": "Speak naturally - AI will analyze their statements and suggest counters",
            "4": "Counter cards appear as transparent overlays only on YOUR screen"
        }
    }


@app.get("/api/negotiation/{room_id}")
async def get_negotiation_room(room_id: str):
    """Get negotiation room details"""
    session = get_negotiation_session(room_id)
    if not session:
        raise HTTPException(status_code=404, detail="Room not found")

    return {
        "room_id": room_id,
        "topic": session.topic,
        "your_position": session.your_position,
        "negotiation_score": session.negotiation_score,
        "transcript_length": len(session.transcript),
        "cards_generated": len(session.counter_cards)
    }


@app.get("/api/negotiation/{room_id}/transcript")
async def get_negotiation_transcript(room_id: str):
    """Get full transcript of the negotiation"""
    transcript = get_transcript(room_id)
    if not transcript:
        raise HTTPException(status_code=404, detail="Room not found")
    return {"transcript": transcript}


@app.get("/api/negotiation/{room_id}/summary")
async def get_negotiation_summary_endpoint(room_id: str):
    """Get summary of the negotiation session"""
    summary = get_session_summary(room_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Room not found")
    return summary


@app.websocket("/api/negotiation/ws/{room_id}")
async def negotiation_websocket(websocket: WebSocket, room_id: str):
    """
    WebSocket endpoint for real-time negotiation AI assistance.

    Client sends: {"type": "transcript", "speaker": "them", "text": "..."}
    Client sends: {"type": "audio", "data": "<base64 audio>"}  (for Whisper transcription)
    Server sends: {"type": "counter_card", "card": {...}, "negotiation_score": 75}
    """
    await websocket.accept()

    # Track connection
    if room_id not in active_connections:
        active_connections[room_id] = []
    active_connections[room_id].append(websocket)

    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "room_id": room_id,
            "message": "AI negotiation assistant ready. I'll analyze their statements and suggest counters."
        })

        while True:
            # Receive message from client (can be text or binary)
            message = await websocket.receive()

            if "text" in message:
                data = json.loads(message["text"])

                if data.get("type") == "transcript":
                    speaker = data.get("speaker", "them")
                    text = data.get("text", "")

                    if text.strip():
                        # Analyze the statement and get counter-arguments
                        result = await analyze_statement(
                            room_id=room_id,
                            statement=text,
                            speaker=speaker
                        )

                        if result:
                            # Send counter card to ALL clients in the room
                            for ws in active_connections.get(room_id, []):
                                try:
                                    await ws.send_json({
                                        "type": "counter_card",
                                        "card": result["card"],
                                        "negotiation_score": result["negotiation_score"]
                                    })
                                except:
                                    pass
                        else:
                            # Acknowledge receipt even if no card generated
                            await websocket.send_json({
                                "type": "transcript_received",
                                "speaker": speaker,
                                "text": text[:50] + "..." if len(text) > 50 else text
                            })

                elif data.get("type") == "audio":
                    # Handle base64 encoded audio for Whisper transcription
                    import base64
                    audio_b64 = data.get("data", "")
                    if audio_b64:
                        try:
                            audio_bytes = base64.b64decode(audio_b64)
                            # Transcribe using Whisper
                            transcript = await transcribe_audio(audio_bytes)
                            if transcript.strip():
                                # Analyze the transcription
                                result = await analyze_statement(
                                    room_id=room_id,
                                    statement=transcript,
                                    speaker="them"
                                )
                                if result:
                                    # Send to all clients
                                    for ws in active_connections.get(room_id, []):
                                        try:
                                            await ws.send_json({
                                                "type": "counter_card",
                                                "card": result["card"],
                                                "negotiation_score": result["negotiation_score"]
                                            })
                                        except:
                                            pass
                        except Exception as e:
                            print(f"Audio transcription error: {e}")

                elif data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})

            elif "bytes" in message:
                # Handle raw binary audio
                audio_bytes = message["bytes"]
                if audio_bytes:
                    transcript = await transcribe_audio(audio_bytes)
                    if transcript.strip():
                        result = await analyze_statement(
                            room_id=room_id,
                            statement=transcript,
                            speaker="them"
                        )
                        if result:
                            for ws in active_connections.get(room_id, []):
                                try:
                                    await ws.send_json({
                                        "type": "counter_card",
                                        "card": result["card"],
                                        "negotiation_score": result["negotiation_score"]
                                    })
                                except:
                                    pass

    except WebSocketDisconnect:
        # Clean up connection
        if room_id in active_connections:
            active_connections[room_id].remove(websocket)
            if not active_connections[room_id]:
                del active_connections[room_id]
    except Exception as e:
        print(f"WebSocket error: {e}")
        if room_id in active_connections and websocket in active_connections[room_id]:
            active_connections[room_id].remove(websocket)


@app.post("/api/negotiation/{room_id}/analyze")
async def analyze_statement_http(room_id: str, message: TranscriptMessage):
    """
    HTTP endpoint to analyze a statement (alternative to WebSocket).
    Useful for testing or when WebSocket isn't available.
    """
    result = await analyze_statement(
        room_id=room_id,
        statement=message.text,
        speaker=message.speaker
    )

    if result:
        return result
    return {"message": "Statement recorded", "card_generated": False}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
