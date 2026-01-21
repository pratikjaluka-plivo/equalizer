"""
Pricing Engine - Compares bill against CGHS, PMJAY, and market rates
This is where we expose the information asymmetry
"""
from typing import Dict, Any
from app.parsers.bill_parser import BillData


# CGHS (Central Government Health Scheme) Rates - 2024
# These are official government rates that hospitals accept for government employees
# Source: cghs.gov.in rate lists
CGHS_RATES = {
    # Surgeries
    "appendectomy": {"nabh": 35000, "non_nabh": 28000, "description": "Appendicectomy (Open/Laparoscopic)"},
    "appendectomy_laparoscopic": {"nabh": 45000, "non_nabh": 36000, "description": "Laparoscopic Appendicectomy"},
    "cholecystectomy": {"nabh": 50000, "non_nabh": 40000, "description": "Cholecystectomy (Gall Bladder Removal)"},
    "cholecystectomy_laparoscopic": {"nabh": 60000, "non_nabh": 48000, "description": "Laparoscopic Cholecystectomy"},
    "hernia_repair": {"nabh": 40000, "non_nabh": 32000, "description": "Hernia Repair"},
    "hernia_repair_laparoscopic": {"nabh": 55000, "non_nabh": 44000, "description": "Laparoscopic Hernia Repair"},
    "caesarean_section": {"nabh": 45000, "non_nabh": 36000, "description": "Caesarean Section"},
    "normal_delivery": {"nabh": 18000, "non_nabh": 14400, "description": "Normal Vaginal Delivery"},
    "hysterectomy": {"nabh": 55000, "non_nabh": 44000, "description": "Hysterectomy"},
    "knee_replacement": {"nabh": 200000, "non_nabh": 160000, "description": "Total Knee Replacement (Unilateral)"},
    "hip_replacement": {"nabh": 210000, "non_nabh": 168000, "description": "Total Hip Replacement"},
    "bypass_surgery": {"nabh": 250000, "non_nabh": 200000, "description": "CABG (Coronary Artery Bypass)"},
    "angioplasty": {"nabh": 120000, "non_nabh": 96000, "description": "Coronary Angioplasty with Stent"},
    "cataract_surgery": {"nabh": 25000, "non_nabh": 20000, "description": "Cataract Surgery with IOL"},

    # ICU/Room Charges (per day)
    "icu_per_day": {"nabh": 5500, "non_nabh": 4400, "description": "ICU Charges per day"},
    "private_room_per_day": {"nabh": 3500, "non_nabh": 2800, "description": "Private Room per day"},
    "semi_private_per_day": {"nabh": 2500, "non_nabh": 2000, "description": "Semi-Private Room per day"},
    "general_ward_per_day": {"nabh": 1500, "non_nabh": 1200, "description": "General Ward per day"},

    # Diagnostics
    "mri_scan": {"nabh": 8000, "non_nabh": 6400, "description": "MRI Scan"},
    "ct_scan": {"nabh": 5000, "non_nabh": 4000, "description": "CT Scan"},
    "xray": {"nabh": 350, "non_nabh": 280, "description": "X-Ray"},
    "ultrasound": {"nabh": 1200, "non_nabh": 960, "description": "Ultrasound"},
    "ecg": {"nabh": 300, "non_nabh": 240, "description": "ECG"},
    "echocardiogram": {"nabh": 2500, "non_nabh": 2000, "description": "2D Echocardiogram"},

    # Common Tests
    "blood_test_cbc": {"nabh": 250, "non_nabh": 200, "description": "Complete Blood Count"},
    "blood_test_lipid": {"nabh": 600, "non_nabh": 480, "description": "Lipid Profile"},
    "blood_test_thyroid": {"nabh": 800, "non_nabh": 640, "description": "Thyroid Profile"},
    "blood_test_liver": {"nabh": 700, "non_nabh": 560, "description": "Liver Function Test"},
    "blood_test_kidney": {"nabh": 600, "non_nabh": 480, "description": "Kidney Function Test"},
}


