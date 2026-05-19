"""
FastAPI Application - Drift Monitoring Microservice
REST API for receiving Classifier outputs and providing system reliability status
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

from api.models import (
    FeatureInput,
    BatchProgressResponse,
    ReliabilityResponse,
    HealthResponse
)
from monitoring_framework import MonitoringFramework

# ============================================================
# Initialize FastAPI App
# ============================================================

app = FastAPI(
    title="Drift Monitoring API",
    description="Microservice 5: Monitors distributional drift in deepfake detection system",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc"  # ReDoc at /redoc
)

# CORS middleware (allow Frontend to call this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize Monitoring Framework (Global State)


monitoring = None

@app.on_event("startup")
async def startup_event():
    """Initialize monitoring framework on startup"""
    global monitoring
    monitoring = MonitoringFramework(
        reference_path='data/reference/train_features.npy',
        batch_size=1000
    )
    print(" Drift Monitoring API started")
    print(f"  Batch size: {monitoring.batch_size}")
    print(f"  Reference samples: {monitoring.detector.n_samples}")



# API Endpoints

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with API information"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Drift Monitoring API</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                max-width: 800px; 
                margin: 50px auto; 
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #2c3e50; }
            .endpoint { 
                background: #ecf0f1; 
                padding: 15px; 
                margin: 10px 0; 
                border-radius: 5px;
                font-family: monospace;
            }
            .method { 
                display: inline-block;
                padding: 3px 8px;
                border-radius: 3px;
                font-weight: bold;
                margin-right: 10px;
            }
            .post { background: #3498db; color: white; }
            .get { background: #2ecc71; color: white; }
            a { color: #3498db; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 Drift Monitoring API</h1>
            <p><strong>Microservice 5</strong> - Deepfake Detection System</p>
            <p>Monitors distributional drift in Meta-Learning Classifier outputs</p>
            
            <h2>API Endpoints</h2>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/api/drift/collect-features</strong>
                <br>Receive features from Classifier (Microservice 4)
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/system-reliability</strong>
                <br>Get current drift status for Frontend
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/health</strong>
                <br>Health check for orchestrator
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/admin/drift-dashboard</strong>
                <br>Admin dashboard with drift trends
            </div>
            
            <h2>Documentation</h2>
            <p>
                <a href="/docs">📘 Swagger UI (Interactive API Docs)</a><br>
                <a href="/redoc">📗 ReDoc (Alternative Docs)</a>
            </p>
            
            <h2>Status</h2>
            <p>✓ API Running</p>
            <p>✓ Monitoring Framework Active</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post(
    "/api/drift/collect-features",
    response_model=BatchProgressResponse,
    status_code=status.HTTP_200_OK,
    summary="Collect features from Classifier",
    description="Receives 16-dim feature vector from Microservice 4 (Meta-Learning Classifier)"
)
async def collect_features(data: FeatureInput):
    """
    Endpoint called by Classifier for each processed video
    
    Workflow:
    1. Receive 16-dim features from Classifier
    2. Add to batch buffer
    3. If batch reaches 1000 → Calculate drift
    4. Return batch progress
    """
    try:
        # Add features to monitoring framework
        response = monitoring.add_features(
            features=data.features,
            video_id=data.video_id,
            prediction=data.prediction,
            confidence=data.confidence
        )
        
        return BatchProgressResponse(**response)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error: {str(e)}"
        )


@app.get(
    "/api/system-reliability",
    response_model=ReliabilityResponse,
    status_code=status.HTTP_200_OK,
    summary="Get system reliability status",
    description="Returns current drift status for Frontend to display colored badge"
)
async def get_system_reliability():
    """
    Endpoint called by Frontend to display reliability badge
    
    Returns:
    - Badge color (green/yellow/red)
    - Badge text
    - User warning message
    - Current PSI value
    """
    try:
        status_data = monitoring.get_reliability_status()
        return ReliabilityResponse(**status_data)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving status: {str(e)}"
        )


@app.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Used by orchestrator to check if service is running"
)
async def health_check():
    """
    Health check endpoint for monitoring/orchestration
    """
    return HealthResponse(
        status="healthy",
        service="drift_monitor",
        timestamp=datetime.now().isoformat(),
        batch_progress={
            "current_count": len(monitoring.feature_buffer),
            "batch_size": monitoring.batch_size
        }
    )


@app.get(
    "/admin/drift-dashboard",
    response_class=HTMLResponse,
    summary="Admin dashboard",
    description="Visual dashboard showing drift trends over time"
)
async def drift_dashboard():
    """
    Admin dashboard with PSI trends, drift history, and recommendations
    (Full implementation in next step)
    """
    # Placeholder - will implement full dashboard in Step 12
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Drift Dashboard</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                max-width: 1200px; 
                margin: 20px auto; 
                padding: 20px;
            }
            h1 { color: #2c3e50; }
            .status-box {
                background: #ecf0f1;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <h1>Drift Monitoring Dashboard</h1>
        <div class="status-box">
            <h2>Current Status</h2>
            <p><strong>Reliability:</strong> {reliability}</p>
            <p><strong>PSI:</strong> {psi}</p>
            <p><strong>Batches Analyzed:</strong> {batches}</p>
        </div>
        <p><em>Full dashboard with charts coming in next step...</em></p>
    </body>
    </html>
    """.format(
        reliability=monitoring.current_reliability,
        psi=f"{monitoring.current_psi:.4f}" if monitoring.current_psi else "N/A",
        batches=monitoring.batch_count
    )
    return HTMLResponse(content=html_content)


@app.post(
    "/admin/reset-batch",
    status_code=status.HTTP_200_OK,
    summary="Reset batch buffer (Admin only)",
    description="Clears current batch buffer - use for testing"
)
async def reset_batch():
    """
    Admin endpoint to reset batch buffer
    Useful during testing/debugging
    """
    old_count = len(monitoring.feature_buffer)
    monitoring.feature_buffer = []
    
    return {
        "status": "success",
        "message": f"Batch buffer reset. Cleared {old_count} features.",
        "new_count": 0
    }


# Run Server (for development)

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=5001,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )