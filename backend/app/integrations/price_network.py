"""
Crowdsourced Price Network
==========================
Anonymous bill data collection and aggregation system.

Features:
- Anonymous bill submission (no PII stored)
- City/hospital/procedure aggregation
- Real market price intelligence
- Comparison percentiles
- Network effects - each submission makes it more valuable

"847 patients shared bills from Mumbai hospitals this month.
Average appendectomy: ₹1,42,000. You're paying ₹3,50,000."
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from collections import defaultdict
import hashlib
import statistics


class PriceSubmission(BaseModel):
    """Anonymous price submission from a patient"""
    hospital_name: str
    hospital_city: str
    hospital_state: str
    procedure: str
    total_amount: float
    year: int = datetime.now().year
    month: int = datetime.now().month
    # Optional anonymized context
    was_emergency: bool = False
    had_insurance: bool = False
    negotiated: bool = False
    final_amount: Optional[float] = None  # If negotiated
    outcome: Optional[str] = None  # "paid_full", "negotiated", "consumer_court", etc.


class PriceDataPoint(BaseModel):
    """Stored price data point (anonymized)"""
    submission_hash: str  # Unique identifier
    hospital_normalized: str  # Normalized hospital name
    city: str
    state: str
    procedure_normalized: str  # Normalized procedure name
    amount: float
    final_amount: Optional[float]
    year: int
    month: int
    was_emergency: bool
    had_insurance: bool
    negotiated: bool
    outcome: Optional[str]
    submitted_at: datetime


class PriceNetwork:
    """
    Manages crowdsourced price intelligence.

    In production, this would be backed by a proper database.
    For now, using in-memory storage with sample data.
    """

    # Procedure name normalization
    PROCEDURE_ALIASES = {
        "appendectomy": ["appendix", "appendicectomy", "appendix removal"],
        "caesarean": ["c-section", "cesarean", "caesarean section", "c section", "lscs"],
        "cholecystectomy": ["gallbladder", "gallbladder removal", "gall bladder"],
        "hernia_repair": ["hernia", "hernioplasty", "inguinal hernia"],
        "knee_replacement": ["tkr", "total knee replacement", "knee surgery"],
        "hip_replacement": ["thr", "total hip replacement", "hip surgery"],
        "angioplasty": ["ptca", "stent", "coronary angioplasty"],
        "bypass": ["cabg", "coronary bypass", "heart bypass"],
        "cataract": ["cataract surgery", "phaco", "lens replacement"],
        "mri": ["mri scan", "magnetic resonance"],
        "ct_scan": ["ct", "cat scan", "computed tomography"],
    }

    # Hospital name normalization
    HOSPITAL_ALIASES = {
        "kokilaben": ["kokilaben dhirubhai ambani", "kdah", "kokilaben hospital"],
        "fortis": ["fortis hospital", "fortis healthcare"],
        "apollo": ["apollo hospital", "apollo hospitals"],
        "max": ["max hospital", "max healthcare", "max super speciality"],
        "lilavati": ["lilavati hospital"],
        "manipal": ["manipal hospital", "manipal hospitals"],
        "narayana": ["narayana health", "narayana hrudayalaya", "nh"],
        "aiims": ["aiims delhi", "all india institute"],
        "medanta": ["medanta hospital", "medanta medicity"],
        "breach_candy": ["breach candy", "breach candy hospital"],
    }

    def __init__(self):
        self.data_points: List[PriceDataPoint] = []
        self._load_seed_data()

    def _normalize_procedure(self, procedure: str) -> str:
        """Normalize procedure name for matching"""
        proc_lower = procedure.lower().strip()
        for normalized, aliases in self.PROCEDURE_ALIASES.items():
            if proc_lower in aliases or normalized in proc_lower:
                return normalized
        return proc_lower.replace(" ", "_")

    def _normalize_hospital(self, hospital: str) -> str:
        """Normalize hospital name for matching"""
        hosp_lower = hospital.lower().strip()
        for normalized, aliases in self.HOSPITAL_ALIASES.items():
            for alias in aliases:
                if alias in hosp_lower:
                    return normalized
        return hosp_lower.replace(" ", "_")[:50]

    def _generate_hash(self, submission: PriceSubmission) -> str:
        """Generate unique hash for submission (for deduplication)"""
        data = f"{submission.hospital_name}{submission.procedure}{submission.total_amount}{submission.year}{submission.month}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def _load_seed_data(self):
        """Load realistic seed data based on actual Indian hospital prices"""
        seed_data = [
            # Mumbai - Kokilaben
            {"hospital": "Kokilaben", "city": "Mumbai", "state": "Maharashtra", "procedure": "appendectomy", "amounts": [320000, 285000, 350000, 290000, 310000]},
            {"hospital": "Kokilaben", "city": "Mumbai", "state": "Maharashtra", "procedure": "caesarean", "amounts": [180000, 220000, 195000, 210000]},
            {"hospital": "Kokilaben", "city": "Mumbai", "state": "Maharashtra", "procedure": "cholecystectomy", "amounts": [250000, 280000, 265000, 290000]},
            {"hospital": "Kokilaben", "city": "Mumbai", "state": "Maharashtra", "procedure": "knee_replacement", "amounts": [450000, 520000, 480000, 500000]},

            # Mumbai - Lilavati
            {"hospital": "Lilavati", "city": "Mumbai", "state": "Maharashtra", "procedure": "appendectomy", "amounts": [180000, 165000, 195000, 175000]},
            {"hospital": "Lilavati", "city": "Mumbai", "state": "Maharashtra", "procedure": "caesarean", "amounts": [120000, 140000, 135000, 130000]},
            {"hospital": "Lilavati", "city": "Mumbai", "state": "Maharashtra", "procedure": "angioplasty", "amounts": [280000, 320000, 300000]},

            # Mumbai - Fortis
            {"hospital": "Fortis", "city": "Mumbai", "state": "Maharashtra", "procedure": "appendectomy", "amounts": [220000, 245000, 230000, 250000]},
            {"hospital": "Fortis", "city": "Mumbai", "state": "Maharashtra", "procedure": "bypass", "amounts": [450000, 520000, 480000]},

            # Delhi - Max
            {"hospital": "Max", "city": "Delhi", "state": "Delhi", "procedure": "appendectomy", "amounts": [280000, 310000, 295000, 320000]},
            {"hospital": "Max", "city": "Delhi", "state": "Delhi", "procedure": "caesarean", "amounts": [150000, 175000, 165000, 180000]},
            {"hospital": "Max", "city": "Delhi", "state": "Delhi", "procedure": "knee_replacement", "amounts": [380000, 420000, 400000]},

            # Delhi - Apollo
            {"hospital": "Apollo", "city": "Delhi", "state": "Delhi", "procedure": "appendectomy", "amounts": [240000, 260000, 250000, 270000]},
            {"hospital": "Apollo", "city": "Delhi", "state": "Delhi", "procedure": "angioplasty", "amounts": [250000, 290000, 270000, 280000]},
            {"hospital": "Apollo", "city": "Delhi", "state": "Delhi", "procedure": "cataract", "amounts": [45000, 55000, 50000, 48000]},

            # Delhi - Fortis
            {"hospital": "Fortis", "city": "Delhi", "state": "Delhi", "procedure": "appendectomy", "amounts": [260000, 280000, 270000]},
            {"hospital": "Fortis", "city": "Delhi", "state": "Delhi", "procedure": "hernia_repair", "amounts": [180000, 200000, 190000]},

            # Bangalore - Manipal
            {"hospital": "Manipal", "city": "Bangalore", "state": "Karnataka", "procedure": "appendectomy", "amounts": [150000, 175000, 160000, 165000]},
            {"hospital": "Manipal", "city": "Bangalore", "state": "Karnataka", "procedure": "caesarean", "amounts": [100000, 120000, 110000]},

            # Bangalore - Narayana
            {"hospital": "Narayana", "city": "Bangalore", "state": "Karnataka", "procedure": "appendectomy", "amounts": [120000, 140000, 130000, 135000]},
            {"hospital": "Narayana", "city": "Bangalore", "state": "Karnataka", "procedure": "bypass", "amounts": [280000, 320000, 300000, 310000]},
            {"hospital": "Narayana", "city": "Bangalore", "state": "Karnataka", "procedure": "angioplasty", "amounts": [180000, 210000, 195000]},

            # Chennai - Apollo
            {"hospital": "Apollo", "city": "Chennai", "state": "Tamil Nadu", "procedure": "appendectomy", "amounts": [200000, 220000, 210000]},
            {"hospital": "Apollo", "city": "Chennai", "state": "Tamil Nadu", "procedure": "hip_replacement", "amounts": [350000, 400000, 380000]},

            # Hyderabad - Apollo
            {"hospital": "Apollo", "city": "Hyderabad", "state": "Telangana", "procedure": "appendectomy", "amounts": [180000, 200000, 190000]},
            {"hospital": "Apollo", "city": "Hyderabad", "state": "Telangana", "procedure": "caesarean", "amounts": [95000, 110000, 100000]},
        ]

        # Generate data points from seed
        for entry in seed_data:
            for i, amount in enumerate(entry["amounts"]):
                # Vary the months to simulate real submissions
                month = ((datetime.now().month - 1 - i) % 12) + 1
                year = datetime.now().year if month <= datetime.now().month else datetime.now().year - 1

                submission = PriceSubmission(
                    hospital_name=entry["hospital"],
                    hospital_city=entry["city"],
                    hospital_state=entry["state"],
                    procedure=entry["procedure"],
                    total_amount=amount,
                    year=year,
                    month=month,
                )
                self._add_data_point(submission)

    def _add_data_point(self, submission: PriceSubmission) -> PriceDataPoint:
        """Add a new data point"""
        data_point = PriceDataPoint(
            submission_hash=self._generate_hash(submission),
            hospital_normalized=self._normalize_hospital(submission.hospital_name),
            city=submission.hospital_city,
            state=submission.hospital_state,
            procedure_normalized=self._normalize_procedure(submission.procedure),
            amount=submission.total_amount,
            final_amount=submission.final_amount,
            year=submission.year,
            month=submission.month,
            was_emergency=submission.was_emergency,
            had_insurance=submission.had_insurance,
            negotiated=submission.negotiated,
            outcome=submission.outcome,
            submitted_at=datetime.now(),
        )
        self.data_points.append(data_point)
        return data_point

    def submit_price(self, submission: PriceSubmission) -> Dict[str, Any]:
        """Submit a new anonymous price data point"""
        # Check for duplicates
        submission_hash = self._generate_hash(submission)
        if any(dp.submission_hash == submission_hash for dp in self.data_points):
            return {
                "success": False,
                "message": "This submission appears to be a duplicate",
            }

        data_point = self._add_data_point(submission)

        # Get comparison data
        comparison = self.get_price_comparison(
            procedure=submission.procedure,
            city=submission.hospital_city,
            hospital=submission.hospital_name,
            amount=submission.total_amount,
        )

        return {
            "success": True,
            "message": "Thank you! Your anonymous submission helps other patients.",
            "submission_id": data_point.submission_hash,
            "comparison": comparison,
            "total_submissions_this_month": self._count_recent_submissions(),
        }

    def _count_recent_submissions(self) -> int:
        """Count submissions in the last 30 days"""
        cutoff = datetime.now() - timedelta(days=30)
        return len([dp for dp in self.data_points if dp.submitted_at >= cutoff])

    def get_price_comparison(
        self,
        procedure: str,
        city: str,
        hospital: Optional[str] = None,
        amount: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Get comprehensive price comparison for a procedure.

        Returns:
        - City average
        - Hospital-specific data
        - Percentile ranking
        - Price range
        - Historical trend
        """
        proc_normalized = self._normalize_procedure(procedure)
        city_lower = city.lower()

        # Filter relevant data points
        city_data = [
            dp for dp in self.data_points
            if dp.procedure_normalized == proc_normalized and dp.city.lower() == city_lower
        ]

        if not city_data:
            return {
                "data_available": False,
                "message": f"No price data available for {procedure} in {city} yet. Be the first to contribute!",
                "total_submissions": 0,
            }

        city_amounts = [dp.amount for dp in city_data]

        # Calculate statistics
        city_avg = statistics.mean(city_amounts)
        city_median = statistics.median(city_amounts)
        city_min = min(city_amounts)
        city_max = max(city_amounts)
        city_stdev = statistics.stdev(city_amounts) if len(city_amounts) > 1 else 0

        # Hospital-specific breakdown
        hospital_breakdown = defaultdict(list)
        for dp in city_data:
            hospital_breakdown[dp.hospital_normalized].append(dp.amount)

        hospital_stats = []
        for hosp, amounts in hospital_breakdown.items():
            hospital_stats.append({
                "hospital": hosp.replace("_", " ").title(),
                "average": round(statistics.mean(amounts)),
                "min": min(amounts),
                "max": max(amounts),
                "submissions": len(amounts),
            })

        # Sort by average price
        hospital_stats.sort(key=lambda x: x["average"])

        result = {
            "data_available": True,
            "procedure": procedure,
            "city": city,
            "total_submissions": len(city_data),
            "city_statistics": {
                "average": round(city_avg),
                "median": round(city_median),
                "min": round(city_min),
                "max": round(city_max),
                "std_dev": round(city_stdev),
            },
            "hospital_breakdown": hospital_stats,
        }

        # If specific hospital provided
        if hospital:
            hosp_normalized = self._normalize_hospital(hospital)
            hosp_data = [dp for dp in city_data if dp.hospital_normalized == hosp_normalized]

            if hosp_data:
                hosp_amounts = [dp.amount for dp in hosp_data]
                result["your_hospital"] = {
                    "name": hospital,
                    "average": round(statistics.mean(hosp_amounts)),
                    "submissions": len(hosp_data),
                    "vs_city_avg": round(statistics.mean(hosp_amounts) - city_avg),
                    "vs_city_avg_pct": round(((statistics.mean(hosp_amounts) - city_avg) / city_avg) * 100, 1) if city_avg > 0 else 0,
                }

        # If specific amount provided, calculate percentile
        if amount:
            below_count = len([a for a in city_amounts if a < amount])
            percentile = (below_count / len(city_amounts)) * 100

            result["your_bill"] = {
                "amount": amount,
                "percentile": round(percentile, 1),
                "interpretation": self._interpret_percentile(percentile),
                "vs_average": round(amount - city_avg),
                "vs_average_pct": round(((amount - city_avg) / city_avg) * 100, 1) if city_avg > 0 else 0,
                "cheaper_hospitals": [
                    h for h in hospital_stats if h["average"] < amount
                ],
            }

        return result

    def _interpret_percentile(self, percentile: float) -> str:
        """Interpret what a percentile means"""
        if percentile >= 90:
            return "VERY HIGH - You're being charged more than 90% of patients"
        elif percentile >= 75:
            return "HIGH - You're being charged more than 75% of patients"
        elif percentile >= 50:
            return "ABOVE AVERAGE - You're being charged more than half of patients"
        elif percentile >= 25:
            return "BELOW AVERAGE - You're being charged less than most patients"
        else:
            return "LOW - You're getting a relatively good rate"

    def get_city_overview(self, city: str) -> Dict[str, Any]:
        """Get overview of all procedures in a city"""
        city_lower = city.lower()
        city_data = [dp for dp in self.data_points if dp.city.lower() == city_lower]

        if not city_data:
            return {
                "city": city,
                "data_available": False,
                "message": f"No price data available for {city} yet.",
            }

        # Group by procedure
        procedure_stats = defaultdict(list)
        for dp in city_data:
            procedure_stats[dp.procedure_normalized].append(dp.amount)

        procedures = []
        for proc, amounts in procedure_stats.items():
            procedures.append({
                "procedure": proc.replace("_", " ").title(),
                "average": round(statistics.mean(amounts)),
                "min": round(min(amounts)),
                "max": round(max(amounts)),
                "submissions": len(amounts),
            })

        procedures.sort(key=lambda x: x["submissions"], reverse=True)

        return {
            "city": city,
            "data_available": True,
            "total_submissions": len(city_data),
            "procedures_covered": len(procedure_stats),
            "hospitals_covered": len(set(dp.hospital_normalized for dp in city_data)),
            "procedures": procedures,
        }

    def get_network_stats(self) -> Dict[str, Any]:
        """Get overall network statistics"""
        total = len(self.data_points)
        recent = self._count_recent_submissions()

        cities = set(dp.city for dp in self.data_points)
        hospitals = set(dp.hospital_normalized for dp in self.data_points)
        procedures = set(dp.procedure_normalized for dp in self.data_points)

        # Calculate potential savings (comparing to cheapest in each city)
        potential_savings = 0
        for dp in self.data_points:
            city_proc_data = [
                d.amount for d in self.data_points
                if d.city == dp.city and d.procedure_normalized == dp.procedure_normalized
            ]
            if city_proc_data:
                min_price = min(city_proc_data)
                potential_savings += max(0, dp.amount - min_price)

        return {
            "total_submissions": total,
            "submissions_last_30_days": recent,
            "cities_covered": len(cities),
            "hospitals_covered": len(hospitals),
            "procedures_covered": len(procedures),
            "potential_savings_identified": round(potential_savings),
            "average_overcharge": round(potential_savings / total) if total > 0 else 0,
            "message": f"{total} patients have shared their bills. Together we're exposing ₹{potential_savings:,.0f} in overcharges.",
        }


# Global instance for the API
price_network = PriceNetwork()
