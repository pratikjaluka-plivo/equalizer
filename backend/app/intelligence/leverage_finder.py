"""
Leverage Finder - Identifies ALL pressure points against a hospital
This is where we build the ammunition
"""
from typing import Dict, Any, List
from app.parsers.bill_parser import BillData


def find_all_leverage(
        bill_data: BillData,
        price_comparison: Dict[str, Any],
        hospital_intel: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Find every possible leverage point against this hospital for this bill
    Returns a prioritized list of pressure points
    """
    leverage_points: List[Dict[str, Any]] = []
    total_leverage_score = 0

    # 1. PRICING LEVERAGE - They're overcharging
    if price_comparison.get("assessment") in ["SEVERE_OVERCHARGE", "SIGNIFICANT_OVERCHARGE"]:
        overcharge = price_comparison.get("overcharge_vs_cghs", 0)
        percentage = price_comparison.get("overcharge_percentage", 0)

        leverage_points.append({
            "type": "PRICING_OVERCHARGE",
            "severity": "HIGH" if percentage > 200 else "MEDIUM",
            "score": min(40, percentage / 5),
            "title": f"Overcharged by {percentage:.0f}% vs Government Rates",
            "detail": f"You were billed ₹{bill_data.total_amount:,.0f}. CGHS rate for this procedure is ₹{price_comparison.get('cghs_rate_nabh', 0):,.0f}. "
                      f"This hospital accepts CGHS rates for government employees - they should accept similar rates for you.",
            "evidence": f"CGHS Rate: ₹{price_comparison.get('cghs_rate_nabh', 0):,} | PMJAY Rate: ₹{price_comparison.get('pmjay_rate', 0):,}",
            "action": "Demand itemized bill and question each charge against CGHS rates"
        })
        total_leverage_score += min(40, percentage / 5)

    # 2. CGHS EMPANELMENT LEVERAGE
    if hospital_intel.get("accreditation", {}).get("cghs_empanelled"):
        leverage_points.append({
            "type": "CGHS_EMPANELLED",
            "severity": "HIGH",
            "score": 25,
            "title": "Hospital Accepts Government Rates",
            "detail": "This hospital is CGHS empanelled, meaning they routinely accept government-mandated rates. "
                      "They cannot claim these rates are unsustainable when they accept them daily for government employees.",
            "evidence": "CGHS Empanelment Status: Active",
            "action": "Quote their CGHS empanelment and demand same rates"
        })
        total_leverage_score += 25

    # 3. CHARITABLE TRUST LEVERAGE
    charity_info = hospital_intel.get("charity_obligations", {})
    if charity_info.get("is_charitable_trust"):
        leverage_points.append({
            "type": "CHARITABLE_TRUST",
            "severity": "HIGH",
            "score": 30,
            "title": "Charitable Trust - MUST Provide Subsidized Care",
            "detail": "This hospital is registered as a charitable trust and enjoys tax exemptions. "
                      "In exchange, they are LEGALLY REQUIRED to provide subsidized care. "
                      "Failure to do so can jeopardize their tax-exempt status.",
            "evidence": f"Hospital Type: Charitable Trust | Tax Status: Exempt under 12A/80G",
            "action": "Demand charity care application and quote their legal obligations"
        })
        total_leverage_score += 30

        if charity_info.get("income_limit"):
            leverage_points.append({
                "type": "CHARITY_CARE_ELIGIBLE",
                "severity": "HIGH" if bill_data.patient_income and bill_data.patient_income < charity_info["income_limit"] else "MEDIUM",
                "score": 20,
                "title": f"Charity Care Income Limit: ₹{charity_info['income_limit']:,}/year",
                "detail": f"This hospital's charity care policy covers patients earning under ₹{charity_info['income_limit']:,}/year. "
                          "If you qualify, you may be entitled to FREE or heavily subsidized care.",
                "evidence": f"Income Limit: ₹{charity_info['income_limit']:,}",
                "action": "Apply for charity care immediately"
            })
            total_leverage_score += 20

    # 4. EWS QUOTA LEVERAGE
    if charity_info.get("ews_quota"):
        leverage_points.append({
            "type": "EWS_QUOTA",
            "severity": "MEDIUM",
            "score": 15,
            "title": f"EWS Quota: {charity_info['ews_quota']}",
            "detail": f"This hospital is required to reserve {charity_info['ews_quota']} of beds for "
                      "Economically Weaker Sections at subsidized rates. This is often under-utilized.",
            "evidence": f"State Mandate: {charity_info['ews_quota']} EWS reservation",
            "action": "File RTI to check EWS quota compliance"
        })
        total_leverage_score += 15

    # 5. NABH ACCREDITATION LEVERAGE
    if hospital_intel.get("accreditation", {}).get("nabh_accredited"):
        leverage_points.append({
            "type": "NABH_STANDARDS",
            "severity": "MEDIUM",
            "score": 15,
            "title": "NABH Accredited - Bound by Standards",
            "detail": "NABH accreditation requires hospitals to follow patient rights standards including "
                      "transparent billing. You can complain to NABH if standards are violated.",
            "evidence": f"NABH Valid Until: {hospital_intel['accreditation'].get('nabh_valid_until', 'Active')}",
            "action": "Threaten NABH complaint for billing standard violations"
        })
        total_leverage_score += 15

    # 6. COMPLAINT HISTORY LEVERAGE
    complaints = hospital_intel.get("complaint_history", {})
    if complaints.get("consumer_complaints_last_year", 0) > 30:
        leverage_points.append({
            "type": "HIGH_COMPLAINTS",
            "severity": "MEDIUM",
            "score": 20,
            "title": f"{complaints['consumer_complaints_last_year']} Consumer Complaints Last Year",
            "detail": "This hospital has a high volume of consumer complaints. They are sensitive to "
                      "additional complaints and negative publicity.",
            "evidence": f"Consumer Complaints (2024): {complaints['consumer_complaints_last_year']} | "
                        f"Medical Council Complaints: {complaints.get('medical_council_complaints', 0)}",
            "action": "Mention you are prepared to add to their complaint record"
        })
        total_leverage_score += 20

    # 7. RECENT VIOLATIONS LEVERAGE
    if complaints.get("recent_violations"):
        leverage_points.append({
            "type": "RECENT_VIOLATIONS",
            "severity": "HIGH",
            "score": 25,
            "title": "Recent Regulatory Violations",
            "detail": f"This hospital has recent violations: {', '.join(complaints['recent_violations'])}. "
                      "They are under regulatory scrutiny and will want to avoid additional attention.",
            "evidence": f"Violations: {', '.join(complaints['recent_violations'])}",
            "action": "Reference their violation history in your complaint"
        })
        total_leverage_score += 25

    # 8. CONSUMER PROTECTION ACT LEVERAGE (Always applicable)
    leverage_points.append({
        "type": "CONSUMER_PROTECTION_ACT",
        "severity": "HIGH",
        "score": 20,
        "title": "Consumer Protection Act, 2019",
        "detail": "Medical services are covered under the Consumer Protection Act, 2019. "
                  "You can file a complaint in Consumer Court for unfair trade practices, "
                  "deficiency in service, or excessive charging. Courts have awarded significant "
                  "compensation in medical billing cases.",
        "evidence": "CPA 2019 Section 2(42) - 'Service' includes medical services",
        "action": "Threaten Consumer Court complaint with specific sections"
    })
    total_leverage_score += 20

    # 9. ITEMIZED BILL RIGHT (Always applicable)
    leverage_points.append({
        "type": "ITEMIZED_BILL_RIGHT",
        "severity": "MEDIUM",
        "score": 15,
        "title": "Right to Itemized Bill",
        "detail": "You have a legal right to receive a fully itemized bill with breakdown of all charges. "
                  "Many hospitals provide only summary bills to hide overcharges.",
        "evidence": "Clinical Establishments Act + Consumer Protection Act",
        "action": "Demand complete itemization before any payment"
    })
    total_leverage_score += 15

    # 10. INSURANCE/TPA LEVERAGE
    leverage_points.append({
        "type": "INSURANCE_REGULATIONS",
        "severity": "MEDIUM",
        "score": 10,
        "title": "IRDAI Regulations on Cashless Claims",
        "detail": "If you have insurance, hospitals cannot force you to pay and claim later for empanelled procedures. "
                  "IRDAI has strict guidelines on cashless settlement timelines.",
        "evidence": "IRDAI (Health Insurance) Regulations, 2016",
        "action": "Involve your insurance company/TPA in negotiations"
    })
    total_leverage_score += 10

    # 11. SOCIAL MEDIA / REPUTATION LEVERAGE
    if hospital_intel.get("negotiation_intel", {}).get("has_pr_sensitivity"):
        leverage_points.append({
            "type": "REPUTATION_RISK",
            "severity": "MEDIUM",
            "score": 15,
            "title": "Reputation Sensitivity",
            "detail": "This hospital has shown sensitivity to public complaints and media attention. "
                      "A well-documented complaint on social media or to health journalists can be effective.",
            "evidence": "Hospital responds to online complaints within 24-48 hours typically",
            "action": "Prepare detailed social media post as escalation option"
        })
        total_leverage_score += 15

    # Sort by score (highest first)
    leverage_points.sort(key=lambda x: x["score"], reverse=True)

    # Determine overall leverage level
    if total_leverage_score > 150:
        overall_level = "MAXIMUM"
        summary = "You have exceptional leverage. This hospital has multiple vulnerabilities."
    elif total_leverage_score > 100:
        overall_level = "HIGH"
        summary = "You have strong leverage. Multiple pressure points available."
    elif total_leverage_score > 60:
        overall_level = "MEDIUM"
        summary = "You have moderate leverage. Focus on your strongest points."
    else:
        overall_level = "LOW"
        summary = "Limited leverage identified. Consumer Court remains your strongest option."

    return {
        "total_score": min(200, total_leverage_score),
        "level": overall_level,
        "summary": summary,
        "points": leverage_points,
        "top_3": leverage_points[:3],
        "recommended_approach": _get_recommended_approach(leverage_points, bill_data, hospital_intel)
    }


def _get_recommended_approach(
        leverage_points: List[Dict],
        bill_data: BillData,
        hospital_intel: Dict
) -> str:
    """Determine the recommended negotiation approach based on leverage"""

    # Check for charity care eligibility first
    charity_info = hospital_intel.get("charity_obligations", {})
    if charity_info.get("is_charitable_trust") or charity_info.get("has_charity_policy"):
        if bill_data.patient_income:
            income_limit = charity_info.get("income_limit", 0)
            if bill_data.patient_income < income_limit:
                return "CHARITY_CARE"

    # Check for severe overcharge - dispute route
    for point in leverage_points:
        if point["type"] == "PRICING_OVERCHARGE" and point["severity"] == "HIGH":
            return "DISPUTE_AND_NEGOTIATE"

    # Check for high hospital vulnerability
    vuln = hospital_intel.get("vulnerability_analysis", {})
    if vuln.get("level") == "HIGH":
        return "AGGRESSIVE_NEGOTIATION"

    # Default to standard negotiation
    return "STANDARD_NEGOTIATION"
