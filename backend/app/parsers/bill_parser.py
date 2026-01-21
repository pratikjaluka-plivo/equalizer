"""
Bill Parser - Uses Claude to extract structured data from medical bills
Supports PDF and image uploads, as well as manual entry
"""
import anthropic
from pydantic import BaseModel
from typing import Optional, Dict, List
import base64
import json

from app.config import get_settings


class BillData(BaseModel):
    hospital_name: str
    hospital_city: str
    hospital_state: str
    procedure_description: str
    total_amount: float
    itemized_charges: Dict[str, float] = {}
    patient_income: Optional[float] = None
    patient_state: str = "Maharashtra"

    # Extracted fields
    procedure_codes: List[str] = []
    date_of_service: Optional[str] = None
    errors_detected: List[str] = []
    potential_overcharges: float = 0.0


BILL_PARSING_PROMPT = """You are an expert medical bill analyst for Indian healthcare.

Analyze this medical bill and extract the following information in JSON format:

{
    "hospital_name": "Name of the hospital",
    "hospital_city": "City where hospital is located",
    "hospital_state": "State where hospital is located",
    "procedure_description": "Main procedure or treatment",
    "procedure_codes": ["List of procedure codes if visible"],
    "total_amount": 00000.00,
    "date_of_service": "DD/MM/YYYY if visible",
    "itemized_charges": {
        "Category 1": 00000.00,
        "Category 2": 00000.00
    },
    "errors_detected": [
        "List any obvious billing errors, duplicate charges, or suspicious items"
    ],
    "potential_overcharges": 00000.00
}

Common billing errors to look for:
- Duplicate charges for the same service
- Unbundling (charging separately for items typically included together)
- Upcoding (charging for more expensive procedures than performed)
- Charges for services not rendered
- Inflated supply charges
- Excessive room charges
- Unnecessary tests or procedures

Be thorough and critical. Indian hospitals are known for:
- Charging inflated MRP on medicines (should be at discounted rates)
- Adding unnecessary "packages" or "kits"
- Charging for consumables that should be included
- Duplicate ICU/room charges
- Excessive surgeon/doctor fees beyond scheduled rates

Return ONLY valid JSON, no other text."""


async def parse_bill(file_contents: bytes, filename: str) -> dict:
    """
    Parse a medical bill from PDF or image using Claude
    """
    settings = get_settings()
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    # Determine file type and prepare for Claude
    if filename.lower().endswith('.pdf'):
        # For PDF, we'd need pdf2image conversion
        # For now, return error asking for image
        raise ValueError("PDF support coming soon. Please upload an image of the bill.")

    # Assume it's an image
    image_data = base64.standard_b64encode(file_contents).decode("utf-8")

    # Determine media type
    if filename.lower().endswith(('.jpg', '.jpeg')):
        media_type = "image/jpeg"
    elif filename.lower().endswith('.png'):
        media_type = "image/png"
    elif filename.lower().endswith('.webp'):
        media_type = "image/webp"
    else:
        media_type = "image/jpeg"  # Default

    # Call Claude with vision
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": BILL_PARSING_PROMPT
                    }
                ],
            }
        ],
    )

    # Parse the response
    response_text = message.content[0].text

    # Try to extract JSON from response
    try:
        # Handle case where Claude wraps JSON in markdown
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        bill_data = json.loads(response_text.strip())
        return bill_data
    except json.JSONDecodeError:
        raise ValueError(f"Could not parse bill. Claude response: {response_text}")


async def parse_bill_text(bill_text: str) -> dict:
    """
    Parse a medical bill from plain text description using Claude
    """
    settings = get_settings()
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": f"{BILL_PARSING_PROMPT}\n\nBill text:\n{bill_text}"
            }
        ],
    )

    response_text = message.content[0].text

    try:
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        bill_data = json.loads(response_text.strip())
        return bill_data
    except json.JSONDecodeError:
        raise ValueError(f"Could not parse bill. Claude response: {response_text}")
