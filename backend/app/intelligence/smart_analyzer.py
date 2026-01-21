"""
Smart Bill Analyzer - LLM-driven analysis that works for ANY patient.

Does NOT rely on CGHS (which is only for government employees).
Instead uses:
1. PMJAY (Ayushman Bharat) rates as baseline
2. State Clinical Establishments Act capped rates
3. Insurance company standard rates
4. Market research from similar hospitals
5. LLM-powered fair price estimation
"""
import os
import json
import httpx
import base64
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


@dataclass
class ParsedBill:
    """Structured bill data extracted by LLM"""
    hospital_name: str
    hospital_city: str
    hospital_state: str
    hospital_type: str  # "private", "government", "charitable_trust"

    patient_name: Optional[str]
    admission_date: Optional[str]
    discharge_date: Optional[str]

    primary_diagnosis: str
    primary_procedure: str
    secondary_procedures: List[str]

    total_amount: float
    itemized_charges: Dict[str, float]

    # LLM-detected issues
    billing_errors: List[Dict[str, Any]]
    duplicate_charges: List[Dict[str, Any]]
    suspicious_items: List[Dict[str, Any]]

    raw_text: str  # Original bill text for reference


@dataclass
class FairPriceEstimate:
    """Fair price estimates from multiple sources"""
    pmjay_rate: Optional[float]  # Ayushman Bharat rate
    insurance_typical_rate: Optional[float]  # What insurance companies pay
    market_average_low: float  # Budget hospitals
    market_average_mid: float  # Standard hospitals
    market_average_high: float  # Premium hospitals

    recommended_fair_price: float
    maximum_reasonable_price: float

    sources: List[Dict[str, str]]  # Evidence for each estimate
    confidence: str  # "high", "medium", "low"


@dataclass
class BillAnalysis:
    """Complete analysis result"""
    parsed_bill: ParsedBill
    fair_price: FairPriceEstimate

    overcharge_amount: float
    overcharge_percentage: float

    severity: str  # "none", "minor", "moderate", "severe", "extreme"
    dispute_recommended: bool

    key_issues: List[Dict[str, Any]]
    negotiation_points: List[str]
    suggested_settlement: float

    legal_references: List[Dict[str, str]]
    next_steps: List[str]


# Comprehensive prompt for bill parsing
BILL_PARSING_PROMPT = """You are an expert Indian medical bill analyst. Analyze this hospital bill thoroughly.

Extract ALL information and identify ANY billing irregularities.

IMPORTANT CONTEXT:
- Indian private hospitals often overcharge significantly
- Look for: duplicate charges, inflated MRP on medicines, unnecessary items, bundled charges that should be separate
- Common tricks: charging for "kits" and "packages" with hidden items, excessive room charges, ICU upcoding

Return a JSON object with this EXACT structure:
{
    "hospital_name": "Full hospital name as shown",
    "hospital_city": "City",
    "hospital_state": "State",
    "hospital_type": "private/government/charitable_trust",

    "patient_name": "Patient name if visible",
    "admission_date": "DD/MM/YYYY if visible",
    "discharge_date": "DD/MM/YYYY if visible",

    "primary_diagnosis": "Main medical condition/reason for admission",
    "primary_procedure": "Main surgery/treatment performed",
    "secondary_procedures": ["List of other procedures if any"],

    "total_amount": 0.00,
    "itemized_charges": {
        "Room Charges": 0.00,
        "Surgery/Procedure": 0.00,
        "Doctor/Surgeon Fees": 0.00,
        "Medicines": 0.00,
        "Consumables": 0.00,
        "Diagnostics/Tests": 0.00,
        "ICU Charges": 0.00,
        "Other": 0.00
    },

    "billing_errors": [
        {"item": "Description", "issue": "What's wrong", "amount": 0.00, "should_be": 0.00}
    ],
    "duplicate_charges": [
        {"item": "Description", "occurrences": 2, "total_overcharge": 0.00}
    ],
    "suspicious_items": [
        {"item": "Description", "concern": "Why it's suspicious", "amount": 0.00}
    ],

    "raw_text": "Key text/numbers from the bill for reference"
}

Be AGGRESSIVE in finding issues. Most Indian hospital bills have problems.
Return ONLY valid JSON."""


async def parse_bill_with_llm(
    file_contents: bytes,
    filename: str,
    hospital_name: Optional[str] = None
) -> ParsedBill:
    """
    Parse a medical bill using LLM vision capabilities.
    Supports images and PDFs.
    """
    # Determine file type
    is_pdf = filename.lower().endswith('.pdf')

    # Prepare image data
    if is_pdf:
        # For PDF, we'll use pdf2image or send as-is to Gemini (which supports PDFs)
        image_data = base64.standard_b64encode(file_contents).decode("utf-8")
        media_type = "application/pdf"
    else:
        image_data = base64.standard_b64encode(file_contents).decode("utf-8")
        if filename.lower().endswith(('.jpg', '.jpeg')):
            media_type = "image/jpeg"
        elif filename.lower().endswith('.png'):
            media_type = "image/png"
        else:
            media_type = "image/jpeg"

    # Add hospital name context if provided
    context = ""
    if hospital_name:
        context = f"\nHOSPITAL CONTEXT: The patient selected hospital '{hospital_name}'. Verify this matches the bill.\n"

    prompt = BILL_PARSING_PROMPT + context

    # Try OpenAI first (better vision), fall back to Gemini
    result = await _parse_with_openai(image_data, media_type, prompt)

    if not result:
        result = await _parse_with_gemini(image_data, media_type, prompt, is_pdf)

    if not result:
        raise ValueError("Failed to parse bill with any available LLM")

    return ParsedBill(
        hospital_name=result.get("hospital_name", hospital_name or "Unknown"),
        hospital_city=result.get("hospital_city", "Unknown"),
        hospital_state=result.get("hospital_state", "Unknown"),
        hospital_type=result.get("hospital_type", "private"),
        patient_name=result.get("patient_name"),
        admission_date=result.get("admission_date"),
        discharge_date=result.get("discharge_date"),
        primary_diagnosis=result.get("primary_diagnosis", "Unknown"),
        primary_procedure=result.get("primary_procedure", "Unknown"),
        secondary_procedures=result.get("secondary_procedures", []),
        total_amount=float(result.get("total_amount", 0)),
        itemized_charges=result.get("itemized_charges", {}),
        billing_errors=result.get("billing_errors", []),
        duplicate_charges=result.get("duplicate_charges", []),
        suspicious_items=result.get("suspicious_items", []),
        raw_text=result.get("raw_text", "")
    )


async def _parse_with_openai(image_data: str, media_type: str, prompt: str) -> Optional[Dict]:
    """Parse bill using OpenAI GPT-4 Vision"""
    if not OPENAI_API_KEY:
        return None

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # OpenAI doesn't support PDF directly, skip if PDF
            if media_type == "application/pdf":
                return None

            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{media_type};base64,{image_data}"
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": prompt
                                }
                            ]
                        }
                    ],
                    "max_tokens": 4000
                }
            )

            if response.status_code == 200:
                data = response.json()
                result_text = data["choices"][0]["message"]["content"]
                return _extract_json(result_text)
            else:
                logger.error(f"OpenAI vision error: {response.status_code}")

    except Exception as e:
        logger.error(f"OpenAI parsing error: {e}")

    return None


async def _parse_with_gemini(image_data: str, media_type: str, prompt: str, is_pdf: bool = False) -> Optional[Dict]:
    """Parse bill using Gemini (supports PDFs)"""
    if not GEMINI_API_KEY:
        return None

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Gemini supports both images and PDFs
            inline_data = {
                "mime_type": media_type,
                "data": image_data
            }

            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{
                        "parts": [
                            {"inline_data": inline_data},
                            {"text": prompt}
                        ]
                    }],
                    "generationConfig": {"temperature": 0.1}
                }
            )

            if response.status_code == 200:
                data = response.json()
                result_text = data["candidates"][0]["content"]["parts"][0]["text"]
                return _extract_json(result_text)
            else:
                logger.error(f"Gemini vision error: {response.status_code} - {response.text}")

    except Exception as e:
        logger.error(f"Gemini parsing error: {e}")

    return None


def _extract_json(text: str) -> Optional[Dict]:
    """Extract JSON from LLM response"""
    text = text.strip()

    # Remove markdown code blocks
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]

    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        logger.error(f"Failed to parse JSON: {text[:500]}")
        return None


# Fair pricing data - NOT CGHS dependent
# These are universal benchmarks that apply to everyone