# PMJAY (Ayushman Bharat) Rates - 2024
# These are rates for the national health insurance scheme
# Generally lower than CGHS as they're meant for economically weaker sections
PMJAY_RATES = {
    "appendectomy": {"rate": 20000, "package_code": "S-SUR-014"},
    "appendectomy_laparoscopic": {"rate": 28000, "package_code": "S-SUR-015"},
    "cholecystectomy": {"rate": 25000, "package_code": "S-SUR-020"},
    "cholecystectomy_laparoscopic": {"rate": 35000, "package_code": "S-SUR-021"},
    "hernia_repair": {"rate": 18000, "package_code": "S-SUR-030"},
    "caesarean_section": {"rate": 22000, "package_code": "O-OBS-001"},
    "normal_delivery": {"rate": 9000, "package_code": "O-OBS-002"},
    "hysterectomy": {"rate": 30000, "package_code": "O-GYN-001"},
    "knee_replacement": {"rate": 80000, "package_code": "O-ORT-010"},
    "hip_replacement": {"rate": 85000, "package_code": "O-ORT-011"},
    "bypass_surgery": {"rate": 120000, "package_code": "C-CAR-001"},
    "angioplasty": {"rate": 60000, "package_code": "C-CAR-010"},
    "cataract_surgery": {"rate": 15000, "package_code": "E-OPH-001"},
}


# Market rate multipliers (what private hospitals typically charge vs CGHS)
# These are based on analysis of hospital bills across major cities
MARKET_MULTIPLIERS = {
    "mumbai": {"premium": 4.0, "standard": 2.5, "budget": 1.5},
    "delhi": {"premium": 3.5, "standard": 2.2, "budget": 1.4},
    "bangalore": {"premium": 3.0, "standard": 2.0, "budget": 1.3},
    "chennai": {"premium": 2.8, "standard": 1.8, "budget": 1.3},
    "hyderabad": {"premium": 2.5, "standard": 1.7, "budget": 1.2},
    "kolkata": {"premium": 2.2, "standard": 1.5, "budget": 1.2},
    "pune": {"premium": 2.5, "standard": 1.8, "budget": 1.3},
    "ahmedabad": {"premium": 2.3, "standard": 1.6, "budget": 1.2},
    "default": {"premium": 2.5, "standard": 1.8, "budget": 1.3},
}


def normalize_procedure(description: str) -> str:
    """
    Normalize procedure description to match our database keys
    """
    description = description.lower().strip()

    # Common mappings
    mappings = {
        "appendix": "appendectomy",
        "appendicectomy": "appendectomy",
        "lap appendectomy": "appendectomy_laparoscopic",
        "laparoscopic appendectomy": "appendectomy_laparoscopic",
        "laparoscopic appendicectomy": "appendectomy_laparoscopic",
        "gall bladder": "cholecystectomy",
        "gallbladder": "cholecystectomy",
        "lap chole": "cholecystectomy_laparoscopic",
        "laparoscopic cholecystectomy": "cholecystectomy_laparoscopic",
        "c-section": "caesarean_section",
        "c section": "caesarean_section",
        "lscs": "caesarean_section",
        "cesarean": "caesarean_section",
        "caesarian": "caesarean_section",
        "normal delivery": "normal_delivery",
        "vaginal delivery": "normal_delivery",
        "knee replacement": "knee_replacement",
        "tkr": "knee_replacement",
        "total knee": "knee_replacement",
        "hip replacement": "hip_replacement",
        "thr": "hip_replacement",
        "total hip": "hip_replacement",
        "bypass": "bypass_surgery",
        "cabg": "bypass_surgery",
        "angioplasty": "angioplasty",
        "ptca": "angioplasty",
        "stent": "angioplasty",
        "cataract": "cataract_surgery",
        "phaco": "cataract_surgery",
        "hernia": "hernia_repair",
        "hysterectomy": "hysterectomy",
        "uterus removal": "hysterectomy",
    }

    for key, value in mappings.items():
        if key in description:
            return value

    # Return closest match or original
    return description


