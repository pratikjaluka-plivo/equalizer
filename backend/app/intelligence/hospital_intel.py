"""
Hospital Intelligence - Deep profile on hospitals
NABH status, complaints, ownership, regulatory history
"""
from typing import Dict, Any, Optional
import httpx


# Sample hospital database with intelligence data
# In production, this would be fetched from NABH API, RTI data, court records
HOSPITAL_DATABASE = {
    # Mumbai Hospitals
    "kokilaben dhirubhai ambani hospital": {
        "official_name": "Kokilaben Dhirubhai Ambani Hospital",
        "city": "Mumbai",
        "state": "Maharashtra",
        "nabh_accredited": True,
        "nabh_valid_until": "2026-03-15",
        "type": "private",
        "beds": 750,
        "ownership": "Reliance Foundation",
        "cghs_empanelled": True,
        "pmjay_empanelled": False,
        "consumer_complaints_last_year": 23,
        "medical_council_complaints": 2,
        "known_issues": ["High pricing complaints", "Billing disputes"],
        "charity_care_policy": False,
        "ews_quota": "10% as per state mandate",
        "recent_violations": [],
        "average_settlement_discount": 35,
    },
    "lilavati hospital": {
        "official_name": "Lilavati Hospital and Research Centre",
        "city": "Mumbai",
        "state": "Maharashtra",
        "nabh_accredited": True,
        "nabh_valid_until": "2025-09-20",
        "type": "charitable_trust",
        "beds": 314,
        "ownership": "Lilavati Kirtilal Mehta Medical Trust",
        "cghs_empanelled": True,
        "pmjay_empanelled": False,
        "consumer_complaints_last_year": 34,
        "medical_council_complaints": 5,
        "known_issues": ["Billing transparency issues", "Long wait times"],
        "charity_care_policy": True,
        "charity_care_income_limit": 300000,  # Annual income limit for free care
        "ews_quota": "20% as charitable trust",
        "recent_violations": ["Price display violation - 2023"],
        "average_settlement_discount": 40,
    },
    "breach candy hospital": {
        "official_name": "Breach Candy Hospital Trust",
        "city": "Mumbai",
        "state": "Maharashtra",
        "nabh_accredited": True,
        "nabh_valid_until": "2025-12-01",
        "type": "charitable_trust",
        "beds": 190,
        "ownership": "Breach Candy Hospital Trust",
        "cghs_empanelled": True,
        "pmjay_empanelled": False,
        "consumer_complaints_last_year": 12,
        "medical_council_complaints": 1,
        "known_issues": [],
        "charity_care_policy": True,
        "charity_care_income_limit": 250000,
        "ews_quota": "20% as charitable trust",
        "recent_violations": [],
        "average_settlement_discount": 30,
    },
    "fortis hospital mumbai": {
        "official_name": "Fortis Hospital Mumbai",
        "city": "Mumbai",
        "state": "Maharashtra",
        "nabh_accredited": True,
        "nabh_valid_until": "2025-06-30",
        "type": "private",
        "beds": 300,
        "ownership": "IHH Healthcare (Malaysian MNC)",
        "cghs_empanelled": True,
        "pmjay_empanelled": True,
        "consumer_complaints_last_year": 67,
        "medical_council_complaints": 8,
        "known_issues": ["Dengue death case 2017", "Billing overcharge cases"],
        "charity_care_policy": False,
        "ews_quota": "10% as per state mandate",
        "recent_violations": ["NPPA drug pricing violation - 2022"],
        "average_settlement_discount": 45,
    },

    # Delhi Hospitals
    "max super speciality hospital saket": {
        "official_name": "Max Super Speciality Hospital, Saket",
        "city": "Delhi",
        "state": "Delhi",
        "nabh_accredited": True,
        "nabh_valid_until": "2025-11-15",
        "type": "private",
        "beds": 500,
        "ownership": "Max Healthcare (Radiant Life Care)",
        "cghs_empanelled": True,
        "pmjay_empanelled": True,
        "consumer_complaints_last_year": 89,
        "medical_council_complaints": 12,
        "known_issues": ["Twin death case 2017", "Multiple billing disputes"],
        "charity_care_policy": False,
        "ews_quota": "25% (Delhi High Court mandate)",
        "recent_violations": [],
        "average_settlement_discount": 40,
    },
    "apollo hospital delhi": {
        "official_name": "Indraprastha Apollo Hospital",
        "city": "Delhi",
        "state": "Delhi",
        "nabh_accredited": True,
        "nabh_valid_until": "2026-02-28",
        "type": "private",
        "beds": 710,
        "ownership": "Apollo Hospitals Enterprise Ltd",
        "cghs_empanelled": True,
        "pmjay_empanelled": True,
        "consumer_complaints_last_year": 78,
        "medical_council_complaints": 9,
        "known_issues": ["High pricing", "Insurance claim disputes"],
        "charity_care_policy": False,
        "ews_quota": "25% (Delhi High Court mandate)",
        "recent_violations": [],
        "average_settlement_discount": 35,
    },
    "aiims delhi": {
        "official_name": "All India Institute of Medical Sciences, Delhi",
        "city": "Delhi",
        "state": "Delhi",
        "nabh_accredited": True,
        "nabh_valid_until": "N/A - Government Institution",
        "type": "government",
        "beds": 2478,
        "ownership": "Government of India",
        "cghs_empanelled": True,
        "pmjay_empanelled": True,
        "consumer_complaints_last_year": 23,
        "medical_council_complaints": 3,
        "known_issues": ["Long wait times", "Overcrowding"],
        "charity_care_policy": True,
        "charity_care_income_limit": "Subsidized for all",
        "ews_quota": "100% - Government hospital",
        "recent_violations": [],
        "average_settlement_discount": 0,  # Already subsidized
    },

    # Bangalore Hospitals
    "manipal hospital bangalore": {
        "official_name": "Manipal Hospital, Old Airport Road",
        "city": "Bangalore",
        "state": "Karnataka",
        "nabh_accredited": True,
        "nabh_valid_until": "2025-08-20",
        "type": "private",
        "beds": 600,
        "ownership": "Manipal Health Enterprises",
        "cghs_empanelled": True,
        "pmjay_empanelled": True,
        "consumer_complaints_last_year": 45,
        "medical_council_complaints": 6,
        "known_issues": ["Billing complexity"],
        "charity_care_policy": False,
        "ews_quota": "10%",
        "recent_violations": [],
        "average_settlement_discount": 35,
    },
    "narayana health bangalore": {
        "official_name": "Narayana Health City",
        "city": "Bangalore",
        "state": "Karnataka",
        "nabh_accredited": True,
        "nabh_valid_until": "2026-01-15",
        "type": "private",
        "beds": 3000,
        "ownership": "Narayana Health (Dr. Devi Shetty)",
        "cghs_empanelled": True,
        "pmjay_empanelled": True,
        "consumer_complaints_last_year": 28,
        "medical_council_complaints": 4,
        "known_issues": [],
        "charity_care_policy": True,
        "charity_care_income_limit": 500000,
        "ews_quota": "20%",
        "recent_violations": [],
        "average_settlement_discount": 25,
    },

    # Generic fallback for unknown hospitals
    "unknown": {
        "official_name": "Unknown Hospital",
        "city": "Unknown",
        "state": "Unknown",
        "nabh_accredited": False,
        "type": "private",
        "beds": 0,
        "ownership": "Unknown",
        "cghs_empanelled": False,
        "pmjay_empanelled": False,
        "consumer_complaints_last_year": 0,
        "medical_council_complaints": 0,
        "known_issues": [],
        "charity_care_policy": False,
        "ews_quota": "10% (default state mandate)",
        "recent_violations": [],
        "average_settlement_discount": 30,
    }
}


