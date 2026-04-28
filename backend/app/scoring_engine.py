"""
Simplified ML Scoring Engine for IntelliCredit
Tier 1: Zero history users (Telecom + Questionnaire + Geolocation)
Tier 2: Full data users (All 6 sources)
"""
import numpy as np
from typing import Dict, List, Tuple, Any
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.isotonic import IsotonicRegression
from sklearn.preprocessing import StandardScaler
import joblib
import os


class ScoringEngine:
    """Two-tier ML scoring engine with isotonic calibration"""
    
    def __init__(self, model_path: str = "backend/models"):
        self.model_path = model_path
        self.tier1_model = None
        self.tier2_model = None
        self.calibrator = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Feature weights for explainability
        self.feature_names_tier1 = [
            "telecom_consistency",
            "telecom_missed_payments",
            "questionnaire_score",
            "geolocation_stability",
            "relocation_count"
        ]
        
        self.feature_names_tier2 = [
            "upi_inflow_regularity",
            "upi_emi_history",
            "upi_balance_trend",
            "telecom_consistency",
            "telecom_missed_payments",
            "ecommerce_return_rate",
            "ecommerce_emi_ratio",
            "geolocation_stability",
            "questionnaire_score",
            "merchant_gst_regularity",
            "merchant_fulfillment_rate"
        ]
    
    def extract_features_tier1(self, profile: Dict[str, Any]) -> np.ndarray:
        """Extract features for Tier 1 model (zero history users)"""
        features = []
        
        # Telecom features
        telecom = profile.get("telecom", {})
        features.append(telecom.get("payment_consistency_24m", 0.5))
        features.append(telecom.get("missed_payments_count", 0) / 10.0)  # Normalize
        
        # Questionnaire score
        questionnaire = profile.get("questionnaire", [])
        if questionnaire:
            positive_answers = sum(
                1 for a in questionnaire 
                if "Often" in a["answer"] or "Always" in a["answer"]
            )
            q_score = positive_answers / len(questionnaire)
        else:
            q_score = 0.5
        features.append(q_score)
        
        # Geolocation features
        geo = profile.get("geolocation", {})
        features.append(min(1.0, geo.get("district_stability_months", 12) / 36.0))
        features.append(min(1.0, geo.get("relocation_count_12m", 0) / 3.0))
        
        return np.array(features).reshape(1, -1)
    
    def extract_features_tier2(self, profile: Dict[str, Any]) -> np.ndarray:
        """Extract features for Tier 2 model (full data users)"""
        features = []
        
        # UPI/Bank features
        upi = profile.get("upi_bank", {})
        features.append(upi.get("inflow_regularity", 0.5))
        features.append(upi.get("emi_payment_history", 0.5))
        features.append((upi.get("balance_trend", 0) + 1) / 2)  # Normalize to 0-1
        
        # Telecom features
        telecom = profile.get("telecom", {})
        features.append(telecom.get("payment_consistency_24m", 0.5))
        features.append(telecom.get("missed_payments_count", 0) / 10.0)
        
        # E-commerce features
        ecommerce = profile.get("ecommerce", {})
        features.append(1 - ecommerce.get("return_rate", 0.3))  # Invert - lower is better
        features.append(ecommerce.get("emi_purchase_ratio", 0.2))
        
        # Geolocation features
        geo = profile.get("geolocation", {})
        features.append(min(1.0, geo.get("district_stability_months", 12) / 36.0))
        
        # Questionnaire score
        questionnaire = profile.get("questionnaire", [])
        if questionnaire:
            positive_answers = sum(
                1 for a in questionnaire 
                if "Often" in a["answer"] or "Always" in a["answer"]
            )
            q_score = positive_answers / len(questionnaire)
        else:
            q_score = 0.5
        features.append(q_score)
        
        # Merchant/GST features (if MSME)
        merchant = profile.get("merchant_gst", {})
        if merchant:
            features.append(merchant.get("gst_filing_regularity", 0.5))
            features.append(merchant.get("fulfillment_rate", 0.5))
        else:
            features.append(0.5)  # Neutral for non-MSME
            features.append(0.5)
        
        return np.array(features).reshape(1, -1)
    
    def determine_tier(self, profile: Dict[str, Any]) -> int:
        """Determine which tier to use based on available data"""
        has_upi = profile.get("upi_bank") is not None
        has_merchant = profile.get("merchant_gst") is not None
        
        # Tier 2 requires UPI/bank data or merchant data
        if has_upi or has_merchant:
            return 2
        else:
            return 1
    
    def train(self, training_data: List[Dict[str, Any]], labels: List[float]):
        """Train both tier models on synthetic data"""
        print(f"Training on {len(training_data)} samples...")
        
        # Prepare Tier 1 data
        X_tier1 = []
        y_tier1 = []
        for profile, label in zip(training_data, labels):
            if self.determine_tier(profile) == 1:
                X_tier1.append(self.extract_features_tier1(profile)[0])
                y_tier1.append(label)
        
        # Prepare Tier 2 data
        X_tier2 = []
        y_tier2 = []
        for profile, label in zip(training_data, labels):
            if self.determine_tier(profile) == 2:
                X_tier2.append(self.extract_features_tier2(profile)[0])
                y_tier2.append(label)
        
        # Train Tier 1 model
        if len(X_tier1) > 10 and len(set(y_tier1)) > 1:
            self.tier1_model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=4,
                learning_rate=0.1,
                random_state=42
            )
            self.tier1_model.fit(np.array(X_tier1), np.array(y_tier1))
            print(f"Tier 1 model trained on {len(X_tier1)} samples")
        elif len(X_tier1) > 10:
            print(f"Tier 1: Skipping training - only 1 class present ({len(X_tier1)} samples)")
        
        # Train Tier 2 model
        if len(X_tier2) > 10 and len(set(y_tier2)) > 1:
            self.tier2_model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
            self.tier2_model.fit(np.array(X_tier2), np.array(y_tier2))
            print(f"Tier 2 model trained on {len(X_tier2)} samples")
        elif len(X_tier2) > 10:
            print(f"Tier 2: Skipping training - only 1 class present ({len(X_tier2)} samples)")
        
        # Train isotonic calibrator on all predictions
        all_probs = []
        all_labels = []
        for profile, label in zip(training_data, labels):
            prob = self.predict_probability(profile)
            all_probs.append(prob)
            all_labels.append(label)
        
        if len(set(all_labels)) > 1:
            self.calibrator = IsotonicRegression(out_of_bounds='clip')
            self.calibrator.fit(all_probs, all_labels)
            print("Isotonic calibrator trained")
        else:
            print("Calibrator: Skipping training - only 1 class present")
        
        self.is_trained = True
    
    def predict_probability(self, profile: Dict[str, Any]) -> float:
        """Get raw default probability from appropriate tier model"""
        tier = self.determine_tier(profile)
        
        if tier == 1 and self.tier1_model:
            features = self.extract_features_tier1(profile)
            prob = self.tier1_model.predict_proba(features)[0][1]
        elif tier == 2 and self.tier2_model:
            features = self.extract_features_tier2(profile)
            prob = self.tier2_model.predict_proba(features)[0][1]
        else:
            # Fallback for untrained models
            prob = 0.5
        
        return prob
    
    def predict_calibrated(self, profile: Dict[str, Any]) -> float:
        """Get calibrated default probability"""
        raw_prob = self.predict_probability(profile)
        
        if self.calibrator:
            calibrated = self.calibrator.predict([raw_prob])[0]
        else:
            calibrated = raw_prob
        
        return calibrated
    
    def calculate_score(self, profile: Dict[str, Any]) -> Tuple[int, str]:
        """Calculate 0-850 credit score from calibrated probability"""
        default_prob = self.predict_calibrated(profile)
        
        # Convert default probability to score (inverse relationship)
        # Lower default risk = higher score
        base_score = int((1 - default_prob) * 850)
        
        # Ensure score is in valid range
        score = max(0, min(850, base_score))
        
        # Determine band
        if score >= 750:
            band = "excellent"
        elif score >= 650:
            band = "good"
        elif score >= 550:
            band = "fair"
        elif score >= 450:
            band = "poor"
        else:
            band = "not_eligible"
        
        return score, band
    
    def get_shap_explanations(self, profile: Dict[str, Any], score: int) -> List[Dict[str, Any]]:
        """Generate SHAP-like explanations for the score"""
        tier = self.determine_tier(profile)
        
        if tier == 1:
            features = self.extract_features_tier1(profile)[0]
            feature_names = self.feature_names_tier1
            model = self.tier1_model
        else:
            features = self.extract_features_tier2(profile)[0]
            feature_names = self.feature_names_tier2
            model = self.tier2_model
        
        if not model:
            return []
        
        # Simplified SHAP approximation using feature importance * feature value
        explanations = []
        importances = model.feature_importances_
        
        # Calculate contribution for each feature
        total_positive = 0
        total_negative = 0
        
        for i, (feature_name, value, importance) in enumerate(zip(feature_names, features, importances)):
            # Direction depends on whether high values are good or bad
            negative_features = ["telecom_missed_payments", "relocation_count", "ecommerce_return_rate"]
            
            if feature_name in negative_features:
                contribution = -importance * value * 100
            else:
                contribution = importance * value * 100
            
            direction = "positive" if contribution > 0 else "negative"
            
            # Generate plain language explanation
            plain_lang = self._generate_explanation(feature_name, value, direction)
            
            explanations.append({
                "feature_name": self._pretty_feature_name(feature_name),
                "contribution_points": round(contribution, 1),
                "direction": direction,
                "plain_language": plain_lang
            })
        
        # Sort by absolute contribution
        explanations.sort(key=lambda x: abs(x["contribution_points"]), reverse=True)
        
        return explanations[:5]  # Top 5 explanations
    
    def _pretty_feature_name(self, feature_name: str) -> str:
        """Convert feature name to human-readable format"""
        mapping = {
            "upi_inflow_regularity": "UPI inflow regularity",
            "upi_emi_history": "EMI payment history",
            "upi_balance_trend": "Bank balance trend",
            "telecom_consistency": "Phone bill payments",
            "telecom_missed_payments": "Missed bill payments",
            "ecommerce_return_rate": "E-commerce return rate",
            "ecommerce_emi_ratio": "EMI purchase ratio",
            "geolocation_stability": "Address stability",
            "relocation_count": "Recent relocations",
            "questionnaire_score": "Financial responsibility",
            "merchant_gst_regularity": "GST filing regularity",
            "merchant_fulfillment_rate": "Order fulfillment rate"
        }
        return mapping.get(feature_name, feature_name)
    
    def _generate_explanation(self, feature_name: str, value: float, direction: str) -> str:
        """Generate plain language explanation for a feature"""
        if feature_name == "telecom_consistency":
            months_on_time = int(value * 24)
            return f"You paid {months_on_time} out of 24 phone bills on time"
        elif feature_name == "telecom_missed_payments":
            count = int(value * 10)
            return f"You missed approximately {count} bill payments"
        elif feature_name == "questionnaire_score":
            pct = int(value * 100)
            return f"Your questionnaire responses show {pct}% financial responsibility indicators"
        elif feature_name == "geolocation_stability":
            months = int(value * 36)
            return f"Stable address for approximately {months} months"
        elif feature_name == "upi_inflow_regularity":
            pct = int(value * 100)
            return f"Regular income pattern detected in {pct}% of months"
        elif feature_name == "ecommerce_return_rate":
            pct = int(value * 100)
            return f"E-commerce return rate of {pct}%"
        else:
            return f"{feature_name.replace('_', ' ').title()}: {value:.2f}"
    
    def save_models(self):
        """Save trained models to disk"""
        os.makedirs(self.model_path, exist_ok=True)
        
        if self.tier1_model:
            joblib.dump(self.tier1_model, os.path.join(self.model_path, "tier1_model.pkl"))
        if self.tier2_model:
            joblib.dump(self.tier2_model, os.path.join(self.model_path, "tier2_model.pkl"))
        if self.calibrator:
            joblib.dump(self.calibrator, os.path.join(self.model_path, "calibrator.pkl"))
        
        print(f"Models saved to {self.model_path}")
    
    def load_models(self):
        """Load trained models from disk"""
        if os.path.exists(os.path.join(self.model_path, "tier1_model.pkl")):
            self.tier1_model = joblib.load(os.path.join(self.model_path, "tier1_model.pkl"))
        if os.path.exists(os.path.join(self.model_path, "tier2_model.pkl")):
            self.tier2_model = joblib.load(os.path.join(self.model_path, "tier2_model.pkl"))
        if os.path.exists(os.path.join(self.model_path, "calibrator.pkl")):
            self.calibrator = joblib.load(os.path.join(self.model_path, "calibrator.pkl"))
        
        self.is_trained = True
        print("Models loaded successfully")


# Quick test
if __name__ == "__main__":
    from data_generator import SyntheticDataGenerator
    
    # Generate training data
    generator = SyntheticDataGenerator()
    dataset = generator.generate_dataset(500)
    labels = [generator.calculate_true_default_risk(user) > 0.5 for user in dataset]
    
    # Train model
    engine = ScoringEngine()
    engine.train(dataset, labels)
    
    # Test on a new user
    test_user = generator.generate_user_profile("individual")
    score, band = engine.calculate_score(test_user)
    explanations = engine.get_shap_explanations(test_user, score)
    
    print(f"\nTest User Score: {score} ({band})")
    print("\nTop Explanations:")
    for exp in explanations[:3]:
        sign = "+" if exp["direction"] == "positive" else "-"
        print(f"  {sign} {exp['feature_name']}: {exp['contribution_points']} pts")
        print(f"    → {exp['plain_language']}")
