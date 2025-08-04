# api_integration_guide.py
# API documentation and integration guide for Strive Pro Phase 2

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import jwt
from dataclasses import asdict

# Import Strive Pro components
from multi_user_management import DatabaseManager, AuthenticationManager, UserRole
from ml_predictive_models import PsychologicalMLEngine, PersonalizedInterventionEngine
from advanced_reporting_system import PDFReportGenerator, ReportConfig

# API Models
class UserRegistration(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(default="user", regex=r'^(user|hr_manager|clinician|admin)$')
    department: Optional[str] = Field(None, max_length=100)
    organization_id: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class AssessmentSubmission(BaseModel):
    assessment_type: str = Field(..., regex=r'^(pss10|dass21|burnout|worklife|jobsat)$')
    answers: List[int] = Field(..., min_items=1, max_items=50)
    user_context: Optional[str] = Field(None, max_length=1000)

class MLPredictionRequest(BaseModel):
    user_data: Dict[str, Any]
    assessment_scores: Optional[Dict[str, int]] = None

class ReportRequest(BaseModel):
    assessment_data: Dict[str, int]
    user_profile: Dict[str, str]
    ml_predictions: Dict[str, Any]
    report_type: str = Field(default="comprehensive", regex=r'^(comprehensive|summary|clinical)$')
    include_charts: bool = True
    include_recommendations: bool = True

# Initialize API
app = FastAPI(
    title="Strive Pro Phase 2 API",
    description="Advanced Psychological Assessment Platform API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize components
db_manager = DatabaseManager()
auth_manager = AuthenticationManager(db_manager)
ml_engine = PsychologicalMLEngine()
intervention_engine = PersonalizedInterventionEngine(ml_engine)
pdf_generator = PDFReportGenerator()

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user from JWT token"""
    try:
        payload = auth_manager.verify_jwt_token(credentials.credentials)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

# Health check endpoint
@app.get("/health")
async def health_check():
    """System health check endpoint"""
    from health_check import check_system_health
    
    health_status = check_system_health()
    
    if health_status["status"] == "healthy":
        return health_status
    else:
        raise HTTPException(status_code=503, detail=health_status)

# Authentication endpoints
@app.post("/auth/register")
async def register_user(user_data: UserRegistration):
    """Register a new user"""
    try:
        role = UserRole(user_data.role)
        
        success = auth_manager.register_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            role=role,
            organization_id=user_data.organization_id,
            department=user_data.department
        )
        
        if success:
            return {"message": "User registered successfully", "username": user_data.username}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists"
            )
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/auth/login")
async def login_user(login_data: UserLogin):
    """Authenticate user and return JWT token"""
    try:
        token = auth_manager.login(login_data.username, login_data.password)
        
        if token:
            # Get user details
            user = db_manager.get_user_by_username(login_data.username)
            return {
                "access_token": token,
                "token_type": "bearer",
                "user_id": user.user_id,
                "username": user.username,
                "role": user.role.value,
                "expires_in": 86400  # 24 hours
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/auth/refresh")
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """Refresh JWT token"""
    try:
        user = db_manager.get_user_by_username(current_user["username"])
        if user:
            new_token = auth_manager.create_jwt_token(user)
            return {
                "access_token": new_token,
                "token_type": "bearer",
                "expires_in": 86400
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Assessment endpoints
@app.post("/assessments/submit")
async def submit_assessment(
    assessment: AssessmentSubmission,
    current_user: dict = Depends(get_current_user)
):
    """Submit assessment answers and get comprehensive analysis"""
    try:
        # Process assessment based on type
        if assessment.assessment_type == "pss10":
            score = calculate_pss10_score(assessment.answers)
            max_score = 40
        elif assessment.assessment_type == "dass21":
            scores = calculate_dass21_scores(assessment.answers)
            score = sum(scores.values())
            max_score = 126  # 42 per dimension * 3
        else:
            # For other assessments, use generic scoring
            score = sum(assessment.answers)
            max_score = len(assessment.answers) * 4
        
        # Get ML prediction
        user_data = {
            'age': 32,  # Would get from user profile
            'prev_pss10': score if assessment.assessment_type == "pss10" else 15,
            'work_hours_per_week': 45,
            'sleep_hours': 7,
            'exercise_frequency': 2,
            'social_support': 6
        }
        
        ml_prediction = ml_engine.predict_risk_assessment(user_data)
        
        # Get personalized interventions
        interventions = intervention_engine.recommend_personalized_interventions(
            user_data, {assessment.assessment_type: score}
        )
        
        # Save to database
        from multi_user_management import AssessmentRecord
        import uuid
        
        record = AssessmentRecord(
            record_id=str(uuid.uuid4()),
            user_id=current_user["user_id"],
            organization_id=current_user.get("organization_id"),
            assessment_type=assessment.assessment_type,
            scores={assessment.assessment_type: score},
            risk_level=ml_prediction.risk_level,
            recommendations=ml_prediction.recommendations,
            completed_at=datetime.now(),
            follow_up_date=datetime.now() + timedelta(days=30),
            notes=assessment.user_context
        )
        
        db_manager.save_assessment_record(record)
        
        return {
            "assessment_id": record.record_id,
            "score": score,
            "max_score": max_score,
            "risk_level": ml_prediction.risk_level,
            "confidence": ml_prediction.confidence,
            "key_factors": ml_prediction.factors,
            "recommendations": ml_prediction.recommendations,
            "personalized_interventions": [asdict(i) for i in interventions[:5]],
            "follow_up_date": record.follow_up_date.isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/assessments/history")
async def get_assessment_history(
    limit: int = 10,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Get user's assessment history"""
    try:
        assessments = db_manager.get_user_assessments(current_user["user_id"])
        
        # Apply pagination
        paginated_assessments = assessments[offset:offset + limit]
        
        return {
            "assessments": [
                {
                    "id": a.record_id,
                    "type": a.assessment_type,
                    "scores": a.scores,
                    "risk_level": a.risk_level,
                    "completed_at": a.completed_at.isoformat(),
                    "follow_up_date": a.follow_up_date.isoformat() if a.follow_up_date else None
                }
                for a in paginated_assessments
            ],
            "total": len(assessments),
            "limit": limit,
            "offset": offset
        }
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# ML endpoints
@app.post("/ml/predict")
async def get_ml_prediction(
    request: MLPredictionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Get ML-powered risk assessment and predictions"""
    try:
        # Get risk prediction
        ml_prediction = ml_engine.predict_risk_assessment(request.user_data)
        
        # Get stress trajectory if assessment scores provided
        trajectory = None
        if request.assessment_scores:
            trajectory = ml_engine.predict_stress_trajectory(request.user_data, 12)
        
        # Get intervention outcomes
        intervention_outcomes = None
        if request.assessment_scores:
            sample_interventions = ["mindfulness meditation", "exercise program", "therapy"]
            intervention_outcomes = ml_engine.predict_intervention_outcomes(
                request.user_data, sample_interventions
            )
        
        return {
            "risk_assessment": asdict(ml_prediction),
            "stress_trajectory": trajectory,
            "intervention_outcomes": intervention_outcomes
        }
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/ml/interventions")
async def get_personalized_interventions(
    assessment_scores: str,  # JSON string of scores
    current_user: dict = Depends(get_current_user)
):
    """Get personalized intervention recommendations"""
    try:
        scores = json.loads(assessment_scores)
        
        user_data = {
            'age': 32,  # Would get from user profile
            'prev_pss10': scores.get('pss10', 15),
            'work_hours_per_week': 45,
            'sleep_hours': 7
        }
        
        interventions = intervention_engine.recommend_personalized_interventions(
            user_data, scores, max_recommendations=10
        )
        
        return {
            "interventions": [asdict(i) for i in interventions]
        }
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Reporting endpoints
@app.post("/reports/generate")
async def generate_report(
    request: ReportRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate comprehensive PDF report"""
    try:
        config = ReportConfig(
            include_charts=request.include_charts,
            include_recommendations=request.include_recommendations,
            report_type=request.report_type
        )
        
        pdf_bytes = pdf_generator.generate_comprehensive_report(
            request.assessment_data,
            request.user_profile,
            request.ml_predictions,
            config
        )
        
        # In a real implementation, you might save this to a file server
        # and return a download URL instead of the raw bytes
        
        import base64
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        return {
            "report_id": f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "pdf_data": pdf_base64,
            "file_size": len(pdf_bytes),
            "generated_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Organization endpoints (for admin/HR roles)
@app.get("/organization/analytics")
async def get_organization_analytics(
    current_user: dict = Depends(get_current_user)
):
    """Get organization-level analytics (admin/HR only)"""
    if current_user["role"] not in ["admin", "hr_manager", "org_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    try:
        from multi_user_management import OrganizationAnalytics
        
        org_analytics = OrganizationAnalytics(db_manager)
        org_id = current_user.get("organization_id", "default")
        
        overview = org_analytics.get_organization_overview(org_id)
        
        return overview
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/organization/users")
async def get_organization_users(
    current_user: dict = Depends(get_current_user)
):
    """Get organization users (admin only)"""
    if current_user["role"] not in ["admin", "org_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    try:
        # This would be implemented in the database manager
        # For now, return a placeholder
        return {
            "users": [],
            "total": 0,
            "message": "User listing functionality to be implemented"
        }
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Utility functions
def calculate_pss10_score(answers: List[int]) -> int:
    """Calculate PSS-10 score"""
    reversed_indices = [3, 4, 6, 7]
    total_score = 0
    
    for i, score in enumerate(answers):
        if i in reversed_indices:
            total_score += (4 - score)
        else:
            total_score += score
    
    return total_score

def calculate_dass21_scores(answers: List[int]) -> Dict[str, int]:
    """Calculate DASS-21 subscale scores"""
    depression_items = list(range(0, 21, 3))  # Items 0, 3, 6, 9, 12, 15, 18
    anxiety_items = list(range(1, 21, 3))     # Items 1, 4, 7, 10, 13, 16, 19
    stress_items = list(range(2, 21, 3))      # Items 2, 5, 8, 11, 14, 17, 20
    
    scores = {
        "depression": sum(answers[i] for i in depression_items) * 2,
        "anxiety": sum(answers[i] for i in anxiety_items) * 2,
        "stress": sum(answers[i] for i in stress_items) * 2
    }
    
    return scores

# WebSocket endpoints for real-time features (optional)
from fastapi import WebSocket

@app.websocket("/ws/progress")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time progress updates"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Handle real-time progress updates
            await websocket.send_text(f"Progress update: {data}")
    except Exception as e:
        print(f"WebSocket error: {e}")

# API Documentation
API_INTEGRATION_GUIDE = """
# Strive Pro Phase 2 API Integration Guide

## Overview
The Strive Pro Phase 2 API provides comprehensive access to psychological assessment, ML predictions, and reporting features.

## Base URL
- Development: `http://localhost:8000`
- Production: `https://your-domain.com/api`

## Authentication
All endpoints (except `/health` and `/auth/*`) require JWT authentication:

```python
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}
```

## Quick Start Example

### Python Client
```python
import requests
import json

# Base configuration
BASE_URL = "http://localhost:8000"
headers = {"Content-Type": "application/json"}

# 1. Register user
registration_data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!",
    "full_name": "Test User",
    "role": "user"
}

response = requests.post(f"{BASE_URL}/auth/register", 
                        json=registration_data, headers=headers)
print("Registration:", response.json())

# 2. Login
login_data = {
    "username": "testuser",
    "password": "SecurePass123!"
}

response = requests.post(f"{BASE_URL}/auth/login", 
                        json=login_data, headers=headers)
auth_data = response.json()
access_token = auth_data["access_token"]

# Update headers with token
auth_headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# 3. Submit assessment
assessment_data = {
    "assessment_type": "pss10",
    "answers": [2, 3, 2, 1, 1, 3, 2, 1, 2, 3],
    "user_context": "Feeling stressed at work lately"
}

response = requests.post(f"{BASE_URL}/assessments/submit",
                        json=assessment_data, headers=auth_headers)
result = response.json()
print("Assessment Result:", result)

# 4. Get ML predictions
ml_request = {
    "user_data": {
        "age": 30,
        "work_hours_per_week": 45,
        "sleep_hours": 6,
        "exercise_frequency": 2
    },
    "assessment_scores": {"pss10": result["score"]}
}

response = requests.post(f"{BASE_URL}/ml/predict",
                        json=ml_request, headers=auth_headers)
predictions = response.json()
print("ML Predictions:", predictions)

# 5. Generate report
report_request = {
    "assessment_data": {"pss10": result["score"]},
    "user_profile": {"name": "Test User", "role": "user"},
    "ml_predictions": predictions["risk_assessment"],
    "report_type": "comprehensive"
}

response = requests.post(f"{BASE_URL}/reports/generate",
                        json=report_request, headers=auth_headers)
report = response.json()
print("Report generated:", report["report_id"])
```

### JavaScript Client
```javascript
class StrivePro2Client {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
        this.accessToken = null;
    }
    
    async login(username, password) {
        const response = await fetch(`${this.baseUrl}/auth/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, password})
        });
        
        const data = await response.json();
        this.accessToken = data.access_token;
        return data;
    }
    
    async submitAssessment(assessmentType, answers, userContext = '') {
        const response = await fetch(`${this.baseUrl}/assessments/submit`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.accessToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                assessment_type: assessmentType,
                answers: answers,
                user_context: userContext
            })
        });
        
        return await response.json();
    }
    
    async getMLPredictions(userData, assessmentScores) {
        const response = await fetch(`${this.baseUrl}/ml/predict`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.accessToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_data: userData,
                assessment_scores: assessmentScores
            })
        });
        
        return await response.json();
    }
}

// Usage
const client = new StrivePro2Client();
await client.login('testuser', 'password');
const result = await client.submitAssessment('pss10', [2,3,2,1,1,3,2,1,2,3]);
console.log('Assessment result:', result);
```

## Rate Limiting
- Authentication endpoints: 10 requests per minute
- Assessment endpoints: 100 requests per hour
- ML prediction endpoints: 50 requests per hour
- Report generation: 20 requests per hour

## Error Handling
All errors follow standard HTTP status codes:
- 400: Bad Request (validation errors)
- 401: Unauthorized (invalid/expired token)
- 403: Forbidden (insufficient permissions)
- 404: Not Found
- 422: Validation Error
- 500: Internal Server Error

Error response format:
```json
{
    "detail": "Error message",
    "error_code": "SPECIFIC_ERROR_CODE",
    "timestamp": "2024-01-01T00:00:00Z"
}
```

## Webhooks (Future Feature)
Configure webhook endpoints to receive real-time notifications:
- Assessment completed
- High-risk detection
- Report generated

## SDK Development
Consider developing SDKs for popular languages:
- Python SDK: `pip install strive-pro-sdk`
- JavaScript SDK: `npm install strive-pro-js`
- R SDK: `install.packages("strivepro")`

## Testing
Use the provided test endpoints for development:
```bash
# Health check
curl http://localhost:8000/health

# API documentation
curl http://localhost:8000/docs
```

For more detailed documentation, visit `/docs` or `/redoc` endpoints.
"""

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Strive Pro Phase 2 API Server...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 ReDoc Documentation: http://localhost:8000/redoc")
    
    uvicorn.run(
        "api_integration_guide:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )