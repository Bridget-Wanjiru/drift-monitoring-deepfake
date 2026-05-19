"""
Pydantic Models - Request/Response Schemas
Defines data structure for API inputs and outputs
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime


class FeatureInput(BaseModel):
    """
    Input from Classifier (Microservice 4)
    This is what your API receives for each video
    """
    video_id: str = Field(..., description="Unique video identifier")
    timestamp: str = Field(..., description="ISO timestamp when video was processed")
    features: List[float] = Field(..., description="16-dimensional feature vector")
    prediction: str = Field(..., description="Classifier prediction: 'real' or 'fake'")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    
    @validator('features')
    def validate_features(cls, v):
        """Ensure exactly 16 features"""
        if len(v) != 16:
            raise ValueError(f"Expected 16 features, got {len(v)}")
        return v
    
    @validator('prediction')
    def validate_prediction(cls, v):
        """Ensure prediction is 'real' or 'fake'"""
        if v.lower() not in ['real', 'fake']:
            raise ValueError(f"Prediction must be 'real' or 'fake', got '{v}'")
        return v.lower()
    
    class Config:
        schema_extra = {
            "example": {
                "video_id": "uuid-88a",
                "timestamp": "2026-03-22T14:30:00Z",
                "features": [0.23, -0.45, 0.12, 0.89, -0.34, 0.56, 0.78, -0.12,
                            0.45, 0.67, -0.23, 0.91, 0.34, -0.67, 0.12, 0.89],
                "prediction": "fake",
                "confidence": 0.87
            }
        }


class BatchProgressResponse(BaseModel):
    """Response after adding features to batch"""
    status: str
    batch_progress: dict
    drift_metrics: Optional[dict] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "batch_progress": {
                    "current_count": 347,
                    "batch_size": 1000,
                    "percentage": 34.7,
                    "drift_calculated": False
                }
            }
        }


class ReliabilityResponse(BaseModel):
    """
    Response for Frontend
    This is what displays the colored badge to users
    """
    reliability: str = Field(..., description="HIGH, MODERATE, or CAUTION")
    psi: Optional[float] = Field(None, description="Current PSI value")
    badge_color: str = Field(..., description="green, yellow, red, or gray")
    badge_text: str = Field(..., description="Text to display on badge")
    show_user_message: bool = Field(..., description="Whether to show warning message")
    user_message: str = Field(..., description="Warning message for users")
    last_check: Optional[str] = Field(None, description="ISO timestamp of last drift calculation")
    videos_in_current_batch: int = Field(..., description="Videos collected so far")
    total_batches_analyzed: int = Field(..., description="Number of complete batches processed")
    
    class Config:
        schema_extra = {
            "example": {
                "reliability": "MODERATE",
                "psi": 0.28,
                "badge_color": "yellow",
                "badge_text": "Caution: Unusual Patterns Detected",
                "show_user_message": True,
                "user_message": "Our system is encountering videos with characteristics...",
                "last_check": "2026-03-22T14:30:00Z",
                "videos_in_current_batch": 347,
                "total_batches_analyzed": 12
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    timestamp: str
    batch_progress: dict
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "service": "drift_monitor",
                "timestamp": "2026-03-22T14:30:00Z",
                "batch_progress": {
                    "current_count": 347,
                    "batch_size": 1000
                }
            }
        }