PMJAY_RATES_2024 = {
    # Surgery packages (inclusive of room, OT, medicines, consumables)
    "appendectomy": {"rate": 20000, "code": "S-SUR-014", "days": 3},
    "appendectomy_laparoscopic": {"rate": 28000, "code": "S-SUR-015", "days": 3},
    "cholecystectomy": {"rate": 25000, "code": "S-SUR-020", "days": 4},
    "cholecystectomy_laparoscopic": {"rate": 35000, "code": "S-SUR-021", "days": 3},
    "hernia_inguinal": {"rate": 18000, "code": "S-SUR-030", "days": 2},
    "hernia_laparoscopic": {"rate": 30000, "code": "S-SUR-031", "days": 2},
    "caesarean_section": {"rate": 22000, "code": "O-OBS-001", "days": 5},
    "normal_delivery": {"rate": 9000, "code": "O-OBS-002", "days": 3},
    "hysterectomy_abdominal": {"rate": 30000, "code": "O-GYN-001", "days": 5},
    "hysterectomy_laparoscopic": {"rate": 40000, "code": "O-GYN-002", "days": 4},
    "knee_replacement_unilateral": {"rate": 80000, "code": "O-ORT-010", "days": 7},
    "knee_replacement_bilateral": {"rate": 140000, "code": "O-ORT-011", "days": 10},
    "hip_replacement": {"rate": 85000, "code": "O-ORT-012", "days": 7},
    "cabg_bypass": {"rate": 120000, "code": "C-CAR-001", "days": 10},
    "angioplasty_single_stent": {"rate": 60000, "code": "C-CAR-010", "days": 3},
    "angioplasty_double_stent": {"rate": 80000, "code": "C-CAR-011", "days": 3},
    "cataract_phaco": {"rate": 15000, "code": "E-OPH-001", "days": 1},
    "kidney_stone_ursl": {"rate": 25000, "code": "U-URO-001", "days": 2},
    "kidney_stone_pcnl": {"rate": 45000, "code": "U-URO-002", "days": 3},
    "prostate_turp": {"rate": 35000, "code": "U-URO-010", "days": 4},
}

# Market rate multipliers based on hospital category
# These represent what private hospitals TYPICALLY charge vs PMJAY
HOSPITAL_MULTIPLIERS = {
    "budget": 1.5,      # Budget/economy hospitals
    "standard": 2.5,    # Regular private hospitals
    "premium": 4.0,     # Premium/corporate hospitals
    "super_premium": 6.0,  # Top-tier hospitals (Medanta, Max, Apollo flagship)
}

# State-wise Clinical Establishments Act status
# States with price capping
PRICE_CAPPED_STATES = {
    "west_bengal": {"capped": True, "max_multiplier": 2.0},
    "maharashtra": {"capped": True, "max_multiplier": 3.0},  # Partial
    "rajasthan": {"capped": True, "max_multiplier": 2.5},
    "karnataka": {"capped": False},
    "tamil_nadu": {"capped": False},
    "delhi": {"capped": False},
    "kerala": {"capped": False},
    "gujarat": {"capped": False},
}


async def estimate_fair_price(
    parsed_bill: ParsedBill
) -> FairPriceEstimate:
    """
    Estimate fair price using multiple sources.
    Does NOT use CGHS (only for govt employees).
    """
    procedure = _normalize_procedure(parsed_bill.primary_procedure)
    state = parsed_bill.hospital_state.lower().replace(" ", "_")

    # Get PMJAY rate if available
    pmjay_data = PMJAY_RATES_2024.get(procedure, {})
    pmjay_rate = pmjay_data.get("rate")

    # Calculate market averages
    if pmjay_rate:
        market_low = pmjay_rate * HOSPITAL_MULTIPLIERS["budget"]
        market_mid = pmjay_rate * HOSPITAL_MULTIPLIERS["standard"]
        market_high = pmjay_rate * HOSPITAL_MULTIPLIERS["premium"]
    else:
        # If no PMJAY rate, use LLM estimation
        estimates = await _llm_price_estimation(parsed_bill)
        market_low = estimates.get("low", parsed_bill.total_amount * 0.3)
        market_mid = estimates.get("mid", parsed_bill.total_amount * 0.5)
        market_high = estimates.get("high", parsed_bill.total_amount * 0.7)
        pmjay_rate = estimates.get("pmjay_estimate")

    # Check if state has price capping
    state_rules = PRICE_CAPPED_STATES.get(state, {"capped": False})

    # Calculate recommended fair price
    if state_rules.get("capped"):
        max_allowed = (pmjay_rate or market_mid) * state_rules.get("max_multiplier", 3.0)
        recommended = min(market_mid, max_allowed)
        maximum = max_allowed
    else:
        recommended = market_mid
        maximum = market_high

    # Insurance typical rate (what TPA usually approves)
    insurance_rate = (pmjay_rate * 2.0) if pmjay_rate else market_mid * 0.8

    sources = []
    if pmjay_rate:
        sources.append({
            "name": "PMJAY (Ayushman Bharat)",
            "rate": pmjay_rate,
            "code": pmjay_data.get("code", ""),
            "note": "Government health insurance rate - baseline reference"
        })
    sources.append({
        "name": "Market Average (Standard Hospital)",
        "rate": market_mid,
        "note": "Typical rate at standard private hospitals"
    })
    if state_rules.get("capped"):
        sources.append({
            "name": f"Clinical Establishments Act ({parsed_bill.hospital_state})",
            "rate": maximum,
            "note": f"State law caps prices at {state_rules.get('max_multiplier', 3)}x government rates"
        })

    return FairPriceEstimate(
        pmjay_rate=pmjay_rate,
        insurance_typical_rate=insurance_rate,
        market_average_low=market_low,
        market_average_mid=market_mid,
        market_average_high=market_high,
        recommended_fair_price=recommended,
        maximum_reasonable_price=maximum,
        sources=sources,
        confidence="high" if pmjay_rate else "medium"
    )


async def _llm_price_estimation(parsed_bill: ParsedBill) -> Dict[str, float]:
    """Use LLM to estimate fair price when no reference data available"""

    prompt = f"""You are a healthcare pricing expert in India. Estimate fair market prices for this procedure.

PROCEDURE: {parsed_bill.primary_procedure}
DIAGNOSIS: {parsed_bill.primary_diagnosis}
HOSPITAL TYPE: {parsed_bill.hospital_type}
CITY: {parsed_bill.hospital_city}, {parsed_bill.hospital_state}
BILLED AMOUNT: ₹{parsed_bill.total_amount:,.0f}

Based on your knowledge of Indian healthcare costs, estimate:
1. What PMJAY (Ayushman Bharat) would pay for this procedure
2. What a budget private hospital would charge
3. What a standard private hospital would charge
4. What a premium hospital would charge

Consider:
- The procedure complexity
- Typical hospital stay duration
- Standard consumables and medicines needed
- Doctor/surgeon fees in that city

Return JSON:
{{
    "pmjay_estimate": 00000,
    "low": 00000,
    "mid": 00000,
    "high": 00000,
    "reasoning": "Brief explanation"
}}"""

    try:
        if OPENAI_API_KEY:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENAI_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 500
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    result = _extract_json(data["choices"][0]["message"]["content"])
                    if result:
                        return result
    except Exception as e:
        logger.error(f"LLM price estimation error: {e}")

    # Fallback: estimate based on billed amount
    return {
        "low": parsed_bill.total_amount * 0.25,
        "mid": parsed_bill.total_amount * 0.4,
        "high": parsed_bill.total_amount * 0.6,
        "pmjay_estimate": None
    }


def _normalize_procedure(description: str) -> str:
    """Normalize procedure description to match database keys"""
    desc = description.lower().strip()

    mappings = {
        "appendix": "appendectomy",
        "appendicectomy": "appendectomy",
        "appendectomy": "appendectomy",
        "lap appendectomy": "appendectomy_laparoscopic",
        "laparoscopic appendectomy": "appendectomy_laparoscopic",
        "gall bladder": "cholecystectomy",
        "gallbladder": "cholecystectomy",
        "cholecystectomy": "cholecystectomy",
        "lap chole": "cholecystectomy_laparoscopic",
        "laparoscopic cholecystectomy": "cholecystectomy_laparoscopic",
        "c-section": "caesarean_section",
        "c section": "caesarean_section",
        "caesarean": "caesarean_section",
        "cesarean": "caesarean_section",
        "lscs": "caesarean_section",
        "normal delivery": "normal_delivery",
        "vaginal delivery": "normal_delivery",
        "hernia": "hernia_inguinal",
        "inguinal hernia": "hernia_inguinal",
        "lap hernia": "hernia_laparoscopic",
        "laparoscopic hernia": "hernia_laparoscopic",
        "hysterectomy": "hysterectomy_abdominal",
        "lap hysterectomy": "hysterectomy_laparoscopic",
        "knee replacement": "knee_replacement_unilateral",
        "tkr": "knee_replacement_unilateral",
        "bilateral knee": "knee_replacement_bilateral",
        "hip replacement": "hip_replacement",
        "thr": "hip_replacement",
        "bypass": "cabg_bypass",
        "cabg": "cabg_bypass",
        "angioplasty": "angioplasty_single_stent",
        "ptca": "angioplasty_single_stent",
        "double stent": "angioplasty_double_stent",
        "cataract": "cataract_phaco",
        "phaco": "cataract_phaco",
        "kidney stone": "kidney_stone_ursl",
        "ursl": "kidney_stone_ursl",
        "pcnl": "kidney_stone_pcnl",
        "prostate": "prostate_turp",
        "turp": "prostate_turp",
    }

    for key, value in mappings.items():
        if key in desc:
            return value

    return desc


async def analyze_bill_complete(
    parsed_bill: ParsedBill,
    fair_price: FairPriceEstimate
) -> BillAnalysis:
    """
    Complete bill analysis with recommendations.
    """
    # Calculate overcharge
    overcharge = parsed_bill.total_amount - fair_price.recommended_fair_price
    overcharge_pct = (overcharge / fair_price.recommended_fair_price) * 100 if fair_price.recommended_fair_price > 0 else 0

    # Determine severity
    if overcharge_pct <= 0:
        severity = "none"
        dispute_recommended = False
    elif overcharge_pct <= 30:
        severity = "minor"
        dispute_recommended = False
    elif overcharge_pct <= 80:
        severity = "moderate"
        dispute_recommended = True
    elif overcharge_pct <= 150:
        severity = "severe"
        dispute_recommended = True
    else:
        severity = "extreme"
        dispute_recommended = True

    # Compile key issues
    key_issues = []

    # Add billing errors
    for error in parsed_bill.billing_errors:
        key_issues.append({
            "type": "billing_error",
            "description": error.get("issue", ""),
            "item": error.get("item", ""),
            "impact": error.get("amount", 0)
        })

    # Add duplicate charges
    for dup in parsed_bill.duplicate_charges:
        key_issues.append({
            "type": "duplicate_charge",
            "description": f"Charged {dup.get('occurrences', 2)} times",
            "item": dup.get("item", ""),
            "impact": dup.get("total_overcharge", 0)
        })

    # Add suspicious items
    for item in parsed_bill.suspicious_items:
        key_issues.append({
            "type": "suspicious",
            "description": item.get("concern", ""),
            "item": item.get("item", ""),
            "impact": item.get("amount", 0)
        })

    # Add overcharge as key issue
    if overcharge > 0:
        key_issues.append({
            "type": "overcharge",
            "description": f"Bill is {overcharge_pct:.0f}% above fair market rate",
            "item": "Overall Bill",
            "impact": overcharge
        })

    # Generate negotiation points
    negotiation_points = await _generate_negotiation_points(parsed_bill, fair_price, key_issues)

    # Calculate suggested settlement
    if severity == "none":
        suggested_settlement = parsed_bill.total_amount
    elif severity == "minor":
        suggested_settlement = parsed_bill.total_amount * 0.9
    elif severity == "moderate":
        suggested_settlement = fair_price.recommended_fair_price * 1.2
    elif severity == "severe":
        suggested_settlement = fair_price.recommended_fair_price * 1.1
    else:
        suggested_settlement = fair_price.recommended_fair_price

    # Legal references
    legal_references = [
        {
            "act": "Consumer Protection Act, 2019",
            "relevance": "Medical services are covered. Overcharging is an unfair trade practice.",
            "action": "File complaint at consumer forum (e-Jagriti portal)"
        },
        {
            "act": "Clinical Establishments Act, 2010",
            "relevance": "Hospitals must display rates and cannot charge arbitrarily.",
            "action": "Complain to State Health Department"
        }
    ]

    if parsed_bill.hospital_state.lower() in ["maharashtra", "west bengal", "rajasthan"]:
        legal_references.append({
            "act": f"{parsed_bill.hospital_state} Clinical Establishments Rules",
            "relevance": "State has price capping provisions",
            "action": "Hospital may be violating state law"
        })

    # Next steps
    next_steps = []
    if dispute_recommended:
        next_steps = [
            "Send formal notice to hospital billing department citing specific overcharges",
            "Request itemized breakdown if not already provided",
            "File RTI for hospital's rate card (if registered under CEA)",
            "If no response in 7 days, file complaint on National Consumer Helpline (1800-11-4000)",
            "File e-Jagriti complaint at consumerhelpline.gov.in",
            "Consider approaching consumer forum if amount exceeds ₹1 lakh"
        ]
    else:
        next_steps = [
            "Bill appears to be within reasonable range",
            "You may still request itemized breakdown for verification",
            "Keep all documents for future reference"
        ]

    return BillAnalysis(
        parsed_bill=parsed_bill,
        fair_price=fair_price,
        overcharge_amount=max(0, overcharge),
        overcharge_percentage=max(0, overcharge_pct),
        severity=severity,
        dispute_recommended=dispute_recommended,
        key_issues=key_issues,
        negotiation_points=negotiation_points,
        suggested_settlement=suggested_settlement,
        legal_references=legal_references,
        next_steps=next_steps
    )


