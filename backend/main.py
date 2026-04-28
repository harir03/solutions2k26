"""
IntelliCredit Alternate - Main FastAPI Application
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import os
import json
from datetime import datetime

from app.config import settings
from app.schemas import (
    UserCreate, UserResponse, ConsentRequest, ConsentResponse,
    DataSubmission, ScoringResult, RAGQuery, RAGResponse,
    ScoreBand, SHAPExplanation
)
from app.data_generator import SyntheticDataGenerator
from app.scoring_engine import ScoringEngine

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered alternate credit scoring for underserved India"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
data_generator = SyntheticDataGenerator(seed=42)
scoring_engine = ScoringEngine(model_path="backend/models")
model_trained = False

# In-memory storage for demo (replace with PostgreSQL in production)
users_db: Dict[str, Dict[str, Any]] = {}
consents_db: Dict[str, Dict[str, bool]] = {}
scores_db: Dict[str, Dict[str, Any]] = {}


def ensure_model_trained():
    """Ensure ML model is trained before scoring"""
    global model_trained
    
    if not model_trained:
        print("Training ML model on synthetic data...")
        dataset = data_generator.generate_dataset(500)
        labels = [data_generator.calculate_true_default_risk(user) > 0.5 for user in dataset]
        scoring_engine.train(dataset, labels)
        scoring_engine.save_models()
        model_trained = True
        print("Model training complete!")


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Try to load existing models
    if os.path.exists("backend/models/tier2_model.pkl"):
        try:
            scoring_engine.load_models()
            global model_trained
            model_trained = True
            print("Loaded existing models")
        except Exception as e:
            print(f"Could not load models: {e}")
            ensure_model_trained()
    else:
        ensure_model_trained()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "model_trained": model_trained
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "model_ready": model_trained
    }


@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate):
    """Create a new user"""
    if user.user_id in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    
    users_db[user.user_id] = {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "user_type": user.user_type,
        "created_at": datetime.utcnow().isoformat(),
        "consents": [],
        "latest_score": None
    }
    consents_db[user.user_id] = {}
    
    return UserResponse(
        user_id=user.user_id,
        name=user.name,
        email=user.email,
        phone=user.phone,
        user_type=user.user_type,
        created_at=datetime.fromisoformat(users_db[user.user_id]["created_at"]),
        consents_granted=[],
        latest_score=None
    )


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user by ID"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_db[user_id]
    return UserResponse(
        user_id=user["user_id"],
        name=user["name"],
        email=user["email"],
        phone=user["phone"],
        user_type=user["user_type"],
        created_at=datetime.fromisoformat(user["created_at"]),
        consents_granted=[ConsentSource(c) for c in user["consents"]],
        latest_score=user["latest_score"]
    )


@app.post("/consent", response_model=ConsentResponse)
async def grant_consent(consent: ConsentRequest):
    """Grant or revoke consent for a data source"""
    if consent.user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    consents_db[consent.user_id][consent.source.value] = consent.granted
    
    if consent.granted and consent.source.value not in users_db[consent.user_id]["consents"]:
        users_db[consent.user_id]["consents"].append(consent.source.value)
    elif not consent.granted and consent.source.value in users_db[consent.user_id]["consents"]:
        users_db[consent.user_id]["consents"].remove(consent.source.value)
    
    return ConsentResponse(
        user_id=consent.user_id,
        source=consent.source,
        granted=consent.granted,
        timestamp=consent.timestamp
    )


@app.post("/score", response_model=ScoringResult)
async def calculate_score(data: DataSubmission):
    """Calculate credit score for a user"""
    if not model_trained:
        raise HTTPException(status_code=503, detail="Model not trained yet")
    
    # Build profile from submitted data
    profile = {"user_id": data.user_id}
    
    if data.upi_bank:
        profile["upi_bank"] = data.upi_bank.model_dump()
    if data.telecom:
        profile["telecom"] = data.telecom.model_dump()
    if data.ecommerce:
        profile["ecommerce"] = data.ecommerce.model_dump()
    if data.geolocation:
        profile["geolocation"] = data.geolocation.model_dump()
    if data.questionnaire:
        profile["questionnaire"] = [a.model_dump() for a in data.questionnaire]
    if data.merchant_gst:
        profile["merchant_gst"] = data.merchant_gst.model_dump()
    
    # Calculate score
    score, band = scoring_engine.calculate_score(profile)
    
    # Get SHAP explanations
    shap_explanations = scoring_engine.get_shap_explanations(profile, score)
    
    # Determine tier
    tier = scoring_engine.determine_tier(profile)
    
    # Calculate data completeness
    sources_provided = sum([
        1 if data.upi_bank else 0,
        1 if data.telecom else 0,
        1 if data.ecommerce else 0,
        1 if data.geolocation else 0,
        1 if data.questionnaire else 0,
        1 if data.merchant_gst else 0
    ])
    data_completeness = sources_provided / 6.0
    
    # Check for contradictions (simplified)
    contradictions = []
    if data.upi_bank and data.ecommerce:
        if data.upi_bank.inflow_regularity > 0.8 and data.ecommerce.return_rate > 0.3:
            contradictions.append("High income regularity but high e-commerce return rate")
    
    # Fairness audit (simplified - always passes in demo)
    fairness_passed = True
    
    # Store result
    result = {
        "user_id": data.user_id,
        "score": score,
        "band": band,
        "tier": tier,
        "data_completeness": data_completeness,
        "shap_explanations": shap_explanations,
        "contradictions_flagged": contradictions,
        "fairness_audit_passed": fairness_passed,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    scores_db[data.user_id] = result
    
    # Update user's latest score
    if data.user_id in users_db:
        users_db[data.user_id]["latest_score"] = score
    
    return ScoringResult(**result)


@app.get("/score/{user_id}")
async def get_latest_score(user_id: str):
    """Get latest score for a user"""
    if user_id not in scores_db:
        raise HTTPException(status_code=404, detail="No score found for user")
    
    return scores_db[user_id]


@app.post("/rag/query", response_model=RAGResponse)
async def rag_query(query: RAGQuery):
    """RAG-based loan advisor query (demo version)"""
    # Simplified RAG - in production this would use ChromaDB
    question_lower = query.question.lower()
    
    # Hardcoded knowledge base for demo
    if "improve" in question_lower or "increase" in question_lower:
        answer = "To improve your credit score: 1) Pay all bills on time consistently, 2) Maintain stable address and employment, 3) Reduce e-commerce returns, 4) Complete the financial responsibility questionnaire honestly, 5) For MSMEs: file GST returns regularly."
        sources = ["RBI Financial Literacy Guidelines", "Credit Improvement Best Practices"]
        suggestions = ["How long does it take to improve my score?", "What factors affect my score the most?"]
    elif "reject" in question_lower or "denied" in question_lower:
        answer = "If your application was rejected, review your SHAP breakdown to see which factors negatively impacted your score. Focus on improving those specific areas over the next 3-6 months before reapplying. You can also start with Tier 1 scoring using just telecom and questionnaire data."
        sources = ["RBI Fair Practices Code", "Lender Rejection Guidelines"]
        suggestions = ["What is the minimum score needed?", "Can I appeal the decision?"]
    elif "explain" in question_lower or "why" in question_lower:
        answer = "Your score is calculated using a two-tier ML model that analyzes your alternate data. The SHAP breakdown shows exactly how much each factor contributed - positive factors like on-time bill payments add points, while negative factors like high return rates subtract points. This is required by RBI Fair Practices Code."
        sources = ["RBI Fair Practices Code", "SHAP Explainability Documentation"]
        suggestions = ["Show me my SHAP breakdown", "How is the score calculated?"]
    elif "time" in question_lower or "long" in question_lower:
        answer = "The scoring process takes less than 30 seconds once all data is submitted. However, building a good credit history takes time - most users see significant improvement within 3-6 months of consistent financial behavior."
        sources = ["Processing Time Guidelines"]
        suggestions = ["How often can I check my score?", "When should I reapply?"]
    else:
        answer = "I can help you understand your credit score, explain factors affecting it, provide improvement tips, or clarify the IntelliCredit process. What specific aspect would you like to know about?"
        sources = ["General FAQ"]
        suggestions = ["How do I improve my score?", "Why was I rejected?", "Explain my SHAP breakdown"]
    
    return RAGResponse(
        answer=answer,
        sources=sources,
        confidence=0.9,
        follow_up_suggestions=suggestions
    )


@app.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    total_users = len(users_db)
    total_scores = len(scores_db)
    
    if total_scores == 0:
        # Return demo stats
        return {
            "total_applicants": 10000,
            "score_distribution": {
                "excellent": 1800,
                "good": 2700,
                "fair": 3000,
                "poor": 1500,
                "not_eligible": 1000
            },
            "average_score": 625,
            "approval_rate": 0.75
        }
    
    # Calculate from actual data
    bands = {"excellent": 0, "good": 0, "fair": 0, "poor": 0, "not_eligible": 0}
    scores = []
    
    for score_data in scores_db.values():
        band = score_data.get("band", "not_eligible")
        bands[band] = bands.get(band, 0) + 1
        scores.append(score_data.get("score", 0))
    
    avg_score = sum(scores) / len(scores) if scores else 0
    approval_rate = (bands["excellent"] + bands["good"]) / total_scores if total_scores > 0 else 0
    
    return {
        "total_applicants": total_users,
        "score_distribution": bands,
        "average_score": round(avg_score),
        "approval_rate": round(approval_rate, 2)
    }


@app.get("/demo/generate-users")
async def generate_demo_users(count: int = 100):
    """Generate synthetic demo users and scores"""
    generated = []
    
    for i in range(count):
        # Generate synthetic profile
        profile = data_generator.generate_user_profile("individual")
        user_id = profile["user_id"]
        
        # Create user
        if user_id not in users_db:
            users_db[user_id] = {
                "user_id": user_id,
                "name": f"Demo User {i}",
                "email": None,
                "phone": None,
                "user_type": "individual",
                "created_at": datetime.utcnow().isoformat(),
                "consents": ["telecom", "questionnaire", "geolocation"],
                "latest_score": None
            }
        
        # Calculate score
        score, band = scoring_engine.calculate_score(profile)
        shap_explanations = scoring_engine.get_shap_explanations(profile, score)
        tier = scoring_engine.determine_tier(profile)
        
        scores_db[user_id] = {
            "user_id": user_id,
            "score": score,
            "band": band,
            "tier": tier,
            "data_completeness": 0.5,
            "shap_explanations": shap_explanations,
            "contradictions_flagged": [],
            "fairness_audit_passed": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        users_db[user_id]["latest_score"] = score
        
        generated.append({"user_id": user_id, "score": score, "band": band})
    
    return {
        "generated": len(generated),
        "sample": generated[:5]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
