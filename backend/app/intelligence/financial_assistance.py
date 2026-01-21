"""
Financial Assistance Module
===========================
Helps patients with valid bills find financial support through:
- NGOs and charitable organizations
- Government health schemes
- Insurance options
- Hospital payment plans
"""
from typing import Dict, Any, List, Optional


# NGO Database by City - Organizations that help with medical bill payments
NGO_DATABASE = {
    "mumbai": [
        {
            "name": "Tata Memorial Hospital Patient Welfare Fund",
            "description": "Financial assistance for cancer patients",
            "contact": "022-24177000",
            "website": "https://tmc.gov.in",
            "covers": ["cancer treatment", "chemotherapy", "surgery"],
            "eligibility": "Income below 3 lakh/year",
        },
        {
            "name": "Helpage India - Mumbai",
            "description": "Healthcare support for senior citizens",
            "contact": "1800-180-1253",
            "website": "https://www.helpageindia.org",
            "covers": ["elderly care", "chronic diseases", "surgeries"],
            "eligibility": "Age 60+ years",
        },
        {
            "name": "Indian Cancer Society",
            "description": "Financial aid for cancer treatment",
            "contact": "022-24178516",
            "website": "https://www.indiancancersociety.org",
            "covers": ["cancer treatment", "diagnostics"],
            "eligibility": "Cancer patients with financial need",
        },
        {
            "name": "Rotary Club Mumbai",
            "description": "Medical assistance programs",
            "contact": "022-26551234",
            "website": "https://www.rotarymumbai.org",
            "covers": ["surgeries", "medical emergencies"],
            "eligibility": "Case-by-case basis",
        },
    ],
    "delhi": [
        {
            "name": "AIIMS Patient Welfare Society",
            "description": "Support for underprivileged patients at AIIMS",
            "contact": "011-26588500",
            "website": "https://www.aiims.edu",
            "covers": ["all treatments at AIIMS"],
            "eligibility": "BPL card holders or income proof",
        },
        {
            "name": "CanSupport",
            "description": "Free home-based palliative care for cancer patients",
            "contact": "011-41010539",
            "website": "https://www.cansupport.org",
            "covers": ["cancer care", "palliative care", "counseling"],
            "eligibility": "Cancer patients in Delhi NCR",
        },
        {
            "name": "Uday Foundation",
            "description": "Medical and financial assistance",
            "contact": "011-43111916",
            "website": "https://www.udayfoundation.org",
            "covers": ["heart surgery", "organ transplants", "cancer"],
            "eligibility": "Underprivileged patients",
        },
        {
            "name": "Smile Foundation",
            "description": "Healthcare for underprivileged",
            "contact": "011-43123700",
            "website": "https://www.smilefoundationindia.org",
            "covers": ["cleft surgery", "child health", "general healthcare"],
            "eligibility": "Economically weaker sections",
        },
    ],
    "bangalore": [
        {
            "name": "Bangalore Kidney Foundation",
            "description": "Support for kidney patients",
            "contact": "080-22867890",
            "website": "https://www.bkfindia.org",
            "covers": ["dialysis", "kidney transplant"],
            "eligibility": "Kidney patients with financial need",
        },
        {
            "name": "Kidwai Memorial Institute Patient Fund",
            "description": "Cancer treatment assistance",
            "contact": "080-26094000",
            "website": "https://kidwai.kar.nic.in",
            "covers": ["cancer treatment"],
            "eligibility": "Cancer patients",
        },
        {
            "name": "St. John's Medical College Charity Fund",
            "description": "Medical assistance for poor patients",
            "contact": "080-22065000",
            "website": "https://www.stjohns.in",
            "covers": ["general medical care", "surgeries"],
            "eligibility": "Income based assessment",
        },
    ],
    "chennai": [
        {
            "name": "Adyar Cancer Institute Trust",
            "description": "Cancer care for economically weak",
            "contact": "044-24910754",
            "website": "https://www.cancerinstitutewia.in",
            "covers": ["cancer treatment"],
            "eligibility": "Cancer patients, income based",
        },
        {
            "name": "Apollo Hospitals Patient Assistance",
            "description": "Financial aid programs",
            "contact": "044-28293333",
            "website": "https://www.apollohospitals.com",
            "covers": ["cardiac care", "oncology", "transplants"],
            "eligibility": "Case-by-case evaluation",
        },
    ],
    "hyderabad": [
        {
            "name": "Care Foundation",
            "description": "Medical assistance for underprivileged",
            "contact": "040-30418888",
            "website": "https://www.carehospitals.com",
            "covers": ["cardiac care", "general surgeries"],
            "eligibility": "Income proof required",
        },
        {
            "name": "MNJ Cancer Hospital Trust",
            "description": "Free cancer treatment",
            "contact": "040-27505566",
            "website": "https://mnjcancerhospital.org",
            "covers": ["cancer treatment"],
            "eligibility": "Cancer patients",
        },
    ],
    "kolkata": [
        {
            "name": "Ramakrishna Mission Seva Pratishthan",
            "description": "Medical care and financial assistance",
            "contact": "033-24758080",
            "website": "https://rkmsp.org",
            "covers": ["general medical care", "surgeries"],
            "eligibility": "All patients, especially underprivileged",
        },
        {
            "name": "Bharat Sevashram Sangha",
            "description": "Free medical services",
            "contact": "033-24755234",
            "website": "https://www.bharatsevashram.org",
            "covers": ["general healthcare"],
            "eligibility": "Open to all",
        },
    ],
    # Default for other cities
    "default": [
        {
            "name": "Prime Minister's National Relief Fund (PMNRF)",
            "description": "Financial assistance for medical treatment",
            "contact": "Apply online",
            "website": "https://pmnrf.gov.in",
            "covers": ["major surgeries", "critical illness", "transplants"],
            "eligibility": "Indian citizens with financial need",
        },
        {
            "name": "Chief Minister's Relief Fund",
            "description": "State-level medical assistance",
            "contact": "Check state government website",
            "website": "Varies by state",
            "covers": ["medical emergencies", "surgeries"],
            "eligibility": "State residents with financial need",
        },
    ],
}


