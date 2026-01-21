"""
CGHS Rate lookup functionality
"""
from typing import Optional, Dict, Any
from app.intelligence.pricing_engine import CGHS_RATES, normalize_procedure


def get_rate(procedure_code: str) -> Optional[Dict[str, Any]]:
    """Get CGHS rate for a procedure code"""
    # Normalize the procedure code
    normalized = normalize_procedure(procedure_code)

    rate_data = CGHS_RATES.get(normalized)
    if rate_data:
        return {
            "procedure": normalized,
            "description": rate_data.get("description", normalized),
            "nabh_rate": rate_data.get("nabh"),
            "non_nabh_rate": rate_data.get("non_nabh"),
        }

    return None


def list_all_rates() -> Dict[str, Any]:
    """List all available CGHS rates"""
    return {
        key: {
            "description": data.get("description", key),
            "nabh_rate": data.get("nabh"),
            "non_nabh_rate": data.get("non_nabh"),
        }
        for key, data in CGHS_RATES.items()
    }
