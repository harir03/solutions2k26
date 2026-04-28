"""
Synthetic Data Generator for IntelliCredit
Generates realistic Indian alternate data patterns for demo purposes
"""
import random
import numpy as np
from typing import Dict, List, Any
from datetime import datetime, timedelta


class SyntheticDataGenerator:
    """Generates synthetic data matching Indian alternate data patterns"""
    
    def __init__(self, seed: int = 42):
        random.seed(seed)
        np.random.seed(seed)
        
        # Indian demographic distributions (simplified for demo)
        self.districts = [
            "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata",
            "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Lucknow"
        ]
    
    def generate_user_profile(self, user_type: str = "individual") -> Dict[str, Any]:
        """Generate a complete synthetic user profile"""
        user_id = f"user_{random.randint(10000, 99999)}"
        
        # Determine risk profile (affects all data sources) - more balanced distribution
        risk_profile = random.choices(
            ["low", "medium", "high"],
            weights=[0.35, 0.40, 0.25]  # More medium risk users
        )[0]
        
        # Wider quality spread to create both good and bad candidates
        base_quality = {"low": 0.90, "medium": 0.55, "high": 0.25}[risk_profile]
        
        profile = {
            "user_id": user_id,
            "user_type": user_type,
            "risk_profile": risk_profile,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Generate data for each source with correlated quality
        profile["upi_bank"] = self._generate_upi_data(base_quality)
        profile["telecom"] = self._generate_telecom_data(base_quality)
        profile["ecommerce"] = self._generate_ecommerce_data(base_quality)
        profile["geolocation"] = self._generate_geolocation_data(base_quality)
        profile["questionnaire"] = self._generate_questionnaire_data(base_quality)
        
        if user_type == "msme":
            profile["merchant_gst"] = self._generate_merchant_data(base_quality)
        
        return profile
    
    def _generate_upi_data(self, quality: float) -> Dict[str, Any]:
        """Generate UPI/Bank cash flow data"""
        noise = random.uniform(-0.1, 0.1)
        adjusted_quality = max(0.1, min(1.0, quality + noise))
        
        return {
            "monthly_inflow_avg": random.uniform(15000, 150000) * adjusted_quality,
            "inflow_regularity": adjusted_quality + random.uniform(-0.05, 0.05),
            "emi_payment_history": adjusted_quality + random.uniform(-0.05, 0.05),
            "balance_trend": random.uniform(-0.3, 0.5) * adjusted_quality,
            "months_of_data": random.randint(6, 36)
        }
    
    def _generate_telecom_data(self, quality: float) -> Dict[str, Any]:
        """Generate telecom payment consistency data"""
        consistency = max(0.5, quality + random.uniform(-0.1, 0.1))
        tenure = random.randint(12, 60)
        missed = max(0, int((1 - consistency) * tenure * 0.1))
        
        return {
            "payment_consistency_24m": min(1.0, consistency),
            "missed_payments_count": missed,
            "average_bill_amount": random.uniform(300, 2000),
            "tenure_months": tenure
        }
    
    def _generate_ecommerce_data(self, quality: float) -> Dict[str, Any]:
        """Generate e-commerce behavior data"""
        return_rate = max(0.05, 0.3 - (quality * 0.25) + random.uniform(-0.05, 0.05))
        
        return {
            "return_rate": min(0.5, return_rate),
            "basket_growth_yoy": random.uniform(-0.1, 0.4) * quality,
            "emi_purchase_ratio": random.uniform(0.1, 0.4) * quality,
            "purchase_frequency": random.uniform(1, 10) * quality,
            "months_active": random.randint(6, 36)
        }
    
    def _generate_geolocation_data(self, quality: float) -> Dict[str, Any]:
        """Generate geolocation stability data (district-level only)"""
        stability_months = int(quality * 36 + random.uniform(-6, 6))
        
        return {
            "district_stability_months": max(1, min(60, stability_months)),
            "home_work_distance_km": random.uniform(2, 50),
            "relocation_count_12m": max(0, int((1 - quality) * 3 + random.uniform(-1, 1)))
        }
    
    def _generate_questionnaire_data(self, quality: float) -> List[Dict[str, Any]]:
        """Generate psychometric questionnaire responses"""
        questions = [
            (1, "How often do you save before making large purchases?"),
            (2, "Do you track your monthly expenses?"),
            (3, "How confident are you about your future income?"),
            (4, "Have you ever missed a bill payment due to forgetfulness?"),
            (5, "Do you maintain an emergency fund?"),
            (6, "How do you handle unexpected expenses?"),
            (7, "Do you compare prices before making purchases?"),
            (8, "How often do you use credit/EMI for purchases?"),
            (9, "Do you have financial goals for the next 5 years?"),
            (10, "How would you describe your risk tolerance?"),
        ]
        
        answers = []
        for q_id, question in questions:
            # Quality affects response positivity
            base_score = quality * 4 + random.uniform(-0.5, 0.5)
            score = max(1, min(5, base_score))
            
            answers.append({
                "question_id": q_id,
                "answer": self._score_to_text(score),
                "confidence": random.uniform(0.7, 1.0)
            })
        
        return answers
    
    def _score_to_text(self, score: float) -> str:
        """Convert numeric score to text response"""
        if score >= 4.5:
            return "Always/Very High"
        elif score >= 3.5:
            return "Often/High"
        elif score >= 2.5:
            return "Sometimes/Moderate"
        elif score >= 1.5:
            return "Rarely/Low"
        else:
            return "Never/Very Low"
    
    def _generate_merchant_data(self, quality: float) -> Dict[str, Any]:
        """Generate merchant/GST rating data for MSMEs"""
        return {
            "business_tenure_months": random.randint(12, 120),
            "gst_filing_regularity": max(0.5, quality + random.uniform(-0.1, 0.1)),
            "fulfillment_rate": max(0.6, quality + random.uniform(-0.1, 0.1)),
            "customer_rating_avg": random.uniform(3.0, 5.0) * quality,
            "monthly_revenue_avg": random.uniform(50000, 500000) * quality
        }
    
    def generate_dataset(self, n_users: int = 1000) -> List[Dict[str, Any]]:
        """Generate a complete dataset of synthetic users"""
        users = []
        for i in range(n_users):
            user_type = "msme" if random.random() < 0.3 else "individual"
            users.append(self.generate_user_profile(user_type))
        return users
    
    def calculate_true_default_risk(self, profile: Dict[str, Any]) -> float:
        """Calculate ground truth default probability for model training"""
        quality_signals = []
        
        if profile.get("upi_bank"):
            upi = profile["upi_bank"]
            quality_signals.append(upi["inflow_regularity"] * 0.3)
            quality_signals.append(upi["emi_payment_history"] * 0.3)
        
        if profile.get("telecom"):
            telecom = profile["telecom"]
            quality_signals.append(telecom["payment_consistency_24m"] * 0.25)
        
        if profile.get("questionnaire"):
            q_answers = profile["questionnaire"]
            avg_score = len(q_answers) > 0 and sum(
                1 for a in q_answers if "Often" in a["answer"] or "Always" in a["answer"]
            ) / len(q_answers) or 0.5
            quality_signals.append(avg_score * 0.15)
        
        if profile.get("ecommerce"):
            ecommerce = profile["ecommerce"]
            quality_signals.append((1 - ecommerce["return_rate"]) * 0.1)
        
        avg_quality = np.mean(quality_signals) if quality_signals else 0.5
        
        # Convert to default probability (inverse relationship)
        # Use threshold-based approach to ensure class balance
        risk_profile = profile.get("risk_profile", "medium")
        
        if risk_profile == "low":
            # Low risk users should have low default probability
            default_prob = random.uniform(0.05, 0.35)
        elif risk_profile == "medium":
            # Medium risk - around the threshold
            default_prob = random.uniform(0.35, 0.65)
        else:  # high risk
            # High risk users should have high default probability
            default_prob = random.uniform(0.65, 0.95)
        
        return default_prob


# Quick test
if __name__ == "__main__":
    generator = SyntheticDataGenerator()
    
    # Generate one sample user
    user = generator.generate_user_profile("individual")
    print("Sample User Profile:")
    print(f"User ID: {user['user_id']}")
    print(f"Risk Profile: {user['risk_profile']}")
    print(f"\nUPI Data: {user['upi_bank']}")
    print(f"Telecom Data: {user['telecom']}")
    print(f"\nTrue Default Risk: {generator.calculate_true_default_risk(user):.2%}")
    
    # Generate small dataset
    dataset = generator.generate_dataset(10)
    print(f"\nGenerated {len(dataset)} synthetic users")
