# Multi-System Integrations for The Equalizer
# These modules orchestrate multiple external systems to maximize patient leverage

from .escalation_pipeline import EscalationPipeline, EscalationState
from .price_network import PriceNetwork, PriceSubmission
from .grievance_blitz import GrievanceBlitz, GrievanceFiling
from .evidence_compiler import EvidenceCompiler
from .social_intelligence import SocialIntelligence

__all__ = [
    'EscalationPipeline',
    'EscalationState',
    'PriceNetwork',
    'PriceSubmission',
    'GrievanceBlitz',
    'GrievanceFiling',
    'EvidenceCompiler',
    'SocialIntelligence'
]
