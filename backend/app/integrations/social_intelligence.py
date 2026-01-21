"""
Social Intelligence Module
==========================
Monitors social media, reviews, and news for hospital reputation data.

Features:
- Aggregate hospital reputation scores
- Track complaint trends
- Monitor news mentions
- Generate social media posts
- Connect patients with similar issues

"You can see the hospital's reputation bleeding in real-time."
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import hashlib
import random


class ReviewData(BaseModel):
    """Individual review/complaint data"""
    platform: str
    rating: Optional[float] = None
    sentiment: str  # positive, negative, neutral
    category: str  # billing, care, staff, facility
    snippet: str
    date: datetime
    url: Optional[str] = None


class HospitalReputation(BaseModel):
    """Aggregated hospital reputation data"""
    hospital_name: str
    city: str
    overall_score: float  # 0-100
    trend: str  # improving, declining, stable
    trend_percentage: float

    review_count: int
    average_rating: float  # 1-5

    sentiment_breakdown: Dict[str, int]  # positive, negative, neutral counts
    category_breakdown: Dict[str, int]  # billing, care, staff, etc.

    recent_complaints: List[ReviewData]
    billing_complaint_rate: float  # % of complaints about billing

    news_mentions: int
    negative_news_count: int


class SocialPost(BaseModel):
    """Pre-formatted social media post"""
    platform: str
    content: str
    hashtags: List[str]
    character_count: int
    includes_mention: bool
    call_to_action: str


class SocialIntelligence:
    """
    Aggregates and analyzes social/review data about hospitals.

    In production, this would connect to:
    - Twitter/X API
    - Google Reviews API
    - Practo API
    - News APIs
    - Consumer complaint databases

    For now, uses realistic simulated data based on actual hospital reputations.
    """

    HOSPITAL_BASE_DATA = {
        "kokilaben": {
            "full_name": "Kokilaben Dhirubhai Ambani Hospital",
            "city": "Mumbai",
            "base_rating": 4.2,
            "billing_complaint_rate": 0.35,
            "reputation_score": 72,
        },
        "fortis": {
            "full_name": "Fortis Hospital",
            "city": "Multiple",
            "base_rating": 3.8,
            "billing_complaint_rate": 0.42,
            "reputation_score": 65,
        },
        "apollo": {
            "full_name": "Apollo Hospitals",
            "city": "Multiple",
            "base_rating": 4.0,
            "billing_complaint_rate": 0.38,
            "reputation_score": 68,
        },
        "max": {
            "full_name": "Max Super Speciality Hospital",
            "city": "Delhi",
            "base_rating": 3.9,
            "billing_complaint_rate": 0.40,
            "reputation_score": 66,
        },
        "lilavati": {
            "full_name": "Lilavati Hospital",
            "city": "Mumbai",
            "base_rating": 4.1,
            "billing_complaint_rate": 0.30,
            "reputation_score": 70,
        },
        "manipal": {
            "full_name": "Manipal Hospital",
            "city": "Bangalore",
            "base_rating": 4.3,
            "billing_complaint_rate": 0.28,
            "reputation_score": 75,
        },
        "narayana": {
            "full_name": "Narayana Health",
            "city": "Bangalore",
            "base_rating": 4.4,
            "billing_complaint_rate": 0.22,
            "reputation_score": 80,
        },
        "medanta": {
            "full_name": "Medanta - The Medicity",
            "city": "Gurgaon",
            "base_rating": 4.1,
            "billing_complaint_rate": 0.36,
            "reputation_score": 69,
        },
    }

    COMPLAINT_TEMPLATES = {
        "billing": [
            "Charged ₹{amount} for a simple procedure. Way overpriced!",
            "Hidden charges everywhere. Final bill was 3x the estimate.",
            "They charged ₹{amount} for what should cost ₹{fair}. Ridiculous.",
            "No itemized bill provided. Just a shocking total amount.",
            "Insurance rejected because hospital inflated the bill.",
        ],
        "care": [
            "Doctors were good but nursing staff could be better.",
            "Long waiting times even with appointment.",
            "Treatment was good, recovery was smooth.",
            "Post-surgery care was excellent.",
        ],
        "staff": [
            "Front desk staff very helpful.",
            "Billing department was unresponsive to queries.",
            "Nurses were caring and attentive.",
            "Administration was unhelpful during discharge.",
        ],
    }

    def __init__(self):
        pass

    def _normalize_hospital(self, hospital_name: str) -> Optional[str]:
        """Normalize hospital name to key"""
        name_lower = hospital_name.lower()
        for key in self.HOSPITAL_BASE_DATA.keys():
            if key in name_lower:
                return key
        return None

    def get_hospital_reputation(
        self,
        hospital_name: str,
        city: Optional[str] = None,
    ) -> HospitalReputation:
        """
        Get aggregated reputation data for a hospital.
        """
        hospital_key = self._normalize_hospital(hospital_name)

        if hospital_key and hospital_key in self.HOSPITAL_BASE_DATA:
            base_data = self.HOSPITAL_BASE_DATA[hospital_key]
        else:
            # Default for unknown hospitals
            base_data = {
                "full_name": hospital_name,
                "city": city or "Unknown",
                "base_rating": 3.5,
                "billing_complaint_rate": 0.35,
                "reputation_score": 60,
            }

        # Generate realistic review data
        total_reviews = random.randint(500, 2000)
        recent_complaints = self._generate_recent_complaints(
            hospital_name=base_data["full_name"],
            billing_rate=base_data["billing_complaint_rate"],
        )

        # Calculate sentiment breakdown
        negative_count = int(total_reviews * (1 - base_data["base_rating"] / 5) * 1.5)
        positive_count = int(total_reviews * (base_data["base_rating"] / 5) * 0.8)
        neutral_count = total_reviews - negative_count - positive_count

        # Calculate category breakdown
        billing_complaints = int(total_reviews * base_data["billing_complaint_rate"])
        care_complaints = int(total_reviews * 0.25)
        staff_complaints = int(total_reviews * 0.15)
        facility_complaints = int(total_reviews * 0.10)

        # Trend calculation (simulated)
        trend_pct = random.uniform(-15, 10)
        trend = "declining" if trend_pct < -5 else ("improving" if trend_pct > 5 else "stable")

        return HospitalReputation(
            hospital_name=base_data["full_name"],
            city=base_data.get("city", city or "Unknown"),
            overall_score=base_data["reputation_score"],
            trend=trend,
            trend_percentage=round(trend_pct, 1),
            review_count=total_reviews,
            average_rating=base_data["base_rating"],
            sentiment_breakdown={
                "positive": positive_count,
                "negative": negative_count,
                "neutral": neutral_count,
            },
            category_breakdown={
                "billing": billing_complaints,
                "care": care_complaints,
                "staff": staff_complaints,
                "facility": facility_complaints,
            },
            recent_complaints=recent_complaints,
            billing_complaint_rate=round(base_data["billing_complaint_rate"] * 100, 1),
            news_mentions=random.randint(5, 30),
            negative_news_count=random.randint(0, 5),
        )

    def _generate_recent_complaints(
        self,
        hospital_name: str,
        billing_rate: float,
        count: int = 5,
    ) -> List[ReviewData]:
        """Generate realistic recent complaints"""
        complaints = []

        platforms = ["Google Reviews", "Practo", "Twitter", "Consumer Forum"]

        for i in range(count):
            is_billing = random.random() < billing_rate
            category = "billing" if is_billing else random.choice(["care", "staff"])

            templates = self.COMPLAINT_TEMPLATES.get(category, self.COMPLAINT_TEMPLATES["care"])
            template = random.choice(templates)

            # Fill in template variables
            snippet = template.format(
                amount=f"{random.randint(1, 5)}L",
                fair=f"{random.randint(30, 80)}K",
            )

            days_ago = random.randint(1, 30)

            complaints.append(ReviewData(
                platform=random.choice(platforms),
                rating=random.uniform(1.0, 3.0) if is_billing else random.uniform(2.5, 4.5),
                sentiment="negative" if is_billing else random.choice(["negative", "neutral", "positive"]),
                category=category,
                snippet=snippet,
                date=datetime.now() - timedelta(days=days_ago),
            ))

        # Sort by date (most recent first)
        complaints.sort(key=lambda x: x.date, reverse=True)
        return complaints

    def generate_social_posts(
        self,
        hospital_name: str,
        procedure: str,
        billed_amount: float,
        fair_amount: float,
        include_hospital_handle: bool = False,
    ) -> List[SocialPost]:
        """
        Generate pre-formatted social media posts.
        """
        overcharge = billed_amount - fair_amount
        overcharge_pct = ((billed_amount - fair_amount) / fair_amount) * 100 if fair_amount > 0 else 0

        posts = []

        # Twitter/X Post
        twitter_content = f"""I was charged ₹{billed_amount/100000:.1f}L for {procedure} at {hospital_name}.

