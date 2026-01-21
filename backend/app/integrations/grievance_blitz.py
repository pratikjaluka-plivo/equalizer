"""
Multi-Portal Grievance Blitz
============================
File complaints on multiple platforms simultaneously.

Platforms:
- e-Jagriti (Consumer Court) - https://e-jagriti.gov.in/
- CPGRAMS (Central Govt) - https://pgportal.gov.in/
- RTI Online - https://rtionline.gov.in/
- State Health Department portals
- Medical Council (if doctor misconduct)
- NABH complaints
- IRDAI (if insurance involved)

"One click files complaints on ALL relevant platforms simultaneously."
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from enum import Enum


class GrievancePortal(str, Enum):
    E_JAGRITI = "e_jagriti"  # Consumer Court
    CPGRAMS = "cpgrams"  # Central Govt Grievance
    RTI_ONLINE = "rti_online"  # RTI Portal
    STATE_HEALTH = "state_health"  # State Health Dept
    MEDICAL_COUNCIL = "medical_council"  # MCI/State Medical Council
    NABH = "nabh"  # NABH Complaints
    IRDAI = "irdai"  # Insurance Ombudsman


class GrievanceFiling(BaseModel):
    """Pre-filled grievance filing for a specific portal"""
    portal: GrievancePortal
    portal_name: str
    portal_url: str
    filing_type: str
    subject: str
    body: str
    attachments_needed: List[str]
    estimated_response_time: str
    filing_fee: Optional[str] = None
    instructions: List[str]
    pre_filled_fields: Dict[str, Any]


class GrievanceBlitz:
    """
    Generates pre-filled complaint filings for multiple platforms.

    The actual filing is done by the user (or can be automated via n8n).
    This class generates all the content and instructions.
    """

    PORTAL_INFO = {
        GrievancePortal.E_JAGRITI: {
            "name": "e-Jagriti (Consumer Court)",
            "url": "https://e-jagriti.gov.in/",
            "type": "consumer_complaint",
            "response_time": "30-90 days for initial hearing",
            "fee": "Based on claim amount (₹100-₹5,000)",
        },
        GrievancePortal.CPGRAMS: {
            "name": "CPGRAMS (Central Government)",
            "url": "https://pgportal.gov.in/",
            "type": "public_grievance",
            "response_time": "30-60 days",
            "fee": "Free",
        },
        GrievancePortal.RTI_ONLINE: {
            "name": "RTI Online Portal",
            "url": "https://rtionline.gov.in/",
            "type": "information_request",
            "response_time": "30 days (legally mandated)",
            "fee": "₹10 per request",
        },
        GrievancePortal.STATE_HEALTH: {
            "name": "State Health Department",
            "url": "",  # Varies by state
            "type": "health_grievance",
            "response_time": "15-45 days",
            "fee": "Free",
        },
        GrievancePortal.MEDICAL_COUNCIL: {
            "name": "Medical Council of India / State Medical Council",
            "url": "https://www.nmc.org.in/",
            "type": "medical_misconduct",
            "response_time": "60-180 days",
            "fee": "Free",
        },
        GrievancePortal.NABH: {
            "name": "NABH Complaints",
            "url": "https://nabh.co/contact-us/",
            "type": "accreditation_complaint",
            "response_time": "30-60 days",
            "fee": "Free",
        },
        GrievancePortal.IRDAI: {
            "name": "IRDAI Insurance Ombudsman",
            "url": "https://igms.irda.gov.in/",
            "type": "insurance_complaint",
            "response_time": "30-90 days",
            "fee": "Free",
        },
    }

    STATE_HEALTH_PORTALS = {
        "Maharashtra": {
            "url": "https://arogya.maharashtra.gov.in/",
            "email": "secyph@maharashtra.gov.in",
            "grievance_url": "https://grievances.maharashtra.gov.in/",
        },
        "Delhi": {
            "url": "https://health.delhigovt.nic.in/",
            "email": "selokhswa@gmail.com",
            "grievance_url": "https://pgms.delhi.gov.in/",
        },
        "Karnataka": {
            "url": "https://karunadu.karnataka.gov.in/hfw/",
            "email": "pshfw@karnataka.gov.in",
            "grievance_url": "https://pgr.karnataka.gov.in/",
        },
        "Tamil Nadu": {
            "url": "https://www.tnhealth.tn.gov.in/",
            "email": "dghs@tn.gov.in",
            "grievance_url": "https://www.tnhealth.tn.gov.in/",
        },
        "Telangana": {
            "url": "https://health.telangana.gov.in/",
            "email": "cchs.ts@nic.in",
            "grievance_url": "https://ts.meeseva.telangana.gov.in/",
        },
    }

    def generate_blitz(
        self,
        hospital_name: str,
        hospital_city: str,
        hospital_state: str,
        procedure: str,
        billed_amount: float,
        fair_amount: float,
        patient_name: str,
        patient_address: str,
        patient_email: str,
        patient_phone: str,
        treatment_date: str,
        bill_date: str,
        has_insurance: bool = False,
        insurance_company: Optional[str] = None,
        doctor_name: Optional[str] = None,
        is_nabh_accredited: bool = True,
        additional_issues: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate pre-filled filings for all relevant portals.

        Returns a complete package with filings for each platform.
        """
        overcharge = billed_amount - fair_amount
        overcharge_pct = ((billed_amount - fair_amount) / fair_amount) * 100 if fair_amount > 0 else 0

        filings = []

        # 1. Consumer Court (e-Jagriti) - Always include
        filings.append(self._generate_consumer_court_filing(
            hospital_name=hospital_name,
            hospital_city=hospital_city,
            hospital_state=hospital_state,
            procedure=procedure,
            billed_amount=billed_amount,
            fair_amount=fair_amount,
            overcharge=overcharge,
            overcharge_pct=overcharge_pct,
            patient_name=patient_name,
            patient_address=patient_address,
            patient_email=patient_email,
            treatment_date=treatment_date,
            bill_date=bill_date,
        ))

        # 2. CPGRAMS - For central government attention
        filings.append(self._generate_cpgrams_filing(
            hospital_name=hospital_name,
            hospital_city=hospital_city,
            hospital_state=hospital_state,
            procedure=procedure,
            billed_amount=billed_amount,
            fair_amount=fair_amount,
            overcharge=overcharge,
            overcharge_pct=overcharge_pct,
            patient_name=patient_name,
        ))

        # 3. RTI Request - For transparency
        filings.append(self._generate_rti_filing(
            hospital_name=hospital_name,
            hospital_city=hospital_city,
            hospital_state=hospital_state,
            procedure=procedure,
            patient_name=patient_name,
        ))

        # 4. State Health Department - If available
        if hospital_state in self.STATE_HEALTH_PORTALS:
            filings.append(self._generate_state_health_filing(
                hospital_name=hospital_name,
                hospital_city=hospital_city,
                hospital_state=hospital_state,
                procedure=procedure,
                billed_amount=billed_amount,
                fair_amount=fair_amount,
                overcharge=overcharge,
                patient_name=patient_name,
            ))

        # 5. NABH - If hospital is accredited
        if is_nabh_accredited:
            filings.append(self._generate_nabh_filing(
                hospital_name=hospital_name,
                hospital_city=hospital_city,
                procedure=procedure,
                billed_amount=billed_amount,
                fair_amount=fair_amount,
                patient_name=patient_name,
            ))

        # 6. IRDAI - If insurance involved
        if has_insurance and insurance_company:
            filings.append(self._generate_irdai_filing(
                hospital_name=hospital_name,
                procedure=procedure,
                billed_amount=billed_amount,
                fair_amount=fair_amount,
                patient_name=patient_name,
                insurance_company=insurance_company,
            ))

        return {
            "generated_at": datetime.now().isoformat(),
            "case_summary": {
                "hospital": hospital_name,
                "city": hospital_city,
                "state": hospital_state,
                "procedure": procedure,
                "billed_amount": billed_amount,
                "fair_amount": fair_amount,
                "overcharge_amount": overcharge,
                "overcharge_percentage": round(overcharge_pct, 1),
            },
            "total_filings": len(filings),
            "filings": filings,
            "cross_reference_note": self._generate_cross_reference_note(len(filings)),
            "recommended_sequence": [
                "1. File on e-Jagriti first (strongest legal standing)",
                "2. File RTI request (forces disclosure within 30 days)",
                "3. File on CPGRAMS (gets central government attention)",
                "4. File with State Health Department (local pressure)",
                "5. File NABH complaint if accredited (accreditation at risk)",
                "6. File IRDAI if insurance involved",
            ],
        }

    def _generate_consumer_court_filing(self, **kwargs) -> GrievanceFiling:
        """Generate e-Jagriti consumer court complaint"""
        subject = f"Consumer Complaint: Excessive Medical Billing by {kwargs['hospital_name']}"

        body = f"""
CONSUMER COMPLAINT UNDER CONSUMER PROTECTION ACT, 2019

COMPLAINANT:
Name: {kwargs['patient_name']}
Address: {kwargs['patient_address']}
Email: {kwargs['patient_email']}

OPPOSITE PARTY:
Name: {kwargs['hospital_name']}
Address: {kwargs['hospital_city']}, {kwargs['hospital_state']}

FACTS OF THE CASE:

1. The Complainant availed medical services at {kwargs['hospital_name']} for {kwargs['procedure']} on {kwargs['treatment_date']}.

2. The Opposite Party raised a bill of ₹{kwargs['billed_amount']:,.0f} for the said procedure.

3. The Central Government Health Scheme (CGHS) approved rate for this procedure is ₹{kwargs['fair_amount']:,.0f}.

4. The Complainant has been overcharged by ₹{kwargs['overcharge']:,.0f} ({kwargs['overcharge_pct']:.0f}% above government-approved rates).

5. This constitutes:
   a) Deficiency in Service under Section 2(11) of the Consumer Protection Act, 2019
   b) Unfair Trade Practice under Section 2(47) of the Consumer Protection Act, 2019

LEGAL BASIS:

1. Indian Medical Association vs V.P. Shantha (1995) - Supreme Court held that medical services fall under Consumer Protection Act.

2. Consumer Protection Act, 2019 - Section 2(47) defines charging excessive prices as unfair trade practice.

3. Clinical Establishments Act, 2010 - Mandates display of rates and charges.

RELIEF SOUGHT:

1. Refund of excess amount: ₹{kwargs['overcharge']:,.0f}
2. Compensation for mental agony and harassment: ₹50,000
3. Cost of litigation: ₹10,000
4. Direction to the Opposite Party to charge only government-approved rates

VERIFICATION:

I, {kwargs['patient_name']}, do hereby verify that the contents of this complaint are true to the best of my knowledge and belief.

Date: {datetime.now().strftime('%d-%m-%Y')}
Place: {kwargs['hospital_city']}
""".strip()

        return GrievanceFiling(
            portal=GrievancePortal.E_JAGRITI,
            portal_name=self.PORTAL_INFO[GrievancePortal.E_JAGRITI]["name"],
            portal_url=self.PORTAL_INFO[GrievancePortal.E_JAGRITI]["url"],
            filing_type="Consumer Complaint",
            subject=subject,
            body=body,
            attachments_needed=[
                "Copy of hospital bill (original)",
                "Copy of CGHS rate list showing approved rates",
                "Discharge summary",
                "Payment receipts",
                "ID proof (Aadhaar/PAN)",
                "Address proof",
            ],
            estimated_response_time=self.PORTAL_INFO[GrievancePortal.E_JAGRITI]["response_time"],
            filing_fee=self.PORTAL_INFO[GrievancePortal.E_JAGRITI]["fee"],
            instructions=[
                "Visit https://e-jagriti.gov.in/ and create an account",
                "Select 'File New Case' → 'Consumer Complaint'",
                "Choose appropriate District/State Commission based on claim amount",
                "Up to ₹1 Crore: District Consumer Forum",
                "₹1 Crore to ₹10 Crore: State Consumer Commission",
                "Copy-paste the complaint text above",
                "Upload all attachments as PDF",
                "Pay the required fee online",
                "Note down the case number for tracking",
            ],
            pre_filled_fields={
                "complaint_type": "Deficiency in Service",
                "opposite_party_type": "Hospital/Healthcare Provider",
                "claim_amount": kwargs['overcharge'] + 60000,  # Overcharge + compensation
                "jurisdiction": "District Forum" if kwargs['billed_amount'] < 10000000 else "State Commission",
            },
        )

    def _generate_cpgrams_filing(self, **kwargs) -> GrievanceFiling:
        """Generate CPGRAMS public grievance"""
        subject = f"Grievance: Excessive Medical Billing at {kwargs['hospital_name']}, {kwargs['hospital_city']}"

        body = f"""
PUBLIC GRIEVANCE REGARDING EXCESSIVE MEDICAL CHARGES

To,
The Secretary,
Ministry of Health and Family Welfare,
Government of India

Subject: Complaint against excessive billing by {kwargs['hospital_name']}, {kwargs['hospital_city']}

Respected Sir/Madam,

I, {kwargs['patient_name']}, wish to bring to your notice the excessive billing practices at {kwargs['hospital_name']}.

DETAILS:
- Hospital: {kwargs['hospital_name']}, {kwargs['hospital_city']}, {kwargs['hospital_state']}
- Procedure: {kwargs['procedure']}
- Amount Billed: ₹{kwargs['billed_amount']:,.0f}
- CGHS Approved Rate: ₹{kwargs['fair_amount']:,.0f}
- Overcharge: ₹{kwargs['overcharge']:,.0f} ({kwargs['overcharge_pct']:.0f}%)

This hospital is charging {kwargs['overcharge_pct']:.0f}% MORE than government-approved CGHS rates for the same procedure.

REQUEST:
1. Investigate the billing practices of this hospital
2. Issue guidelines to prevent such overcharging
3. Take action under relevant healthcare regulations
4. Ensure compliance with Clinical Establishments Act

This grievance has also been filed with the Consumer Court (e-Jagriti) and State Health Department for comprehensive action.

Thanking you,
{kwargs['patient_name']}
""".strip()

        return GrievanceFiling(
            portal=GrievancePortal.CPGRAMS,
            portal_name=self.PORTAL_INFO[GrievancePortal.CPGRAMS]["name"],
            portal_url=self.PORTAL_INFO[GrievancePortal.CPGRAMS]["url"],
            filing_type="Public Grievance",
            subject=subject,
            body=body,
            attachments_needed=[
                "Copy of hospital bill",
                "CGHS rate reference",
            ],
            estimated_response_time=self.PORTAL_INFO[GrievancePortal.CPGRAMS]["response_time"],
            filing_fee=self.PORTAL_INFO[GrievancePortal.CPGRAMS]["fee"],
            instructions=[
                "Visit https://pgportal.gov.in/",
                "Register/Login with your mobile number",
                "Select Ministry: 'Ministry of Health and Family Welfare'",
                "Category: 'Hospital Related'",
                "Copy-paste the grievance text",
                "Upload bill copy as attachment",
                "Submit and note the registration number",
            ],
            pre_filled_fields={
                "ministry": "Ministry of Health and Family Welfare",
                "category": "Hospital/Healthcare",
                "sub_category": "Overcharging/Billing Issues",
            },
        )

    def _generate_rti_filing(self, **kwargs) -> GrievanceFiling:
        """Generate RTI request"""
        subject = f"RTI Application - Hospital Rates and Empanelment Details"

        body = f"""
RIGHT TO INFORMATION APPLICATION

To,
The Public Information Officer,
Ministry of Health and Family Welfare / CGHS
Government of India

Subject: Information regarding {kwargs['hospital_name']}, {kwargs['hospital_city']}

Sir/Madam,

Under the Right to Information Act, 2005, I request the following information:

1. Is {kwargs['hospital_name']}, {kwargs['hospital_city']} empanelled under CGHS? If yes, please provide:
   a) Date of empanelment
   b) Categories of empanelment
   c) Current empanelment status

2. What are the CGHS-approved rates for {kwargs['procedure']} at NABH-accredited hospitals?

3. Is {kwargs['hospital_name']} empanelled under Ayushman Bharat (PM-JAY)? If yes, please provide the approved package rates.

4. What is the process to file a complaint against a hospital charging above CGHS rates?

5. How many complaints have been received against {kwargs['hospital_name']} in the past 2 years regarding billing issues?

6. What action has been taken on such complaints?

I am willing to pay the prescribed fee for this information.

Applicant Details:
Name: {kwargs['patient_name']}
Address: [Your Address]
Phone: [Your Phone]

Date: {datetime.now().strftime('%d-%m-%Y')}
""".strip()

        return GrievanceFiling(
            portal=GrievancePortal.RTI_ONLINE,
            portal_name=self.PORTAL_INFO[GrievancePortal.RTI_ONLINE]["name"],
            portal_url=self.PORTAL_INFO[GrievancePortal.RTI_ONLINE]["url"],
            filing_type="RTI Application",
            subject=subject,
            body=body,
            attachments_needed=[],  # RTI doesn't require attachments
            estimated_response_time=self.PORTAL_INFO[GrievancePortal.RTI_ONLINE]["response_time"],
            filing_fee=self.PORTAL_INFO[GrievancePortal.RTI_ONLINE]["fee"],
            instructions=[
                "Visit https://rtionline.gov.in/",
                "Register with your email and mobile",
                "Select Ministry: 'Ministry of Health and Family Welfare'",
                "Copy-paste the RTI application text",
                "Pay ₹10 fee online",
                "Download acknowledgment",
                "Response is legally mandated within 30 days",
            ],
            pre_filled_fields={
                "ministry": "Ministry of Health and Family Welfare",
                "pio_designation": "CPIO, CGHS",
            },
        )

    def _generate_state_health_filing(self, **kwargs) -> GrievanceFiling:
        """Generate state health department grievance"""
        state_info = self.STATE_HEALTH_PORTALS.get(kwargs['hospital_state'], {})

        subject = f"Complaint: Excessive Billing at {kwargs['hospital_name']}"

        body = f"""
GRIEVANCE TO STATE HEALTH DEPARTMENT

To,
The Director of Health Services,
{kwargs['hospital_state']}

Subject: Complaint regarding excessive medical billing at {kwargs['hospital_name']}

Sir/Madam,

I wish to bring to your notice the excessive billing practices at a hospital in your jurisdiction.

HOSPITAL DETAILS:
Name: {kwargs['hospital_name']}
Location: {kwargs['hospital_city']}, {kwargs['hospital_state']}

COMPLAINT:
- Procedure: {kwargs['procedure']}
- Amount Charged: ₹{kwargs['billed_amount']:,.0f}
- Government Approved Rate: ₹{kwargs['fair_amount']:,.0f}
- Excess Charged: ₹{kwargs['overcharge']:,.0f}

This is a violation of:
1. {kwargs['hospital_state']} Clinical Establishments Act (if applicable)
2. State Healthcare pricing regulations
3. Consumer rights

REQUEST:
1. Investigate the hospital's billing practices
2. Issue appropriate directions under state healthcare laws
3. Ensure compliance with pricing regulations

Complainant: {kwargs['patient_name']}
Date: {datetime.now().strftime('%d-%m-%Y')}
""".strip()

        return GrievanceFiling(
            portal=GrievancePortal.STATE_HEALTH,
            portal_name=f"{kwargs['hospital_state']} Health Department",
            portal_url=state_info.get("grievance_url", state_info.get("url", "")),
            filing_type="Health Department Grievance",
            subject=subject,
            body=body,
            attachments_needed=[
                "Copy of hospital bill",
                "Discharge summary",
            ],
            estimated_response_time=self.PORTAL_INFO[GrievancePortal.STATE_HEALTH]["response_time"],
            filing_fee=self.PORTAL_INFO[GrievancePortal.STATE_HEALTH]["fee"],
            instructions=[
                f"Visit the {kwargs['hospital_state']} grievance portal",
                "Or email directly to: " + state_info.get("email", "[State Health Dept Email]"),
                "Attach hospital bill and this complaint",
                "Follow up after 15 days if no response",
            ],
            pre_filled_fields={
                "state": kwargs['hospital_state'],
                "district": kwargs['hospital_city'],
                "complaint_type": "Hospital Billing",
            },
        )

    def _generate_nabh_filing(self, **kwargs) -> GrievanceFiling:
        """Generate NABH complaint"""
        subject = f"Complaint Against NABH Accredited Hospital - {kwargs['hospital_name']}"

        body = f"""
COMPLAINT TO NATIONAL ACCREDITATION BOARD FOR HOSPITALS

To,
The CEO,
National Accreditation Board for Hospitals & Healthcare Providers (NABH),
Quality Council of India

Subject: Complaint against {kwargs['hospital_name']} - Violation of NABH Standards

Sir/Madam,

I wish to file a complaint against the following NABH-accredited hospital:

HOSPITAL: {kwargs['hospital_name']}, {kwargs['hospital_city']}

COMPLAINT:
The hospital has charged ₹{kwargs['billed_amount']:,.0f} for {kwargs['procedure']}, which is significantly higher than:
- CGHS approved rate: ₹{kwargs['fair_amount']:,.0f}
- Overcharge: {((kwargs['billed_amount'] - kwargs['fair_amount']) / kwargs['fair_amount'] * 100):.0f}%

This violates NABH standards regarding:
1. Transparent billing practices
2. Fair pricing policies
3. Patient rights

NABH Standard Reference:
- COP.4: The organization has a documented policy on pricing
- PRE.1: Patient rights include right to information about charges

REQUEST:
1. Investigate this billing practice
2. Consider impact on accreditation status
3. Issue advisory to the hospital

Patient: {kwargs['patient_name']}
Date: {datetime.now().strftime('%d-%m-%Y')}
""".strip()

        return GrievanceFiling(
            portal=GrievancePortal.NABH,
            portal_name=self.PORTAL_INFO[GrievancePortal.NABH]["name"],
            portal_url=self.PORTAL_INFO[GrievancePortal.NABH]["url"],
            filing_type="Accreditation Complaint",
            subject=subject,
            body=body,
            attachments_needed=[
                "Copy of hospital bill",
                "CGHS rate reference",
            ],
            estimated_response_time=self.PORTAL_INFO[GrievancePortal.NABH]["response_time"],
            filing_fee=self.PORTAL_INFO[GrievancePortal.NABH]["fee"],
            instructions=[
                "Email to: nabh@qcin.org",
                "Or use contact form at https://nabh.co/contact-us/",
                "Include hospital's NABH accreditation number if known",
                "Request formal investigation",
            ],
            pre_filled_fields={
                "accredited_hospital": kwargs['hospital_name'],
                "complaint_category": "Billing Transparency",
            },
        )

    def _generate_irdai_filing(self, **kwargs) -> GrievanceFiling:
        """Generate IRDAI insurance ombudsman complaint"""
        subject = f"Insurance Complaint - {kwargs['insurance_company']} - Balance Billing Issue"

        body = f"""
COMPLAINT TO INSURANCE OMBUDSMAN

To,
The Insurance Ombudsman,
[Relevant Jurisdiction]

Subject: Complaint against {kwargs['insurance_company']} regarding balance billing

Sir/Madam,

COMPLAINANT: {kwargs['patient_name']}
INSURANCE COMPANY: {kwargs['insurance_company']}

COMPLAINT:
1. I was treated at {kwargs['hospital_name']} for {kwargs['procedure']}.
2. Hospital billed: ₹{kwargs['billed_amount']:,.0f}
3. Insurance company settled significantly lower amount.
4. I am being asked to pay the balance despite the charges being excessive.

ISSUE:
The hospital is charging {((kwargs['billed_amount'] - kwargs['fair_amount']) / kwargs['fair_amount'] * 100):.0f}% above government-approved CGHS rates. The insurance company should:
1. Negotiate reasonable rates with network hospitals
2. Not allow balance billing beyond reasonable limits
3. Protect policyholders from excessive charges

RELIEF SOUGHT:
1. Insurance company to settle the full reasonable amount
2. Protection from excessive balance billing
3. Investigation into hospital's network agreement compliance

Date: {datetime.now().strftime('%d-%m-%Y')}
""".strip()

        return GrievanceFiling(
            portal=GrievancePortal.IRDAI,
            portal_name=self.PORTAL_INFO[GrievancePortal.IRDAI]["name"],
            portal_url=self.PORTAL_INFO[GrievancePortal.IRDAI]["url"],
            filing_type="Insurance Ombudsman Complaint",
            subject=subject,
            body=body,
            attachments_needed=[
                "Insurance policy copy",
                "Hospital bill",
                "Claim settlement letter",
                "Discharge summary",
            ],
            estimated_response_time=self.PORTAL_INFO[GrievancePortal.IRDAI]["response_time"],
            filing_fee=self.PORTAL_INFO[GrievancePortal.IRDAI]["fee"],
            instructions=[
                "Visit https://igms.irda.gov.in/",
                "Register and file grievance",
                "Or email to complaints@irdai.gov.in",
                "Include policy number and claim reference",
            ],
            pre_filled_fields={
                "insurance_company": kwargs['insurance_company'],
                "complaint_type": "Claim Related - Balance Billing",
            },
        )

    def _generate_cross_reference_note(self, num_filings: int) -> str:
        """Generate a note to include in each filing referencing others"""
        return f"""
NOTE: This complaint has been simultaneously filed with {num_filings} regulatory bodies including:
- Consumer Court (e-Jagriti)
- CPGRAMS (Central Government)
- RTI Online Portal
- State Health Department
- NABH (if applicable)

All complaints reference each other for coordinated action against excessive medical billing practices.
This multi-platform approach ensures comprehensive regulatory oversight and increases the likelihood of resolution.
""".strip()


# Global instance
grievance_blitz = GrievanceBlitz()