# Government Health Schemes
GOVERNMENT_SCHEMES = [
    {
        "name": "Ayushman Bharat - PMJAY",
        "description": "Free healthcare up to Rs 5 lakh per family per year",
        "eligibility": "BPL families, SECC database beneficiaries",
        "coverage": 500000,
        "website": "https://pmjay.gov.in",
        "how_to_apply": "Check eligibility at mera.pmjay.gov.in or visit nearest Ayushman Mitra",
        "covers": ["hospitalization", "surgeries", "pre/post care"],
    },
    {
        "name": "Central Government Health Scheme (CGHS)",
        "description": "Healthcare for central government employees and pensioners",
        "eligibility": "Central government employees, pensioners, and dependents",
        "coverage": "As per CGHS rates",
        "website": "https://cghs.gov.in",
        "how_to_apply": "Through employer or pension office",
        "covers": ["OPD", "hospitalization", "medicines"],
    },
    {
        "name": "Employees' State Insurance (ESI)",
        "description": "Medical care for organized sector workers",
        "eligibility": "Employees earning up to Rs 21,000/month",
        "coverage": "Full medical coverage",
        "website": "https://esic.nic.in",
        "how_to_apply": "Through employer",
        "covers": ["medical care", "maternity", "disability"],
    },
    {
        "name": "Rashtriya Arogya Nidhi (RAN)",
        "description": "Financial assistance for BPL patients with life-threatening diseases",
        "eligibility": "BPL patients treated at government hospitals",
        "coverage": 1500000,
        "website": "https://main.mohfw.gov.in",
        "how_to_apply": "Through Medical Superintendent of government hospital",
        "covers": ["heart surgery", "kidney transplant", "cancer", "major surgeries"],
    },
    {
        "name": "Health Minister's Discretionary Grant (HMDG)",
        "description": "Financial assistance for patients below poverty line",
        "eligibility": "BPL patients at government hospitals",
        "coverage": 125000,
        "website": "https://main.mohfw.gov.in",
        "how_to_apply": "Apply to Health Ministry",
        "covers": ["life-threatening diseases treatment"],
    },
]


