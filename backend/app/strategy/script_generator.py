"""
Script Generator - Uses Claude to generate personalized negotiation scripts
Emails, phone scripts, complaint letters, social media posts
"""
import anthropic
from typing import Dict, Any
import json

from app.config import get_settings
from app.parsers.bill_parser import BillData


SCRIPT_GENERATION_PROMPT = """You are an expert medical bill negotiator in India. Generate professional, assertive negotiation scripts.

CONTEXT:
- Hospital: {hospital_name}, {hospital_city}
- Procedure: {procedure_description}
- Billed Amount: ₹{billed_amount:,.0f}
- CGHS Rate: ₹{cghs_rate:,.0f}
- Overcharge: {overcharge_percentage:.0f}%
- Hospital Type: {hospital_type}
- NABH Accredited: {nabh_status}
- CGHS Empanelled: {cghs_empanelled}

KEY LEVERAGE POINTS:
{leverage_points}

PATIENT STATE: {patient_state}

Generate the following scripts in JSON format:

{{
    "email_to_billing": {{
        "subject": "Subject line",
        "body": "Full email body with proper formatting. Be professional but firm. Reference specific laws and rates."
    }},
    "email_to_administrator": {{
        "subject": "Subject line for escalation",
        "body": "Escalation email to hospital administrator/CEO. More assertive, reference regulatory bodies."
    }},
    "phone_script": {{
        "opening": "How to open the call",
        "key_points": ["Point 1", "Point 2", "Point 3"],
        "responses_to_pushback": {{
            "We don't offer discounts": "Your response",
            "This is our standard rate": "Your response",
            "You signed the consent form": "Your response"
        }},
        "closing": "How to close the call"
    }},
    "consumer_complaint_draft": {{
        "forum": "Which forum to file in",
        "subject": "Complaint subject",
        "key_allegations": ["Allegation 1", "Allegation 2"],
        "relief_sought": ["Relief 1", "Relief 2"],
        "legal_sections": ["Relevant sections of CPA 2019"]
    }},
    "social_media_post": {{
        "platform": "Twitter/X",
        "post": "The post content (thread format if needed). Professional but attention-grabbing. Tag relevant handles."
    }}
}}

IMPORTANT GUIDELINES:
1. Be professional and factual, not emotional or threatening
2. Reference specific laws: Consumer Protection Act 2019, Clinical Establishments Act
3. Quote exact figures (CGHS rates, overcharge amounts)
4. For charitable trusts, reference their tax-exempt obligations
5. Mention NABH standards if applicable
6. Include specific deadlines in emails (7-14 days)
7. Reference the hospital's complaint history if significant
8. For Delhi hospitals, cite 25% EWS quota mandate
9. Always request written confirmation of any settlement

Return ONLY valid JSON."""


