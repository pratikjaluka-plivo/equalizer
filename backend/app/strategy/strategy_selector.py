"""
Strategy Selector - Choose the optimal negotiation approach
"""
from typing import Dict, Any, List
from app.parsers.bill_parser import BillData


# Strategy definitions
STRATEGIES = {
    "CHARITY_CARE": {
        "name": "Charity Care Application",
        "description": "Apply for the hospital's charity care program to get free or subsidized treatment",
        "success_rate": 85,
        "typical_discount": 80,
        "time_to_resolution": "2-4 weeks",
        "effort_level": "LOW",
        "steps": [
            "Request charity care application form from billing department",
            "Submit income documentation (salary slips, ITR, bank statements)",
            "Follow up within 7 days if no response",
            "Escalate to hospital administrator if denied without valid reason"
        ],
        "requirements": ["Income below hospital's threshold", "Hospital is charitable trust or has charity policy"],
    },

    "DISPUTE_AND_NEGOTIATE": {
        "name": "Dispute Errors + Negotiate",
        "description": "Challenge billing errors first, then negotiate on the corrected amount",
        "success_rate": 70,
        "typical_discount": 50,
        "time_to_resolution": "2-6 weeks",
        "effort_level": "MEDIUM",
        "steps": [
            "Demand fully itemized bill",
            "Identify and formally dispute errors/overcharges",
            "Request correction in writing",
            "Negotiate final amount based on CGHS/fair market rates",
            "Get settlement in writing before payment"
        ],
        "requirements": ["Billing errors identified", "Significant overcharge vs reference rates"],
    },

    "AGGRESSIVE_NEGOTIATION": {
        "name": "Aggressive Negotiation",
        "description": "Use all leverage points to pressure hospital into significant discount",
        "success_rate": 65,
        "typical_discount": 45,
        "time_to_resolution": "1-4 weeks",
        "effort_level": "MEDIUM",
        "steps": [
            "Send formal letter citing all leverage points",
            "Reference specific laws and hospital obligations",
            "Set deadline for response (7 days)",
            "Follow up with call to billing supervisor",
            "Escalate to hospital administrator/CEO if needed"
        ],
        "requirements": ["Multiple strong leverage points", "Hospital has vulnerabilities"],
    },

    "STANDARD_NEGOTIATION": {
        "name": "Standard Negotiation",
        "description": "Request discount citing financial hardship and market rates",
        "success_rate": 55,
        "typical_discount": 30,
        "time_to_resolution": "1-3 weeks",
        "effort_level": "LOW",
        "steps": [
            "Call billing department and request discount",
            "Mention financial hardship (if applicable)",
            "Quote CGHS/PMJAY rates as reference",
            "Ask for payment plan if lump sum is difficult",
            "Get any agreement in writing"
        ],
        "requirements": [],
    },

    "CONSUMER_COURT": {
        "name": "Consumer Court Filing",
        "description": "File complaint in Consumer Forum for unfair trade practices",
        "success_rate": 75,
        "typical_discount": 60,
        "time_to_resolution": "3-12 months",
        "effort_level": "HIGH",
        "steps": [
            "Gather all documentation (bills, communication, evidence)",
            "Draft complaint citing specific violations",
            "File in District Consumer Forum (< ₹1 Cr) or State Commission",
            "Attend hearings (can be virtual)",
            "Most cases settle before final hearing"
        ],
        "requirements": ["Clear evidence of overcharging/deficiency", "Willingness to pursue legal route"],
        "notes": "Many hospitals settle once complaint is filed to avoid precedent"
    },

    "INSURANCE_DISPUTE": {
        "name": "Insurance/TPA Route",
        "description": "Involve insurance company to negotiate or dispute charges",
        "success_rate": 60,
        "typical_discount": 40,
        "time_to_resolution": "2-4 weeks",
        "effort_level": "LOW",
        "steps": [
            "Contact your insurance TPA",
            "Request their standard rates for the procedure",
            "Ask TPA to negotiate with hospital",
            "File complaint with IRDAI if TPA is unhelpful"
        ],
        "requirements": ["Active health insurance", "Hospital is network hospital"],
    }
}


