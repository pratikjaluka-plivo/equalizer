"""
Hospital search functionality
"""
from typing import List, Optional, Dict, Any
from app.intelligence.hospital_intel import HOSPITAL_DATABASE


def search_hospitals(
        query: str,
        city: Optional[str] = None,
        state: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Search hospitals by name, city, or state"""
    results = []
    query = query.lower()

    for key, data in HOSPITAL_DATABASE.items():
        if key == "unknown":
            continue

        # Check if query matches
        if query in key or query in data.get("official_name", "").lower():
            # Filter by city/state if provided
            if city and city.lower() != data.get("city", "").lower():
                continue
            if state and state.lower() != data.get("state", "").lower():
                continue

            results.append({
                "id": key,
                "name": data.get("official_name", key),
                "city": data.get("city", ""),
                "state": data.get("state", ""),
                "type": data.get("type", "private"),
                "nabh_accredited": data.get("nabh_accredited", False),
            })

    return results
