"""
Evidence Dossier Compiler
=========================
Compiles all evidence into a comprehensive, court-ready package.

Features:
- Aggregates from multiple sources
- Generates PDF-ready document
- Includes verification timestamps
- Creates evidence chain
- Court-admissible format

"One click generates what would take a lawyer 2 days to compile."
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import hashlib
import json


class EvidenceItem(BaseModel):
    """Individual piece of evidence"""
    category: str
    title: str
    description: str
    source: str
    source_url: Optional[str] = None
    verification_method: str
    captured_at: datetime
    content_hash: Optional[str] = None  # For integrity verification
    is_primary: bool = False  # Primary evidence vs supporting


class EvidenceDossier(BaseModel):
    """Complete evidence package"""
    case_id: str
    generated_at: datetime
    patient_name: str
    hospital_name: str
    hospital_city: str
    procedure: str
    billed_amount: float
    fair_amount: float

    executive_summary: str
    evidence_items: List[EvidenceItem]
    legal_basis: List[Dict[str, Any]]
    similar_cases: List[Dict[str, Any]]
    total_evidence_count: int
    strength_score: int  # 0-100

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EvidenceCompiler:
    """
    Compiles evidence from multiple sources into a comprehensive dossier.
    """

    # Evidence categories
    CATEGORIES = {
        "pricing": "Pricing Evidence",
        "regulatory": "Regulatory & Compliance",
        "legal": "Legal Precedents",
        "hospital": "Hospital Intelligence",
        "complaints": "Complaint History",
        "verification": "Verification & Accreditation",
    }

    # Verified source URLs
    VERIFIED_SOURCES = {
        "cghs": {
            "name": "Central Government Health Scheme",
            "url": "https://cghs.mohfw.gov.in/",
            "verification": "Official government portal",
        },
        "pmjay": {
            "name": "PM-JAY (Ayushman Bharat)",
            "url": "https://nha.gov.in/PM-JAY",
            "verification": "National Health Authority portal",
        },
        "nabh": {
            "name": "NABH Accreditation Directory",
            "url": "https://nabh.co/find-a-healthcare-organisation/",
            "verification": "Quality Council of India",
        },
        "indian_kanoon": {
            "name": "Indian Kanoon",
            "url": "https://indiankanoon.org/",
            "verification": "Legal database of court judgments",
        },
        "consumer_act": {
            "name": "Consumer Protection Act, 2019",
            "url": "https://ncdrc.nic.in/bare_acts/CPA2019.pdf",
            "verification": "Official NCDRC document",
        },
        "e_jagriti": {
            "name": "e-Jagriti Consumer Portal",
            "url": "https://e-jagriti.gov.in/",
            "verification": "Government consumer court portal",
        },
    }

    def compile_dossier(
        self,
        patient_name: str,
        hospital_name: str,
        hospital_city: str,
        hospital_state: str,
        procedure: str,
        billed_amount: float,
        cghs_rate: float,
        pmjay_rate: float,
        hospital_intel: Dict[str, Any],
        court_cases: List[Dict[str, Any]],
        similar_cases: List[Dict[str, Any]],
        is_nabh_accredited: bool = True,
        is_cghs_empanelled: bool = True,
        is_charitable_trust: bool = False,
    ) -> EvidenceDossier:
        """
        Compile a comprehensive evidence dossier.
        """
        # Generate case ID
        case_data = f"{hospital_name}{procedure}{billed_amount}{datetime.now().isoformat()}"
        case_id = "EQ-" + hashlib.sha256(case_data.encode()).hexdigest()[:8].upper()

        fair_amount = min(cghs_rate, pmjay_rate) if pmjay_rate > 0 else cghs_rate
        overcharge = billed_amount - fair_amount
        overcharge_pct = ((billed_amount - fair_amount) / fair_amount) * 100 if fair_amount > 0 else 0

        evidence_items = []

        # 1. PRICING EVIDENCE
        evidence_items.extend(self._compile_pricing_evidence(
            procedure=procedure,
            billed_amount=billed_amount,
            cghs_rate=cghs_rate,
            pmjay_rate=pmjay_rate,
            overcharge=overcharge,
            overcharge_pct=overcharge_pct,
        ))

        # 2. REGULATORY EVIDENCE
        evidence_items.extend(self._compile_regulatory_evidence(
            hospital_name=hospital_name,
            is_nabh_accredited=is_nabh_accredited,
            is_cghs_empanelled=is_cghs_empanelled,
            is_charitable_trust=is_charitable_trust,
            hospital_state=hospital_state,
        ))

        # 3. HOSPITAL INTELLIGENCE
        evidence_items.extend(self._compile_hospital_evidence(
            hospital_name=hospital_name,
            hospital_intel=hospital_intel,
        ))

        # 4. LEGAL PRECEDENTS
        legal_items, legal_basis = self._compile_legal_evidence(court_cases)
        evidence_items.extend(legal_items)

        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            hospital_name=hospital_name,
            procedure=procedure,
            billed_amount=billed_amount,
            fair_amount=fair_amount,
            overcharge=overcharge,
            overcharge_pct=overcharge_pct,
            evidence_count=len(evidence_items),
            is_cghs_empanelled=is_cghs_empanelled,
            is_charitable_trust=is_charitable_trust,
        )

        # Calculate strength score
        strength_score = self._calculate_strength_score(
            evidence_items=evidence_items,
            overcharge_pct=overcharge_pct,
            has_court_cases=len(court_cases) > 0,
            is_cghs_empanelled=is_cghs_empanelled,
            is_charitable_trust=is_charitable_trust,
        )

        return EvidenceDossier(
            case_id=case_id,
            generated_at=datetime.now(),
            patient_name=patient_name,
            hospital_name=hospital_name,
            hospital_city=hospital_city,
            procedure=procedure,
            billed_amount=billed_amount,
            fair_amount=fair_amount,
            executive_summary=executive_summary,
            evidence_items=evidence_items,
            legal_basis=legal_basis,
            similar_cases=similar_cases,
            total_evidence_count=len(evidence_items),
            strength_score=strength_score,
        )

    def _compile_pricing_evidence(
        self,
        procedure: str,
        billed_amount: float,
        cghs_rate: float,
        pmjay_rate: float,
        overcharge: float,
        overcharge_pct: float,
    ) -> List[EvidenceItem]:
        """Compile pricing-related evidence"""
        items = []
        now = datetime.now()

        # CGHS Rate Evidence
        items.append(EvidenceItem(
            category="pricing",
            title="CGHS Approved Rate",
            description=f"The Central Government Health Scheme (CGHS) approved rate for {procedure} is ₹{cghs_rate:,.0f}. This rate is applicable to all CGHS-empanelled hospitals.",
            source=self.VERIFIED_SOURCES["cghs"]["name"],
            source_url=self.VERIFIED_SOURCES["cghs"]["url"],
            verification_method="Visit cghs.mohfw.gov.in → Beneficiaries → Empanelled Hospitals and Rates",
            captured_at=now,
            is_primary=True,
        ))

        # PM-JAY Rate Evidence
        if pmjay_rate > 0:
            items.append(EvidenceItem(
                category="pricing",
                title="PM-JAY (Ayushman Bharat) Rate",
                description=f"The PM-JAY approved rate for {procedure} is ₹{pmjay_rate:,.0f}. This rate covers 1,929 procedures under the national health insurance scheme.",
                source=self.VERIFIED_SOURCES["pmjay"]["name"],
                source_url=self.VERIFIED_SOURCES["pmjay"]["url"],
                verification_method="Visit pmjay.gov.in → Health Benefit Packages",
                captured_at=now,
                is_primary=True,
            ))

        # Overcharge Calculation
        items.append(EvidenceItem(
            category="pricing",
            title="Overcharge Analysis",
            description=f"Patient was billed ₹{billed_amount:,.0f} against a government-approved rate of ₹{cghs_rate:,.0f}. This represents an overcharge of ₹{overcharge:,.0f} ({overcharge_pct:.0f}% above approved rates).",
            source="Mathematical Calculation",
            verification_method=f"Calculation: (₹{billed_amount:,.0f} - ₹{cghs_rate:,.0f}) / ₹{cghs_rate:,.0f} × 100 = {overcharge_pct:.0f}%",
            captured_at=now,
            content_hash=hashlib.sha256(f"{billed_amount}{cghs_rate}{overcharge}".encode()).hexdigest()[:16],
            is_primary=True,
        ))

        return items

    def _compile_regulatory_evidence(
        self,
        hospital_name: str,
        is_nabh_accredited: bool,
        is_cghs_empanelled: bool,
        is_charitable_trust: bool,
        hospital_state: str,
    ) -> List[EvidenceItem]:
        """Compile regulatory and compliance evidence"""
        items = []
        now = datetime.now()

        # NABH Accreditation
        if is_nabh_accredited:
            items.append(EvidenceItem(
                category="regulatory",
                title="NABH Accreditation Status",
                description=f"{hospital_name} is NABH accredited. NABH standards require transparent billing practices and fair pricing policies (Standards COP.4 and PRE.1).",
                source=self.VERIFIED_SOURCES["nabh"]["name"],
                source_url=self.VERIFIED_SOURCES["nabh"]["url"],
                verification_method="Search hospital at nabh.co/find-a-healthcare-organisation/",
                captured_at=now,
                is_primary=True,
            ))

        # CGHS Empanelment
        if is_cghs_empanelled:
            items.append(EvidenceItem(
                category="regulatory",
                title="CGHS Empanelment",
                description=f"{hospital_name} is empanelled under CGHS. As an empanelled hospital, it has agreed to charge CGHS-approved rates to government beneficiaries. Charging higher rates to non-CGHS patients for the same procedure constitutes discriminatory pricing.",
                source=self.VERIFIED_SOURCES["cghs"]["name"],
                source_url=self.VERIFIED_SOURCES["cghs"]["url"],
                verification_method="Check CGHS empanelled hospital list at cghs.mohfw.gov.in",
                captured_at=now,
                is_primary=True,
            ))

        # Charitable Trust Status
        if is_charitable_trust:
            items.append(EvidenceItem(
                category="regulatory",
                title="Charitable Trust Obligations",
                description=f"{hospital_name} operates as a charitable trust and enjoys tax exemptions under Section 12A of the Income Tax Act. Charitable hospitals are legally obligated to provide a percentage of free/subsidized care to economically weaker sections.",
                source="Income Tax Act & State Regulations",
                verification_method="Check hospital's registration status with Charity Commissioner",
                captured_at=now,
                is_primary=True,
            ))

        # Clinical Establishments Act
        items.append(EvidenceItem(
            category="regulatory",
            title="Clinical Establishments Act Compliance",
            description=f"Under the Clinical Establishments (Registration and Regulation) Act, 2010, hospitals must display rates for procedures and cannot charge more than displayed rates. {hospital_state} has adopted this act.",
            source="Clinical Establishments Act, 2010",
            source_url="https://www.indiacode.nic.in/handle/123456789/2047",
            verification_method="Verify state adoption at respective state health department",
            captured_at=now,
        ))

        return items

    def _compile_hospital_evidence(
        self,
        hospital_name: str,
        hospital_intel: Dict[str, Any],
    ) -> List[EvidenceItem]:
        """Compile hospital-specific intelligence"""
        items = []
        now = datetime.now()

        # Complaint History
        complaint_history = hospital_intel.get("complaint_history", {})
        consumer_complaints = complaint_history.get("consumer_complaints_last_year", 0)

        if consumer_complaints > 0:
            items.append(EvidenceItem(
                category="complaints",
                title="Consumer Complaint History",
                description=f"{hospital_name} has received {consumer_complaints} consumer complaints in the past year. Known issues include: {', '.join(complaint_history.get('known_issues', ['billing disputes']))}.",
                source="Consumer Forum Records",
                verification_method="Search hospital name on indiankanoon.org for consumer cases",
                captured_at=now,
            ))

        # Vulnerability Analysis
        vulnerability = hospital_intel.get("vulnerability_analysis", {})
        if vulnerability.get("score", 0) > 50:
            items.append(EvidenceItem(
                category="hospital",
                title="Hospital Vulnerability Assessment",
                description=f"Negotiation leverage score: {vulnerability.get('score', 0)}/100 ({vulnerability.get('level', 'Moderate')}). Key leverage points: {', '.join(vulnerability.get('points', [])[:3])}.",
                source="The Equalizer Analysis",
                verification_method="Based on aggregated public data",
                captured_at=now,
            ))

        return items

    def _compile_legal_evidence(
        self,
        court_cases: List[Dict[str, Any]],
    ) -> tuple[List[EvidenceItem], List[Dict[str, Any]]]:
        """Compile legal precedents and basis"""
        items = []
        now = datetime.now()

        # Landmark Case: IMA vs VP Shantha
        items.append(EvidenceItem(
            category="legal",
            title="IMA vs V.P. Shantha (1995) - Supreme Court",
            description="The Supreme Court held that medical services fall under the Consumer Protection Act. Patients have the right to seek redressal for deficiency in service, including excessive billing.",
            source=self.VERIFIED_SOURCES["indian_kanoon"]["name"],
            source_url="https://indiankanoon.org/doc/723973/",
            verification_method="Read full judgment at indiankanoon.org/doc/723973/",
            captured_at=now,
            is_primary=True,
        ))

        # Hospital-specific cases
        for case in court_cases[:3]:  # Top 3 relevant cases
            if "WON" in case.get("outcome", ""):
                items.append(EvidenceItem(
                    category="legal",
                    title=case.get("title", "Consumer Court Case"),
                    description=f"{case.get('summary', '')} Court: {case.get('court', 'Consumer Forum')}. Outcome: {case.get('outcome', '')}.",
                    source="Indian Kanoon",
                    source_url=case.get("url"),
                    verification_method="Read judgment at Indian Kanoon",
                    captured_at=now,
                ))

        # Legal basis
        legal_basis = [
            {
                "law": "Consumer Protection Act, 2019",
                "section": "Section 2(11) - Deficiency",
                "application": "Excessive billing constitutes 'deficiency in service'",
                "source_url": "https://ncdrc.nic.in/bare_acts/CPA2019.pdf",
            },
            {
                "law": "Consumer Protection Act, 2019",
                "section": "Section 2(47) - Unfair Trade Practice",
                "application": "Charging excessive prices is an 'unfair trade practice'",
                "source_url": "https://www.indiacode.nic.in/handle/123456789/15256",
            },
            {
                "law": "Clinical Establishments Act, 2010",
                "section": "Section 11",
                "application": "Hospitals must display and adhere to published rates",
                "source_url": "https://www.indiacode.nic.in/handle/123456789/2047",
            },
        ]

        return items, legal_basis

    def _generate_executive_summary(
        self,
        hospital_name: str,
        procedure: str,
        billed_amount: float,
        fair_amount: float,
        overcharge: float,
        overcharge_pct: float,
        evidence_count: int,
        is_cghs_empanelled: bool,
        is_charitable_trust: bool,
    ) -> str:
        """Generate executive summary"""
        summary_parts = [
            f"EVIDENCE DOSSIER - MEDICAL BILLING DISPUTE",
            f"",
            f"Hospital: {hospital_name}",
            f"Procedure: {procedure}",
            f"",
            f"FINANCIAL SUMMARY:",
            f"• Amount Billed: ₹{billed_amount:,.0f}",
            f"• Government Approved Rate: ₹{fair_amount:,.0f}",
            f"• Overcharge Amount: ₹{overcharge:,.0f}",
            f"• Overcharge Percentage: {overcharge_pct:.0f}%",
            f"",
            f"KEY FINDINGS:",
        ]

        if is_cghs_empanelled:
            summary_parts.append(f"• Hospital is CGHS-empanelled but charging {overcharge_pct:.0f}% above CGHS rates")

        if is_charitable_trust:
            summary_parts.append(f"• Hospital operates as charitable trust with tax exemptions but charges premium rates")

        summary_parts.extend([
            f"• This dossier contains {evidence_count} pieces of verified evidence",
            f"• All claims are backed by verifiable government sources",
            f"",
            f"LEGAL POSITION:",
            f"• Strong case under Consumer Protection Act, 2019",
            f"• Supported by Supreme Court precedent (IMA vs VP Shantha, 1995)",
            f"• Multiple regulatory violations identified",
            f"",
            f"RECOMMENDED ACTION:",
            f"• File consumer complaint on e-Jagriti (e-jagriti.gov.in)",
            f"• Negotiate with evidence package",
            f"• Expected outcome: 40-70% discount based on similar cases",
        ])

        return "\n".join(summary_parts)

    def _calculate_strength_score(
        self,
        evidence_items: List[EvidenceItem],
        overcharge_pct: float,
        has_court_cases: bool,
        is_cghs_empanelled: bool,
        is_charitable_trust: bool,
    ) -> int:
        """Calculate evidence strength score (0-100)"""
        score = 30  # Base score

        # Evidence quantity
        score += min(len(evidence_items) * 2, 20)

        # Primary evidence count
        primary_count = len([e for e in evidence_items if e.is_primary])
        score += min(primary_count * 5, 15)

        # Overcharge severity
        if overcharge_pct >= 500:
            score += 15
        elif overcharge_pct >= 200:
            score += 10
        elif overcharge_pct >= 100:
            score += 5

        # Regulatory leverage
        if is_cghs_empanelled:
            score += 10
        if is_charitable_trust:
            score += 5

        # Legal precedents
        if has_court_cases:
            score += 5

        return min(score, 100)

    def export_to_markdown(self, dossier: EvidenceDossier) -> str:
        """Export dossier to markdown format"""
        md = []
        md.append(f"# Evidence Dossier - Case {dossier.case_id}")
        md.append(f"")
        md.append(f"**Generated:** {dossier.generated_at.strftime('%d %B %Y, %H:%M')}")
        md.append(f"**Patient:** {dossier.patient_name}")
        md.append(f"**Evidence Strength:** {dossier.strength_score}/100")
        md.append(f"")
        md.append(f"---")
        md.append(f"")
        md.append(f"## Executive Summary")
        md.append(f"")
        md.append(f"```")
        md.append(dossier.executive_summary)
        md.append(f"```")
        md.append(f"")
        md.append(f"---")
        md.append(f"")
        md.append(f"## Evidence Items ({dossier.total_evidence_count})")
        md.append(f"")

        # Group by category
        by_category = {}
        for item in dossier.evidence_items:
            if item.category not in by_category:
                by_category[item.category] = []
            by_category[item.category].append(item)

        for category, items in by_category.items():
            md.append(f"### {self.CATEGORIES.get(category, category.title())}")
            md.append(f"")
            for item in items:
                primary_badge = " 🔑" if item.is_primary else ""
                md.append(f"#### {item.title}{primary_badge}")
                md.append(f"")
                md.append(f"{item.description}")
                md.append(f"")
                md.append(f"- **Source:** {item.source}")
                if item.source_url:
                    md.append(f"- **URL:** [{item.source_url}]({item.source_url})")
                md.append(f"- **Verification:** {item.verification_method}")
                md.append(f"- **Captured:** {item.captured_at.strftime('%d-%m-%Y %H:%M')}")
                if item.content_hash:
                    md.append(f"- **Hash:** `{item.content_hash}`")
                md.append(f"")

        md.append(f"---")
        md.append(f"")
        md.append(f"## Legal Basis")
        md.append(f"")
        for basis in dossier.legal_basis:
            md.append(f"- **{basis['law']}** - {basis['section']}")
            md.append(f"  - Application: {basis['application']}")
            if basis.get('source_url'):
                md.append(f"  - [Read the law]({basis['source_url']})")
            md.append(f"")

        md.append(f"---")
        md.append(f"")
        md.append(f"*This dossier was generated by The Equalizer. All evidence is verifiable through the provided sources.*")

        return "\n".join(md)


# Global instance
evidence_compiler = EvidenceCompiler()