def select_strategy(
        bill_data: BillData,
        price_comparison: Dict[str, Any],
        hospital_intel: Dict[str, Any],
        leverage_points: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Select the optimal strategy based on the situation
    Returns primary strategy and alternatives
    """

    recommended_approach = leverage_points.get("recommended_approach", "STANDARD_NEGOTIATION")
    strategies_to_consider = []

    # Primary strategy based on leverage analysis
    primary_strategy = STRATEGIES.get(recommended_approach, STRATEGIES["STANDARD_NEGOTIATION"])

    # Build list of applicable strategies
    charity_info = hospital_intel.get("charity_obligations", {})

    # Check Charity Care eligibility
    if charity_info.get("is_charitable_trust") or charity_info.get("has_charity_policy"):
        income_limit = charity_info.get("income_limit", 0)
        if bill_data.patient_income and bill_data.patient_income < income_limit:
            strategies_to_consider.append({
                **STRATEGIES["CHARITY_CARE"],
                "applicable": True,
                "priority": 1,
                "reason": f"Your income (₹{bill_data.patient_income:,}) is below the hospital's charity care threshold (₹{income_limit:,})"
            })

    # Check Dispute route
    if price_comparison.get("assessment") in ["SEVERE_OVERCHARGE", "SIGNIFICANT_OVERCHARGE"]:
        strategies_to_consider.append({
            **STRATEGIES["DISPUTE_AND_NEGOTIATE"],
            "applicable": True,
            "priority": 2,
            "reason": f"Bill is {price_comparison.get('overcharge_percentage', 0):.0f}% above government rates"
        })

    # Check Aggressive Negotiation
    if leverage_points.get("level") in ["HIGH", "MAXIMUM"]:
        strategies_to_consider.append({
            **STRATEGIES["AGGRESSIVE_NEGOTIATION"],
            "applicable": True,
            "priority": 3,
            "reason": f"Hospital has high vulnerability (score: {leverage_points.get('total_score', 0)})"
        })

    # Standard negotiation is always applicable
    strategies_to_consider.append({
        **STRATEGIES["STANDARD_NEGOTIATION"],
        "applicable": True,
        "priority": 4,
        "reason": "Available for all cases"
    })

    # Consumer Court as backup
    if price_comparison.get("overcharge_vs_cghs", 0) > 20000:  # Only for significant amounts
        strategies_to_consider.append({
            **STRATEGIES["CONSUMER_COURT"],
            "applicable": True,
            "priority": 5,
            "reason": f"Overcharge of ₹{price_comparison.get('overcharge_vs_cghs', 0):,} justifies legal action"
        })

    # Sort by priority
    strategies_to_consider.sort(key=lambda x: x.get("priority", 99))

    # Calculate expected savings for primary strategy
    primary = strategies_to_consider[0] if strategies_to_consider else STRATEGIES["STANDARD_NEGOTIATION"]
    expected_discount = primary.get("typical_discount", 30)
    expected_savings = bill_data.total_amount * (expected_discount / 100)
    expected_final_amount = bill_data.total_amount - expected_savings

    return {
        "primary_strategy": primary,
        "alternative_strategies": strategies_to_consider[1:4],  # Top 3 alternatives
        "escalation_strategy": STRATEGIES["CONSUMER_COURT"],

        "expected_outcome": {
            "original_bill": bill_data.total_amount,
            "expected_discount_percentage": expected_discount,
            "expected_savings": round(expected_savings),
            "expected_final_amount": round(expected_final_amount),
            "success_probability": primary.get("success_rate", 50),
        },

        "recommendation": f"Start with {primary['name']}. If unsuccessful, escalate to {strategies_to_consider[1]['name'] if len(strategies_to_consider) > 1 else 'Consumer Court'}.",
    }