Government approved rate (CGHS): ₹{fair_amount/100000:.1f}L

That's {overcharge_pct:.0f}% OVERCHARGE. ₹{overcharge/100000:.1f}L extra.

This is why we need healthcare price transparency in India. 🧵"""

        twitter_hashtags = ["MedicalBilling", "HealthcareIndia", "PatientRights", "CGHS", "ConsumerRights"]

        posts.append(SocialPost(
            platform="Twitter/X",
            content=twitter_content,
            hashtags=twitter_hashtags,
            character_count=len(twitter_content),
            includes_mention=include_hospital_handle,
            call_to_action="Share to raise awareness about medical overcharging",
        ))

        # LinkedIn Post
        linkedin_content = f"""🏥 A personal experience with healthcare pricing in India:

I recently underwent {procedure} at {hospital_name}.

Bill received: ₹{billed_amount:,.0f}
CGHS approved rate: ₹{fair_amount:,.0f}
Overcharge: ₹{overcharge:,.0f} ({overcharge_pct:.0f}%)

This isn't an isolated incident. Every year, Indian patients lose ₹47,000 Crore to medical overcharging.

What can we do?
✅ Know your rights (Consumer Protection Act covers medical services)
✅ Check CGHS/PMJAY rates before procedures
✅ File complaints on e-Jagriti if overcharged
✅ Share your experiences

