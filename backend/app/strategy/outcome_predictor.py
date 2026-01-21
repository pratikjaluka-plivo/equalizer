"""
Outcome Predictor - Estimates success probability and expected savings
"""
from typing import Dict, Any
from app.parsers.bill_parser import BillData


def predict_outcome(
        bill_data: BillData,
        price_comparison: Dict[str, Any],
        hospital_intel: Dict[str, Any],
        leverage_points: Dict[str, Any],
        strategy: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Predict the likely outcome of negotiation
    """

    # Base success rate from strategy
    base_success = strategy.get("primary_strategy", {}).get("success_rate", 50)
    base_discount = strategy.get("primary_strategy", {}).get("typical_discount", 30)

    # Adjust based on leverage
    leverage_score = leverage_points.get("total_score", 50)
    if leverage_score > 150:
        success_modifier = 15
        discount_modifier = 20
    elif leverage_score > 100:
        success_modifier = 10
        discount_modifier = 15
    elif leverage_score > 60:
        success_modifier = 5
        discount_modifier = 10
    else:
        success_modifier = 0
        discount_modifier = 0

    # Adjust based on hospital vulnerability
    vulnerability = hospital_intel.get("vulnerability_analysis", {}).get("level", "LOW")
    if vulnerability == "HIGH":
        success_modifier += 10
        discount_modifier += 10
    elif vulnerability == "MEDIUM":
        success_modifier += 5
        discount_modifier += 5

    # Adjust based on hospital's settlement history
    avg_settlement = hospital_intel.get("negotiation_intel", {}).get("average_settlement_discount", 30)
    discount_modifier += (avg_settlement - 30) / 2  # Adjust towards hospital's historical average

    # Calculate final estimates
    final_success_rate = min(95, base_success + success_modifier)
    final_discount = min(90, base_discount + discount_modifier)

    # Calculate amounts
    expected_discount_amount = bill_data.total_amount * (final_discount / 100)
    expected_final_low = bill_data.total_amount * (1 - (final_discount + 10) / 100)
    expected_final_high = bill_data.total_amount * (1 - (final_discount - 10) / 100)
    expected_final_mid = bill_data.total_amount * (1 - final_discount / 100)

    # Compare to reference rates
    cghs_rate = price_comparison.get("cghs_rate_nabh", 0)
    target_amount = price_comparison.get("target_realistic", expected_final_mid)

    # Determine confidence level
    if final_success_rate > 80 and leverage_score > 100:
        confidence = "HIGH"
        confidence_explanation = "Strong leverage and hospital vulnerability make success likely"
    elif final_success_rate > 60:
        confidence = "MEDIUM"
        confidence_explanation = "Reasonable chance of success with proper negotiation"
    else:
        confidence = "LOW"
        confidence_explanation = "May require escalation to Consumer Court for resolution"

    return {
        "success_probability": round(final_success_rate),
        "confidence": confidence,
        "confidence_explanation": confidence_explanation,

        "expected_discount": {
            "percentage": round(final_discount),
            "amount": round(expected_discount_amount),
        },

        "expected_final_amount": {
            "low": round(max(cghs_rate * 0.9, expected_final_low)),  # Don't expect below CGHS
            "mid": round(max(cghs_rate, expected_final_mid)),
            "high": round(expected_final_high),
        },

        "target_amount": round(target_amount),
        "original_bill": bill_data.total_amount,

        "savings_estimate": {
            "minimum": round(bill_data.total_amount - expected_final_high),
            "expected": round(expected_discount_amount),
            "maximum": round(bill_data.total_amount - max(cghs_rate * 0.9, expected_final_low)),
        },

        "time_estimate": strategy.get("primary_strategy", {}).get("time_to_resolution", "2-4 weeks"),

        "breakdown": {
            "base_success_rate": base_success,
            "leverage_modifier": success_modifier,
            "base_discount": base_discount,
            "discount_modifier": round(discount_modifier),
            "hospital_avg_settlement": avg_settlement,
        },

        "recommendation": _generate_recommendation(
            final_success_rate, final_discount, bill_data.total_amount,
            cghs_rate, leverage_points, strategy
        )
    }


def _generate_recommendation(
        success_rate: float,
        discount: float,
        bill_amount: float,
        cghs_rate: float,
        leverage_points: Dict,
        strategy: Dict
) -> str:
    """Generate a human-readable recommendation"""

    expected_savings = bill_amount * (discount / 100)
    strategy_name = strategy.get("primary_strategy", {}).get("name", "negotiation")

    if success_rate > 80:
        urgency = "You have strong leverage. Act quickly."
    elif success_rate > 60:
        urgency = "Your case is solid. Be persistent."
    else:
        urgency = "This may require escalation. Be prepared for Consumer Court."

    return f"""Based on your leverage (score: {leverage_points.get('total_score', 0)}/200) and hospital profile:

• Start with {strategy_name}
• Target settlement: ₹{bill_amount - expected_savings:,.0f} (down from ₹{bill_amount:,.0f})
• Expected savings: ₹{expected_savings:,.0f}
• Success probability: {success_rate}%

{urgency}

Key leverage points to emphasize:
{chr(10).join(['• ' + p['title'] for p in leverage_points.get('top_3', [])])}"""
