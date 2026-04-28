"""
Pydantic models for IntelliCredit API
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ConsentSource(str, Enum):
    UPI_BANK = "upi_bank"
    TELECOM = "telecom"
    ECOMMERCE = "ecommerce"
    GEOLOCATION = "geolocation"
    QUESTIONNAIRE = "questionnaire"
    MERCHANT_GST = "merchant_gst"


class ConsentRequest(BaseModel):
    user_id: str
    source: ConsentSource
    granted: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ConsentResponse(BaseModel):
    user_id: str
    source: ConsentSource
    granted: bool
    timestamp: datetime


class QuestionnaireAnswer(BaseModel):
    question_id: int
    answer: str
    confidence: float = Field(ge=0.0, le=1.0)


class QuestionnaireSubmit(BaseModel):
    user_id: str
    answers: List[QuestionnaireAnswer]


class UserDataUPI(BaseModel):
    monthly_inflow_avg: float
    inflow_regularity: float = Field(ge=0.0, le=1.0)
    emi_payment_history: float = Field(ge=0.0, le=1.0)
    balance_trend: float = Field(ge=-1.0, le=1.0)
    months_of_data: int


class UserDataTelecom(BaseModel):
    payment_consistency_24m: float = Field(ge=0.0, le=1.0)
    missed_payments_count: int
    average_bill_amount: float
    tenure_months: int


class UserDataEcommerce(BaseModel):
    return_rate: float = Field(ge=0.0, le=1.0)
    basket_growth_yoy: float
    emi_purchase_ratio: float = Field(ge=0.0, le=1.0)
    purchase_frequency: float
    months_active: int


class UserDataGeolocation(BaseModel):
    district_stability_months: int
    home_work_distance_km: float
    relocation_count_12m: int
    # Note: No GPS coordinates stored - district level only


class UserDataMerchant(BaseModel):
    business_tenure_months: int
    gst_filing_regularity: float = Field(ge=0.0, le=1.0)
    fulfillment_rate: float = Field(ge=0.0, le=1.0)
    customer_rating_avg: float = Field(ge=0.0, le=5.0)
    monthly_revenue_avg: float


class DataSubmission(BaseModel):
    user_id: str
    upi_bank: Optional[UserDataUPI] = None
    telecom: Optional[UserDataTelecom] = None
    ecommerce: Optional[UserDataEcommerce] = None
    geolocation: Optional[UserDataGeolocation] = None
    questionnaire: Optional[List[QuestionnaireAnswer]] = None
    merchant_gst: Optional[UserDataMerchant] = None


class ScoreBand(str, Enum):
    EXCELLENT = "excellent"  # 750-850
    GOOD = "good"  # 650-749
    FAIR = "fair"  # 550-649
    POOR = "poor"  # 450-549
    NOT_ELIGIBLE = "not_eligible"  # < 450


class SHAPExplanation(BaseModel):
    feature_name: str
    contribution_points: float
    direction: str  # "positive" or "negative"
    plain_language: str


class ScoringResult(BaseModel):
    user_id: str
    score: int = Field(ge=0, le=850)
    band: ScoreBand
    tier: int  # 1 or 2
    data_completeness: float = Field(ge=0.0, le=1.0)
    shap_explanations: List[SHAPExplanation]
    contradictions_flagged: List[str]
    fairness_audit_passed: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "score": 720,
                "band": "good",
                "tier": 2,
                "data_completeness": 0.85,
                "shap_explanations": [
                    {
                        "feature_name": "Phone bill payments",
                        "contribution_points": 89,
                        "direction": "positive",
                        "plain_language": "You paid 23 out of 24 phone bills on time in the last 24 months"
                    }
                ],
                "contradictions_flagged": [],
                "fairness_audit_passed": True
            }
        }


class RAGQuery(BaseModel):
    user_id: str
    question: str
    context_score: Optional[int] = None


class RAGResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence: float
    follow_up_suggestions: List[str]


class ImprovementPlan(BaseModel):
    current_score: int
    target_score: int
    timeline_months: int
    actions: List[Dict[str, Any]]
    estimated_score_gain: int


class UserCreate(BaseModel):
    user_id: str
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    user_type: str = Field(default="individual", pattern="^(individual|msme)$")


class UserResponse(BaseModel):
    user_id: str
    name: str
    email: Optional[str]
    phone: Optional[str]
    user_type: str
    created_at: datetime
    consents_granted: List[ConsentSource]
    latest_score: Optional[int] = None