The information asymmetry between hospitals and patients is the real problem. It's time to level the playing field.

#Healthcare #India #PatientRights #MedicalBilling #ConsumerRights #HealthcareTransparency"""

        posts.append(SocialPost(
            platform="LinkedIn",
            content=linkedin_content,
            hashtags=["Healthcare", "India", "PatientRights", "MedicalBilling"],
            character_count=len(linkedin_content),
            includes_mention=False,
            call_to_action="Share with your network to spread awareness",
        ))

        # WhatsApp/Short Format
        whatsapp_content = f"""⚠️ *Medical Bill Alert*

{hospital_name} charged me *₹{billed_amount/100000:.1f} Lakh* for {procedure}

Government rate (CGHS): *₹{fair_amount/100000:.1f} Lakh*

I was overcharged by *₹{overcharge/100000:.1f} Lakh* ({overcharge_pct:.0f}%)

Know someone dealing with hospital bills? Share this.

Check your rights: e-jagriti.gov.in"""

        posts.append(SocialPost(
            platform="WhatsApp",
            content=whatsapp_content,
            hashtags=[],
            character_count=len(whatsapp_content),
            includes_mention=False,
            call_to_action="Forward to friends and family",
        ))

        return posts

    def find_similar_patients(
        self,
        hospital_name: str,
        procedure: str,
        city: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Find other patients with similar disputes (simulated).

        In production, this would query the community database.
        """
        hospital_key = self._normalize_hospital(hospital_name)

        # Simulated data based on hospital
        base_count = 8 if hospital_key else 3

        return {
            "hospital": hospital_name,
            "procedure": procedure,
            "city": city,
            "similar_disputes_active": random.randint(base_count, base_count + 10),
            "similar_disputes_resolved": random.randint(base_count * 2, base_count * 5),
            "average_resolution_time_days": random.randint(15, 60),
            "average_discount_achieved": random.randint(35, 55),
            "collective_action_available": base_count > 5,
            "message": f"You're not alone. {random.randint(base_count, base_count + 10)} other patients are currently disputing bills from {hospital_name}.",
            "cta": "Join the community to share experiences and coordinate action",
        }

    def get_journalist_matches(
        self,
        hospital_name: str,
        city: str,
    ) -> List[Dict[str, Any]]:
        """
        Find journalists who cover healthcare/consumer issues.

        This would connect to a journalist database in production.
        """
        journalists = [
            {
                "name": "Healthcare Correspondent",
                "outlet": "Economic Times",
                "beat": "Healthcare Policy & Industry",
                "recent_story": "Hospital billing practices under scanner",
                "contact_method": "Via publication",
            },
            {
                "name": "Consumer Affairs Reporter",
                "outlet": "The Hindu",
                "beat": "Consumer Rights",
                "recent_story": "Consumer court wins against private hospitals",
                "contact_method": "Via publication",
            },
            {
                "name": "Investigative Reporter",
                "outlet": "The Print",
                "beat": "Healthcare Investigations",
                "recent_story": "The hidden costs of private healthcare",
                "contact_method": "Via publication",
            },
        ]

        return {
            "journalists": journalists,
            "pitch_template": self._generate_journalist_pitch(hospital_name, city),
            "note": "Journalists are more likely to cover stories when multiple patients are affected. Consider coordinating with other affected patients.",
        }

    def _generate_journalist_pitch(self, hospital_name: str, city: str) -> str:
        """Generate journalist pitch template"""
        return f"""
Subject: Story Lead - Systematic Medical Overcharging at {hospital_name}

Dear [Journalist Name],

I'm writing to share a story lead about systematic overcharging at {hospital_name}, {city}.

KEY FACTS:
• Patients being charged 200-500% above government-approved CGHS rates
• Multiple patients affected (I can connect you with others)
• Documentary evidence of overcharging available
• Consumer court precedents support patients

STORY ANGLE:
This isn't just one patient's complaint - it's a pattern affecting thousands. With healthcare costs being a major concern for Indian families, this story exposes how information asymmetry allows hospitals to charge whatever they want.

I have:
✓ My own documented case with bills and government rate comparisons
✓ Connection to other affected patients
✓ Legal analysis and consumer court precedents
✓ Willingness to go on record

Would you be interested in exploring this story? Happy to share documentation and connect you with other sources.

Best regards,
[Your Name]
""".strip()


# Global instance
social_intelligence = SocialIntelligence()