async def generate_scripts(
        bill_data: BillData,
        price_comparison: Dict[str, Any],
        hospital_intel: Dict[str, Any],
        leverage_points: Dict[str, Any],
        strategy: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate personalized negotiation scripts using Claude
    """
    settings = get_settings()

    # Format leverage points for the prompt
    leverage_text = "\n".join([
        f"- {point['title']}: {point['detail']}"
        for point in leverage_points.get("top_3", [])
    ])

    # Build the prompt
    prompt = SCRIPT_GENERATION_PROMPT.format(
        hospital_name=hospital_intel.get("hospital_profile", {}).get("name", bill_data.hospital_name),
        hospital_city=bill_data.hospital_city,
        procedure_description=bill_data.procedure_description,
        billed_amount=bill_data.total_amount,
        cghs_rate=price_comparison.get("cghs_rate_nabh", 0),
        overcharge_percentage=price_comparison.get("overcharge_percentage", 0),
        hospital_type=hospital_intel.get("hospital_profile", {}).get("type", "private"),
        nabh_status="Yes" if hospital_intel.get("accreditation", {}).get("nabh_accredited") else "No",
        cghs_empanelled="Yes" if hospital_intel.get("accreditation", {}).get("cghs_empanelled") else "No",
        leverage_points=leverage_text,
        patient_state=bill_data.patient_state,
    )

    # If no API key, return template scripts
    if not settings.anthropic_api_key:
        return _get_template_scripts(bill_data, price_comparison, hospital_intel, leverage_points)

    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )

        response_text = message.content[0].text

        # Parse JSON response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        scripts = json.loads(response_text.strip())
        return scripts

    except Exception as e:
        # Fallback to template scripts
        print(f"Script generation error: {e}")
        return _get_template_scripts(bill_data, price_comparison, hospital_intel, leverage_points)


def _get_template_scripts(
        bill_data: BillData,
        price_comparison: Dict[str, Any],
        hospital_intel: Dict[str, Any],
        leverage_points: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Template scripts when Claude API is not available
    """
    hospital_name = hospital_intel.get("hospital_profile", {}).get("name", bill_data.hospital_name)
    cghs_rate = price_comparison.get("cghs_rate_nabh", 0)
    overcharge = price_comparison.get("overcharge_percentage", 0)

    return {
        "email_to_billing": {
            "subject": f"Formal Dispute of Bill Amount - {bill_data.procedure_description}",
            "body": f"""Dear Sir/Madam,

I am writing to formally dispute the bill of ₹{bill_data.total_amount:,.0f} for {bill_data.procedure_description} at {hospital_name}.

Upon review, I find this amount to be significantly higher than standard rates:
- CGHS Rate for this procedure: ₹{cghs_rate:,.0f}
- Your bill: ₹{bill_data.total_amount:,.0f}
- Overcharge: {overcharge:.0f}%

I note that your hospital is CGHS empanelled and accepts government rates for the same procedures. I request that you:

1. Provide a fully itemized bill with breakdown of all charges
2. Justify any charges exceeding CGHS rates
3. Revise the bill to a fair amount in line with government rates

I am prepared to pay ₹{price_comparison.get('target_realistic', 0):,.0f} to settle this matter immediately.

Please respond within 7 working days. Failing a satisfactory resolution, I will be compelled to:
- File a complaint with the Consumer Forum under the Consumer Protection Act, 2019
- Report the matter to the {bill_data.patient_state} State Medical Council
- Approach the media regarding predatory hospital billing practices

I trust we can resolve this amicably.

Regards,
[Your Name]
[Your Contact]"""
        },

        "email_to_administrator": {
            "subject": f"URGENT: Billing Dispute Escalation - Seeking CEO/Administrator Intervention",
            "body": f"""Dear Hospital Administrator,

I am escalating a billing dispute that remains unresolved with your billing department.

FACTS:
- Procedure: {bill_data.procedure_description}
- Billed: ₹{bill_data.total_amount:,.0f}
- CGHS Rate: ₹{cghs_rate:,.0f}
- Overcharge: {overcharge:.0f}%

Your billing department has been unresponsive to my request for justification of these charges.

I am aware that {hospital_name} has received {hospital_intel.get('complaint_history', {}).get('consumer_complaints_last_year', 'multiple')} consumer complaints this year. I would prefer not to add to this number.

I am requesting your personal intervention to:
1. Review my case with fresh eyes
2. Approve a settlement at ₹{price_comparison.get('target_realistic', 0):,.0f}

If I do not hear from you within 5 working days, I will proceed with:
- Consumer Court filing under CPA 2019
- NABH complaint for violation of patient billing standards
- State Health Department complaint
- Media outreach

I believe resolution is in both our interests.

Regards,
[Your Name]"""
        },

        "phone_script": {
            "opening": f"Hello, I'm calling about my bill for {bill_data.procedure_description}. I need to speak with a supervisor about the charges.",
            "key_points": [
                f"I've been billed ₹{bill_data.total_amount:,.0f} but the CGHS rate is only ₹{cghs_rate:,.0f}",
                "I know you're CGHS empanelled and accept these rates for government employees",
                f"I'm prepared to pay ₹{price_comparison.get('target_realistic', 0):,.0f} today to settle this"
            ],
            "responses_to_pushback": {
                "We don't offer discounts": "I'm not asking for a discount. I'm asking for fair pricing. Your CGHS rates prove you can operate profitably at these prices.",
                "This is our standard rate": "Your 'standard rate' is {overcharge:.0f}% above government-mandated rates. I've documented everything and am prepared to escalate.",
                "You signed the consent form": "Consent for treatment is not consent for overcharging. The Consumer Protection Act specifically covers unfair pricing in medical services."
            },
            "closing": "I need a supervisor to approve this settlement today. If we can't resolve this, my next call is to the Consumer Forum."
        },

        "consumer_complaint_draft": {
            "forum": f"District Consumer Disputes Redressal Forum, {bill_data.hospital_city}" if bill_data.total_amount < 10000000 else "State Consumer Disputes Redressal Commission",
            "subject": f"Complaint Against {hospital_name} for Unfair Trade Practices and Excessive Charging",
            "key_allegations": [
                f"Charging ₹{bill_data.total_amount:,.0f} for a procedure that costs ₹{cghs_rate:,.0f} under CGHS - an overcharge of {overcharge:.0f}%",
                "Failure to provide transparent, itemized billing as required under law",
                "Unfair trade practice under Section 2(47) of Consumer Protection Act, 2019"
            ],
            "relief_sought": [
                f"Refund of excess amount: ₹{bill_data.total_amount - cghs_rate:,.0f}",
                "Compensation for mental harassment: ₹50,000",
                "Cost of litigation"
            ],
            "legal_sections": [
                "Consumer Protection Act, 2019 - Section 2(42) (Service), Section 2(47) (Unfair Trade Practice)",
                "Clinical Establishments Act, 2010 - Display of rates",
                "Indian Medical Council Regulations - Professional Conduct"
            ]
        },

        "social_media_post": {
            "platform": "Twitter/X",
            "post": f"""🚨 THREAD: How {hospital_name} charged me ₹{bill_data.total_amount:,.0f} for a procedure that costs ₹{cghs_rate:,.0f} under government rates

1/ I went to {hospital_name} for {bill_data.procedure_description}. The bill? ₹{bill_data.total_amount:,.0f}. That's {overcharge:.0f}% ABOVE what the government pays for the SAME procedure.

2/ This hospital is CGHS empanelled. They accept ₹{cghs_rate:,.0f} from government employees. But they charged me {overcharge:.0f}% more. Same doctors. Same procedure. Different price.

3/ When I asked for an itemized bill, they [describe response].

4/ Indian hospitals operate with ZERO price transparency. There are no standard rates. They charge whatever they think you'll pay.

5/ I've filed a Consumer Court complaint. I'll update you on the outcome.

If you've faced similar issues, reply below. Let's document this.

@MoaborHealth @ABORIMSA @consabormer
#MedicalBilling #HealthcareIndia #ConsumerRights"""
        }
    }