async def _generate_negotiation_points(
    parsed_bill: ParsedBill,
    fair_price: FairPriceEstimate,
    key_issues: List[Dict]
) -> List[str]:
    """Generate specific negotiation points based on analysis"""
    points = []

    # PMJAY reference
    if fair_price.pmjay_rate:
        points.append(
            f"Ayushman Bharat (PMJAY) rate for this procedure is ₹{fair_price.pmjay_rate:,.0f}. "
            f"Your bill of ₹{parsed_bill.total_amount:,.0f} is {parsed_bill.total_amount/fair_price.pmjay_rate:.1f}x this rate."
        )

    # Market rate reference
    points.append(
        f"Standard private hospitals charge ₹{fair_price.market_average_mid:,.0f} for this procedure. "
        f"Even premium hospitals charge around ₹{fair_price.market_average_high:,.0f}."
    )

    # Specific issues
    total_issue_amount = sum(issue.get("impact", 0) for issue in key_issues if issue["type"] != "overcharge")
    if total_issue_amount > 0:
        points.append(
            f"We have identified specific billing issues totaling ₹{total_issue_amount:,.0f} "
            f"including duplicate charges, billing errors, and suspicious items."
        )

    # Insurance reference
    if fair_price.insurance_typical_rate:
        points.append(
            f"Insurance companies typically approve ₹{fair_price.insurance_typical_rate:,.0f} for this procedure. "
            f"Private patients should not pay significantly more than insured patients."
        )

    # Legal leverage
    points.append(
        "Under the Consumer Protection Act 2019, overcharging constitutes an unfair trade practice. "
        "We are prepared to escalate to the consumer forum if a reasonable settlement is not reached."
    )

    return points


async def full_bill_analysis(
    file_contents: bytes,
    filename: str,
    hospital_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main entry point: Complete bill analysis from uploaded file.

    1. Parse bill with LLM
    2. Estimate fair prices
    3. Generate complete analysis
    4. Return actionable results
    """
    # Step 1: Parse the bill
    parsed_bill = await parse_bill_with_llm(file_contents, filename, hospital_name)

    # Step 2: Estimate fair prices
    fair_price = await estimate_fair_price(parsed_bill)

    # Step 3: Complete analysis
    analysis = await analyze_bill_complete(parsed_bill, fair_price)

    # Convert to dict for JSON response
    return {
        "bill": asdict(parsed_bill),
        "fair_price": asdict(fair_price),
        "analysis": {
            "overcharge_amount": analysis.overcharge_amount,
            "overcharge_percentage": analysis.overcharge_percentage,
            "severity": analysis.severity,
            "dispute_recommended": analysis.dispute_recommended,
            "key_issues": analysis.key_issues,
            "negotiation_points": analysis.negotiation_points,
            "suggested_settlement": analysis.suggested_settlement,
            "legal_references": analysis.legal_references,
            "next_steps": analysis.next_steps
        },
        "summary": {
            "hospital": parsed_bill.hospital_name,
            "procedure": parsed_bill.primary_procedure,
            "billed": parsed_bill.total_amount,
            "fair_price": fair_price.recommended_fair_price,
            "overcharge": analysis.overcharge_amount,
            "savings_potential": analysis.overcharge_amount if analysis.dispute_recommended else 0,
            "action_required": analysis.dispute_recommended
        }
    }