# State-wise patient rights and EWS quotas
STATE_HEALTHCARE_LAWS = {
    "maharashtra": {
        "ews_quota_private": "10%",
        "ews_quota_trust": "20%",
        "price_display_mandatory": True,
        "itemized_bill_right": True,
        "clinical_establishments_act": True,
        "consumer_forum": "Maharashtra State Consumer Disputes Redressal Commission",
        "health_authority": "Maharashtra Medical Council",
        "key_laws": [
            "Maharashtra Medicare Service Persons and Medicare Service Institutions (Prevention of Violence) Act, 2010",
            "Bombay Nursing Homes Registration Act, 1949",
            "Clinical Establishments (Registration and Regulation) Act (partially adopted)"
        ],
    },
    "delhi": {
        "ews_quota_private": "25%",
        "ews_quota_trust": "25%",
        "price_display_mandatory": True,
        "itemized_bill_right": True,
        "clinical_establishments_act": True,
        "consumer_forum": "Delhi State Consumer Disputes Redressal Commission",
        "health_authority": "Delhi Medical Council",
        "key_laws": [
            "Delhi High Court mandate on 25% EWS beds in private hospitals on subsidized land",
            "Delhi Nursing Homes Registration Act, 1953",
            "Clinical Establishments (Registration and Regulation) Act, 2010"
        ],
        "special_notes": "Delhi HC has strong precedents on hospital pricing disputes"
    },
    "karnataka": {
        "ews_quota_private": "10%",
        "ews_quota_trust": "20%",
        "price_display_mandatory": True,
        "itemized_bill_right": True,
        "clinical_establishments_act": True,
        "consumer_forum": "Karnataka State Consumer Disputes Redressal Commission",
        "health_authority": "Karnataka Medical Council",
        "key_laws": [
            "Karnataka Private Medical Establishments Act, 2007",
            "Clinical Establishments (Registration and Regulation) Act, 2010"
        ],
    },
    "default": {
        "ews_quota_private": "10%",
        "ews_quota_trust": "20%",
        "price_display_mandatory": True,
        "itemized_bill_right": True,
        "clinical_establishments_act": False,
        "consumer_forum": "State Consumer Disputes Redressal Commission",
        "health_authority": "State Medical Council",
        "key_laws": [
            "Consumer Protection Act, 2019",
            "Indian Medical Council Act",
        ],
    }
}