# Insurance Recommendations
INSURANCE_RECOMMENDATIONS = [
    {
        "type": "health_insurance",
        "name": "Star Health Insurance",
        "plans": [
            {"name": "Family Health Optima", "coverage": "3-25 Lakh", "premium_starts": "Rs 8,000/year"},
            {"name": "Comprehensive Health", "coverage": "5-1 Crore", "premium_starts": "Rs 12,000/year"},
        ],
        "website": "https://www.starhealth.in",
        "features": ["No waiting period for accidents", "Cashless at 14,000+ hospitals", "Day care procedures covered"],
    },
    {
        "type": "health_insurance",
        "name": "HDFC ERGO Health",
        "plans": [
            {"name": "Optima Secure", "coverage": "3-50 Lakh", "premium_starts": "Rs 6,000/year"},
            {"name": "My Health Suraksha", "coverage": "3-1 Crore", "premium_starts": "Rs 10,000/year"},
        ],
        "website": "https://www.hdfcergo.com",
        "features": ["Restore benefit", "No claim bonus up to 100%", "Global coverage options"],
    },
    {
        "type": "health_insurance",
        "name": "ICICI Lombard Health",
        "plans": [
            {"name": "Complete Health", "coverage": "5-50 Lakh", "premium_starts": "Rs 7,500/year"},
            {"name": "Elevate", "coverage": "10 Lakh - 3 Crore", "premium_starts": "Rs 15,000/year"},
        ],
        "website": "https://www.icicilombard.com",
        "features": ["Unlimited restoration", "OPD cover available", "Mental health covered"],
    },
    {
        "type": "critical_illness",
        "name": "Max Bupa Critical Illness Cover",
        "plans": [
            {"name": "CritiCare Plus", "coverage": "5-50 Lakh", "premium_starts": "Rs 5,000/year"},
        ],
        "website": "https://www.nivabupa.com",
        "features": ["Covers 40+ critical illnesses", "Lump sum payout", "Income tax benefits u/s 80D"],
    },
    {
        "type": "government_insurance",
        "name": "Pradhan Mantri Suraksha Bima Yojana",
        "plans": [
            {"name": "PMSBY", "coverage": "2 Lakh (accident)", "premium_starts": "Rs 12/year"},
        ],
        "website": "https://jansuraksha.gov.in",
        "features": ["Available through all banks", "Auto-debit from savings account", "Age 18-70"],
    },
]


# Hospital Financial Assistance Programs
HOSPITAL_PROGRAMS = {
    "apollo": {
        "name": "Apollo Hospitals Financial Assistance",
        "description": "EMI options and charity programs",
        "options": [
            "No-cost EMI for 6-12 months",
            "Apollo Foundation charity fund",
            "Corporate tie-ups for reduced rates",
        ],
        "contact": "Ask billing department",
    },
    "fortis": {
        "name": "Fortis Memorial Research Institute Support",
        "description": "Financial counseling and assistance",
        "options": [
            "Payment plans available",
            "Fortis Foundation support",
            "Insurance desk assistance",
        ],
        "contact": "Financial counselor at hospital",
    },
    "max": {
        "name": "Max Healthcare Patient Support",
        "description": "Financial assistance programs",
        "options": [
            "EMI facilities",
            "Charity care for eligible patients",
            "Insurance assistance",
        ],
        "contact": "Patient relations department",
    },
    "default": {
        "name": "Hospital Financial Counseling",
        "description": "Most hospitals offer payment assistance",
        "options": [
            "Ask for EMI/payment plan options",
            "Inquire about charity care programs",
            "Request itemized bill review",
            "Ask about cash discounts",
        ],
        "contact": "Hospital billing or patient relations",
    },
}


async def get_financial_assistance(
    city: str,
    hospital_name: str,
    bill_amount: float,
    procedure: str,
    patient_income: Optional[float] = None
) -> Dict[str, Any]:
    """
    Get comprehensive financial assistance options for a patient
    """
    city_lower = city.lower()
    hospital_lower = hospital_name.lower()

    # Get NGOs for the city
    ngos = NGO_DATABASE.get(city_lower, NGO_DATABASE["default"])
    # Add default national NGOs to city-specific ones
    if city_lower != "default":
        ngos = ngos + NGO_DATABASE["default"]

    # Get hospital-specific programs
    hospital_program = HOSPITAL_PROGRAMS.get("default")
    for key in HOSPITAL_PROGRAMS:
        if key in hospital_lower:
            hospital_program = HOSPITAL_PROGRAMS[key]
            break

    # Filter government schemes based on potential eligibility
    applicable_schemes = []
    for scheme in GOVERNMENT_SCHEMES:
        # Simple eligibility check - in real app would be more sophisticated
        applicable_schemes.append({
            **scheme,
            "potentially_applicable": True,
            "recommendation": _get_scheme_recommendation(scheme, bill_amount, patient_income)
        })

    # Get insurance recommendations
    insurance_recs = _get_insurance_recommendations(bill_amount, procedure)

    # Calculate potential coverage
    max_govt_coverage = max([s.get("coverage", 0) for s in GOVERNMENT_SCHEMES if isinstance(s.get("coverage"), int)])

    return {
        "bill_assessment": {
            "amount": bill_amount,
            "assessment": "VALID",
            "message": "This bill appears to be fairly priced. Here are options to help cover the cost.",
        },
        "ngos_in_city": ngos,
        "government_schemes": applicable_schemes,
        "hospital_programs": hospital_program,
        "insurance_recommendations": insurance_recs,
        "crowdfunding_options": [
            {
                "platform": "Ketto",
                "website": "https://www.ketto.org",
                "description": "India's most trusted medical crowdfunding platform",
                "success_rate": "80% of campaigns reach their goal",
            },
            {
                "platform": "Milaap",
                "website": "https://www.milaap.org",
                "description": "Crowdfunding for medical emergencies",
                "success_rate": "Over Rs 1000 Cr raised for medical causes",
            },
            {
                "platform": "ImpactGuru",
                "website": "https://www.impactguru.com",
                "description": "Medical fundraising with hospital partnerships",
                "success_rate": "Partnered with 200+ hospitals",
            },
        ],
        "immediate_actions": [
            "Check eligibility for Ayushman Bharat at mera.pmjay.gov.in",
            f"Contact NGOs in {city} for financial assistance",
            "Ask hospital about EMI/payment plan options",
            "Apply to PM National Relief Fund for major treatments",
            "Consider medical crowdfunding if other options exhausted",
        ],
        "future_protection": {
            "message": "Protect yourself from future medical expenses",
            "recommendations": insurance_recs[:3],
            "tax_benefits": "Health insurance premiums qualify for tax deduction under Section 80D (up to Rs 25,000 for self, Rs 50,000 for senior citizens)",
        },
        "max_potential_coverage": max_govt_coverage,
    }


def _get_scheme_recommendation(scheme: Dict, bill_amount: float, income: Optional[float]) -> str:
    """Get personalized recommendation for a scheme"""
    if scheme["name"] == "Ayushman Bharat - PMJAY":
        return "HIGHLY RECOMMENDED - Check eligibility immediately. Covers up to Rs 5 lakh."
    elif scheme["name"] == "Rashtriya Arogya Nidhi (RAN)":
        if bill_amount > 100000:
            return "Recommended for major treatments at government hospitals"
        return "Consider if treatment at government hospital"
    elif scheme["name"] == "CGHS":
        return "Check if you or family members are central government employees"
    elif scheme["name"] == "ESI":
        return "Check if your employer is registered under ESI"
    else:
        return "Check eligibility based on your situation"


def _get_insurance_recommendations(bill_amount: float, procedure: str) -> List[Dict]:
    """Get insurance recommendations based on bill amount"""
    recommendations = []

    # Recommend coverage based on bill amount
    recommended_coverage = max(bill_amount * 3, 500000)  # At least 3x the bill or 5 lakh

    for insurance in INSURANCE_RECOMMENDATIONS:
        rec = {
            **insurance,
            "recommendation": f"Consider coverage of at least Rs {recommended_coverage/100000:.0f} Lakh based on your medical expenses",
            "why_recommended": _get_insurance_reason(insurance, procedure),
        }
        recommendations.append(rec)

    return recommendations


def _get_insurance_reason(insurance: Dict, procedure: str) -> str:
    """Get reason why an insurance is recommended"""
    procedure_lower = procedure.lower()

    if insurance["type"] == "critical_illness":
        if any(word in procedure_lower for word in ["cancer", "heart", "kidney", "transplant"]):
            return "Critical illness cover provides lump sum for serious conditions"
        return "Provides additional financial cushion for critical conditions"
    elif insurance["type"] == "government_insurance":
        return "Very affordable option for accident coverage"
    else:
        return "Comprehensive health cover for hospitalization and surgeries"


# Quick lookup functions
def get_ngos_by_city(city: str) -> List[Dict]:
    """Get NGOs for a specific city"""
    city_lower = city.lower()
    return NGO_DATABASE.get(city_lower, NGO_DATABASE["default"])


def get_all_government_schemes() -> List[Dict]:
    """Get all government schemes"""
    return GOVERNMENT_SCHEMES


def get_insurance_options() -> List[Dict]:
    """Get all insurance options"""
    return INSURANCE_RECOMMENDATIONS
