"""
Auto-Escalation Pipeline
========================
A fully automated escalation system that applies pressure over time.

Flow:
Day 0:  Patient submits bill → Analysis generated
Day 1:  Auto-send email to hospital billing
Day 3:  No response? → Escalate to hospital administrator
Day 5:  No response? → Send to hospital grievance cell
Day 7:  No response? → File on e-Jagriti (consumer court)
Day 10: Auto-generate RTI request
Day 14: File on CPGRAMS (central govt grievance)
Day 21: Alert matched journalists
Day 30: Auto-post to social media

This module provides the orchestration layer - actual execution happens via n8n or similar.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel
import json
import hashlib


class EscalationStage(str, Enum):
    SUBMITTED = "submitted"
    EMAIL_BILLING = "email_billing"
    EMAIL_ADMIN = "email_admin"
    GRIEVANCE_CELL = "grievance_cell"
    CONSUMER_COURT = "consumer_court"
    RTI_FILED = "rti_filed"
    CPGRAMS = "cpgrams"
    MEDIA_ALERT = "media_alert"
    SOCIAL_MEDIA = "social_media"
    RESOLVED = "resolved"
    PAUSED = "paused"


class EscalationAction(BaseModel):
    """Represents a scheduled escalation action"""
    stage: EscalationStage
    scheduled_date: datetime
    executed: bool = False
    executed_date: Optional[datetime] = None
    response_received: bool = False
    response_date: Optional[datetime] = None
    response_content: Optional[str] = None
    skip_reason: Optional[str] = None


class EscalationState(BaseModel):
    """Complete state of an escalation case"""
    case_id: str
    created_at: datetime
    hospital_name: str
    hospital_city: str
    hospital_email: Optional[str] = None
    procedure: str
    billed_amount: float
    fair_amount: float
    overcharge_percentage: float
    patient_name: Optional[str] = None
    patient_email: Optional[str] = None
    patient_phone: Optional[str] = None

    current_stage: EscalationStage = EscalationStage.SUBMITTED
    actions: List[EscalationAction] = []

    # Tracking
    total_responses: int = 0
    last_response_date: Optional[datetime] = None
    settlement_offered: Optional[float] = None
    settlement_accepted: bool = False

    # Status flags
    is_active: bool = True
    pause_reason: Optional[str] = None

    class Config:
        use_enum_values = True


class EscalationPipeline:
    """
    Orchestrates the auto-escalation workflow.

    This class generates the escalation schedule and tracks state.
    Actual execution of actions (sending emails, filing complaints)
    is handled by external workflow engines (n8n, Temporal, etc.)
    """

    # Escalation timeline (days from start)
    TIMELINE = {
        EscalationStage.EMAIL_BILLING: 1,
        EscalationStage.EMAIL_ADMIN: 3,
        EscalationStage.GRIEVANCE_CELL: 5,
        EscalationStage.CONSUMER_COURT: 7,
        EscalationStage.RTI_FILED: 10,
        EscalationStage.CPGRAMS: 14,
        EscalationStage.MEDIA_ALERT: 21,
        EscalationStage.SOCIAL_MEDIA: 30,
    }

    # Portal URLs for each stage
    PORTAL_URLS = {
        EscalationStage.CONSUMER_COURT: "https://e-jagriti.gov.in/",
        EscalationStage.RTI_FILED: "https://rtionline.gov.in/",
        EscalationStage.CPGRAMS: "https://pgportal.gov.in/",
    }

    def __init__(self):
        self.cases: Dict[str, EscalationState] = {}

    def create_case(
        self,
        hospital_name: str,
        hospital_city: str,
        procedure: str,
        billed_amount: float,
        fair_amount: float,
        patient_email: Optional[str] = None,
        patient_name: Optional[str] = None,
        hospital_email: Optional[str] = None,
    ) -> EscalationState:
        """Create a new escalation case with scheduled actions"""

        # Generate unique case ID
        case_data = f"{hospital_name}{procedure}{billed_amount}{datetime.now().isoformat()}"
        case_id = hashlib.sha256(case_data.encode()).hexdigest()[:12].upper()

        overcharge_pct = ((billed_amount - fair_amount) / fair_amount) * 100 if fair_amount > 0 else 0

        # Create initial state
        state = EscalationState(
            case_id=case_id,
            created_at=datetime.now(),
            hospital_name=hospital_name,
            hospital_city=hospital_city,
            hospital_email=hospital_email,
            procedure=procedure,
            billed_amount=billed_amount,
            fair_amount=fair_amount,
            overcharge_percentage=round(overcharge_pct, 1),
            patient_name=patient_name,
            patient_email=patient_email,
        )

        # Schedule all escalation actions
        state.actions = self._generate_schedule(state.created_at)

        self.cases[case_id] = state
        return state

    def _generate_schedule(self, start_date: datetime) -> List[EscalationAction]:
        """Generate the escalation schedule"""
        actions = []
        for stage, days in self.TIMELINE.items():
            actions.append(EscalationAction(
                stage=stage,
                scheduled_date=start_date + timedelta(days=days),
            ))
        return actions

    def get_pending_actions(self, case_id: str) -> List[Dict[str, Any]]:
        """Get actions that are due for execution"""
        if case_id not in self.cases:
            return []

        state = self.cases[case_id]
        if not state.is_active:
            return []

        now = datetime.now()
        pending = []

        for action in state.actions:
            if not action.executed and action.scheduled_date <= now:
                # Check if previous action got a response
                should_execute = True
                if action.response_received:
                    should_execute = False  # Got response, skip further escalation

                if should_execute:
                    pending.append({
                        "case_id": case_id,
                        "stage": action.stage,
                        "scheduled_date": action.scheduled_date.isoformat(),
                        "action_details": self._get_action_details(state, action.stage),
                    })

        return pending

    def _get_action_details(self, state: EscalationState, stage: EscalationStage) -> Dict[str, Any]:
        """Get specific details for executing an action"""

        base_details = {
            "hospital_name": state.hospital_name,
            "hospital_city": state.hospital_city,
            "procedure": state.procedure,
            "billed_amount": state.billed_amount,
            "fair_amount": state.fair_amount,
            "overcharge_percentage": state.overcharge_percentage,
            "case_id": state.case_id,
        }

        if stage == EscalationStage.EMAIL_BILLING:
            return {
                **base_details,
                "action": "send_email",
                "recipient_type": "billing_department",
                "subject": f"Billing Dispute - Case #{state.case_id}",
                "template": "billing_dispute_initial",
            }

        elif stage == EscalationStage.EMAIL_ADMIN:
            return {
                **base_details,
                "action": "send_email",
                "recipient_type": "hospital_administrator",
                "subject": f"ESCALATED: Billing Dispute - Case #{state.case_id}",
                "template": "billing_dispute_escalation",
                "note": "No response from billing department after 48 hours",
            }

        elif stage == EscalationStage.GRIEVANCE_CELL:
            return {
                **base_details,
                "action": "send_email",
                "recipient_type": "grievance_cell",
                "subject": f"Formal Grievance: Excessive Medical Billing - Case #{state.case_id}",
                "template": "formal_grievance",
            }

        elif stage == EscalationStage.CONSUMER_COURT:
            return {
                **base_details,
                "action": "generate_filing",
                "portal": "e-Jagriti",
                "portal_url": self.PORTAL_URLS[stage],
                "filing_type": "consumer_complaint",
                "template": "consumer_court_complaint",
            }

        elif stage == EscalationStage.RTI_FILED:
            return {
                **base_details,
                "action": "generate_filing",
                "portal": "RTI Online",
                "portal_url": self.PORTAL_URLS[stage],
                "filing_type": "rti_request",
                "template": "rti_hospital_rates",
                "questions": [
                    f"What are the CGHS-approved rates for {state.procedure} at {state.hospital_name}?",
                    f"Is {state.hospital_name} empanelled under CGHS/PMJAY? If yes, provide empanelment details.",
                    "What is the hospital's charity care policy and EWS quota compliance?",
                    "How many billing complaints have been received in the past 12 months?",
                ],
            }

        elif stage == EscalationStage.CPGRAMS:
            return {
                **base_details,
                "action": "generate_filing",
                "portal": "CPGRAMS",
                "portal_url": self.PORTAL_URLS[stage],
                "filing_type": "public_grievance",
                "ministry": "Ministry of Health and Family Welfare",
                "template": "cpgrams_grievance",
            }

        elif stage == EscalationStage.MEDIA_ALERT:
            return {
                **base_details,
                "action": "alert_journalists",
                "pitch_template": "journalist_pitch",
                "hashtags": ["MedicalBilling", "PatientRights", "HealthcareIndia"],
            }

        elif stage == EscalationStage.SOCIAL_MEDIA:
            return {
                **base_details,
                "action": "social_post",
                "platforms": ["twitter", "linkedin"],
                "template": "social_media_post",
                "include_evidence": True,
            }

        return base_details

    def record_response(
        self,
        case_id: str,
        response_content: str,
        settlement_offered: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Record a response from the hospital"""
        if case_id not in self.cases:
            return {"error": "Case not found"}

        state = self.cases[case_id]
        state.total_responses += 1
        state.last_response_date = datetime.now()

        if settlement_offered:
            state.settlement_offered = settlement_offered

            # Calculate if this is acceptable
            min_acceptable = state.fair_amount * 1.2  # 20% above fair rate
            is_good_offer = settlement_offered <= min_acceptable

            return {
                "case_id": case_id,
                "response_recorded": True,
                "settlement_offered": settlement_offered,
                "recommendation": "ACCEPT" if is_good_offer else "NEGOTIATE",
                "target_amount": state.fair_amount,
                "max_acceptable": min_acceptable,
            }

        return {
            "case_id": case_id,
            "response_recorded": True,
            "total_responses": state.total_responses,
        }

    def pause_escalation(self, case_id: str, reason: str) -> Dict[str, Any]:
        """Pause escalation (e.g., during active negotiation)"""
        if case_id not in self.cases:
            return {"error": "Case not found"}

        state = self.cases[case_id]
        state.is_active = False
        state.pause_reason = reason
        state.current_stage = EscalationStage.PAUSED

        return {
            "case_id": case_id,
            "status": "paused",
            "reason": reason,
        }

    def resolve_case(
        self,
        case_id: str,
        final_amount: float,
        resolution_type: str = "negotiated",
    ) -> Dict[str, Any]:
        """Mark case as resolved"""
        if case_id not in self.cases:
            return {"error": "Case not found"}

        state = self.cases[case_id]
        state.is_active = False
        state.current_stage = EscalationStage.RESOLVED
        state.settlement_accepted = True
        state.settlement_offered = final_amount

        savings = state.billed_amount - final_amount
        savings_pct = (savings / state.billed_amount) * 100 if state.billed_amount > 0 else 0

        return {
            "case_id": case_id,
            "status": "resolved",
            "resolution_type": resolution_type,
            "original_bill": state.billed_amount,
            "final_amount": final_amount,
            "total_savings": savings,
            "savings_percentage": round(savings_pct, 1),
            "escalation_stage_reached": state.current_stage,
            "days_to_resolution": (datetime.now() - state.created_at).days,
        }

    def get_case_status(self, case_id: str) -> Dict[str, Any]:
        """Get comprehensive status of a case"""
        if case_id not in self.cases:
            return {"error": "Case not found"}

        state = self.cases[case_id]

        # Calculate progress
        executed_actions = len([a for a in state.actions if a.executed])
        total_actions = len(state.actions)

        # Find next scheduled action
        next_action = None
        for action in state.actions:
            if not action.executed:
                next_action = {
                    "stage": action.stage,
                    "scheduled_date": action.scheduled_date.isoformat(),
                    "days_until": (action.scheduled_date - datetime.now()).days,
                }
                break

        return {
            "case_id": state.case_id,
            "status": "active" if state.is_active else state.current_stage,
            "created_at": state.created_at.isoformat(),
            "hospital": state.hospital_name,
            "billed_amount": state.billed_amount,
            "fair_amount": state.fair_amount,
            "overcharge_percentage": state.overcharge_percentage,
            "current_stage": state.current_stage,
            "progress": {
                "executed": executed_actions,
                "total": total_actions,
                "percentage": round((executed_actions / total_actions) * 100, 1) if total_actions > 0 else 0,
            },
            "next_action": next_action,
            "responses_received": state.total_responses,
            "settlement_offered": state.settlement_offered,
            "timeline": [
                {
                    "stage": a.stage,
                    "scheduled": a.scheduled_date.isoformat(),
                    "executed": a.executed,
                    "response": a.response_received,
                }
                for a in state.actions
            ],
        }

    def get_n8n_webhook_payload(self, case_id: str) -> Dict[str, Any]:
        """
        Generate payload for n8n webhook to execute actions.
        n8n workflow should be configured to:
        1. Receive this webhook
        2. Execute the appropriate action (send email, file complaint, etc.)
        3. Call back to record execution status
        """
        pending = self.get_pending_actions(case_id)
        if not pending:
            return {"case_id": case_id, "actions": [], "message": "No pending actions"}

        return {
            "case_id": case_id,
            "timestamp": datetime.now().isoformat(),
            "actions": pending,
            "callback_url": f"/api/escalation/{case_id}/callback",
        }


# Global instance for the API
escalation_pipeline = EscalationPipeline()