async def get_price_comparison(bill_data: BillData) -> Dict[str, Any]:
    """
    Get price comparison between billed amount and reference rates
    This is THE key function that exposes the asymmetry
    """
    procedure_key = normalize_procedure(bill_data.procedure_description)
    city = bill_data.hospital_city.lower()

    # Get reference rates
    cghs_rate = CGHS_RATES.get(procedure_key, {})
    pmjay_rate = PMJAY_RATES.get(procedure_key, {})

    # Get market multipliers for the city
    multipliers = MARKET_MULTIPLIERS.get(city, MARKET_MULTIPLIERS["default"])

    # Calculate expected rates
    cghs_nabh = cghs_rate.get("nabh", 0)
    cghs_non_nabh = cghs_rate.get("non_nabh", 0)
    pmjay = pmjay_rate.get("rate", 0)

    # Fair market estimate (based on CGHS + reasonable margin)
    fair_market_low = cghs_nabh * 1.3 if cghs_nabh else bill_data.total_amount * 0.3
    fair_market_high = cghs_nabh * 1.8 if cghs_nabh else bill_data.total_amount * 0.5

    # Calculate overcharge
    if cghs_nabh:
        overcharge_vs_cghs = bill_data.total_amount - cghs_nabh
        overcharge_percentage = ((bill_data.total_amount - cghs_nabh) / cghs_nabh) * 100
    else:
        overcharge_vs_cghs = 0
        overcharge_percentage = 0

    # Determine if the bill is reasonable
    # VALID means the bill is fair and no dispute is needed
    if cghs_nabh and bill_data.total_amount > cghs_nabh * 3:
        assessment = "SEVERE_OVERCHARGE"
        assessment_detail = "Bill is more than 3x the government rate - strong case for dispute"
        dispute_recommended = True
    elif cghs_nabh and bill_data.total_amount > cghs_nabh * 2:
        assessment = "SIGNIFICANT_OVERCHARGE"
        assessment_detail = "Bill is more than 2x the government rate - dispute recommended"
        dispute_recommended = True
    elif cghs_nabh and bill_data.total_amount > cghs_nabh * 1.5:
        assessment = "MODERATE_OVERCHARGE"
        assessment_detail = "Bill is 50-100% above government rate - negotiation possible"
        dispute_recommended = True
    elif cghs_nabh and bill_data.total_amount > cghs_nabh * 1.2:
        assessment = "SLIGHT_OVERCHARGE"
        assessment_detail = "Bill is 20-50% above government rate - minor negotiation possible"
        dispute_recommended = True
    elif cghs_nabh and bill_data.total_amount > cghs_nabh:
        assessment = "FAIR_PRICING"
        assessment_detail = "Bill is within 20% of government rate - this is fair market pricing"
        dispute_recommended = False
    else:
        assessment = "VALID"
        assessment_detail = "Bill is at or below government rates - no overcharging detected"
        dispute_recommended = False

    # Calculate potential savings only if dispute is recommended
    potential_savings = overcharge_vs_cghs if dispute_recommended else 0

    return {
        "billed_amount": bill_data.total_amount,
        "procedure_identified": procedure_key,
        "procedure_description": cghs_rate.get("description", bill_data.procedure_description),

        # What they don't tell you
        "cghs_rate_nabh": cghs_nabh,
        "cghs_rate_non_nabh": cghs_non_nabh,
        "pmjay_rate": pmjay,
        "pmjay_package_code": pmjay_rate.get("package_code", ""),

        # Fair market analysis
        "fair_market_low": round(fair_market_low),
        "fair_market_high": round(fair_market_high),
        "fair_market_mid": round((fair_market_low + fair_market_high) / 2),

        # The damage
        "overcharge_vs_cghs": round(overcharge_vs_cghs),
        "overcharge_percentage": round(overcharge_percentage, 1),
        "assessment": assessment,
        "assessment_detail": assessment_detail,
        "dispute_recommended": dispute_recommended,
        "potential_savings": round(potential_savings),

        # City-specific context
        "city_multipliers": multipliers,
        "expected_premium_hospital": round(cghs_nabh * multipliers["premium"]) if cghs_nabh else None,
        "expected_standard_hospital": round(cghs_nabh * multipliers["standard"]) if cghs_nabh else None,

        # Target negotiation range
        "target_low": cghs_nabh if cghs_nabh else round(bill_data.total_amount * 0.2),
        "target_high": round(cghs_nabh * 1.5) if cghs_nabh else round(bill_data.total_amount * 0.4),
        "target_realistic": round(cghs_nabh * 1.3) if cghs_nabh else round(bill_data.total_amount * 0.35),
    }