def normalize_hospital_name(name: str) -> str:
    """Normalize hospital name for lookup"""
    name = name.lower().strip()
    # Remove common suffixes
    for suffix in [" hospital", " hospitals", " medical centre", " medical center", " healthcare"]:
        name = name.replace(suffix, "")
    return name.strip()


def find_hospital(name: str, city: Optional[str] = None) -> Dict[str, Any]:
    """Find hospital in database"""
    normalized = normalize_hospital_name(name)

    # Try direct match first
    for key, data in HOSPITAL_DATABASE.items():
        if normalized in key or key in normalized:
            if city and city.lower() != data.get("city", "").lower():
                continue
            return data

    # Try partial match
    for key, data in HOSPITAL_DATABASE.items():
        key_words = set(key.split())
        name_words = set(normalized.split())
        if len(key_words.intersection(name_words)) >= 2:
            if city and city.lower() != data.get("city", "").lower():
                continue
            return data

    return HOSPITAL_DATABASE["unknown"]


async def get_hospital_intelligence(
        hospital_name: str,
        city: str,
        state: str
) -> Dict[str, Any]:
    """
    Get comprehensive intelligence on a hospital
    This is ammunition for negotiation
    """
    # Find hospital in database
    hospital_data = find_hospital(hospital_name, city)

    # Get state-specific laws
    state_laws = STATE_HEALTHCARE_LAWS.get(
        state.lower(),
        STATE_HEALTHCARE_LAWS["default"]
    )

    # Determine vulnerability level
    vulnerability_score = 0
    vulnerabilities = []

    # High complaint count = vulnerable to regulatory pressure
    if hospital_data.get("consumer_complaints_last_year", 0) > 50:
        vulnerability_score += 30
        vulnerabilities.append("High consumer complaint volume - sensitive to reputation damage")

    if hospital_data.get("medical_council_complaints", 0) > 5:
        vulnerability_score += 20
        vulnerabilities.append("Multiple medical council complaints - regulatory scrutiny likely")

    # Trust hospitals have charity obligations
    if hospital_data.get("type") == "charitable_trust":
        vulnerability_score += 25
        vulnerabilities.append("Charitable trust - MUST provide subsidized care to maintain tax status")

    # Recent violations = very vulnerable
    if hospital_data.get("recent_violations"):
        vulnerability_score += 25
        vulnerabilities.append(f"Recent violations: {', '.join(hospital_data['recent_violations'])}")

    # NABH accredited hospitals must follow standards
    if hospital_data.get("nabh_accredited"):
        vulnerability_score += 10
        vulnerabilities.append("NABH accredited - bound by NABH standards, can complain to NABH")

    # CGHS empanelled = accepts lower rates
    if hospital_data.get("cghs_empanelled"):
        vulnerability_score += 15
        vulnerabilities.append("CGHS empanelled - already accepts government rates for same procedures")

    # EWS quota compliance can be checked
    if state_laws.get("ews_quota_private"):
        vulnerabilities.append(f"EWS quota: {hospital_data.get('ews_quota', state_laws['ews_quota_private'])} - compliance can be RTI'd")

    return {
        "hospital_profile": {
            "name": hospital_data.get("official_name", hospital_name),
            "city": hospital_data.get("city", city),
            "state": hospital_data.get("state", state),
            "type": hospital_data.get("type", "private"),
            "ownership": hospital_data.get("ownership", "Unknown"),
            "beds": hospital_data.get("beds", 0),
        },

        "accreditation": {
            "nabh_accredited": hospital_data.get("nabh_accredited", False),
            "nabh_valid_until": hospital_data.get("nabh_valid_until"),
            "cghs_empanelled": hospital_data.get("cghs_empanelled", False),
            "pmjay_empanelled": hospital_data.get("pmjay_empanelled", False),
        },

        "complaint_history": {
            "consumer_complaints_last_year": hospital_data.get("consumer_complaints_last_year", 0),
            "medical_council_complaints": hospital_data.get("medical_council_complaints", 0),
            "known_issues": hospital_data.get("known_issues", []),
            "recent_violations": hospital_data.get("recent_violations", []),
        },

        "charity_obligations": {
            "has_charity_policy": hospital_data.get("charity_care_policy", False),
            "income_limit": hospital_data.get("charity_care_income_limit"),
            "ews_quota": hospital_data.get("ews_quota", state_laws.get("ews_quota_private")),
            "is_charitable_trust": hospital_data.get("type") == "charitable_trust",
        },

        "state_laws": state_laws,

        "vulnerability_analysis": {
            "score": min(100, vulnerability_score),
            "level": "HIGH" if vulnerability_score > 60 else "MEDIUM" if vulnerability_score > 30 else "LOW",
            "points": vulnerabilities,
        },

        "negotiation_intel": {
            "average_settlement_discount": hospital_data.get("average_settlement_discount", 30),
            "accepts_cghs_rates": hospital_data.get("cghs_empanelled", False),
            "accepts_pmjay_rates": hospital_data.get("pmjay_empanelled", False),
            "has_pr_sensitivity": hospital_data.get("consumer_complaints_last_year", 0) > 30,
        }
    }
