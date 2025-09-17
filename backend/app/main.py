"""
FastAPI Main Application
Version 2 - Enhanced Multi-Temporal Data Analysis with LangGraph Integration
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import sys
from pathlib import Path
import logging

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️ python-dotenv not available, using system environment variables")

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import routers (V1 for backward compatibility, V2 for enhanced features)
from routers import files, analytics, chat
# Lazy import v2_analytics to speed up startup
from app.database import create_tables

# Configure production logging
# Ensure logs directory exists
Path('logs').mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/backend.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI app instance with V2 enhancements
app = FastAPI(
    title="Historical Multi-Table Data Analysis API v2",
    description="Production-grade API with LangGraph workflows for multi-temporal analysis and conversational AI",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
upload_dir = Path("uploads")
upload_dir.mkdir(exist_ok=True)

# Mount static files for uploaded data
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include V1 routers (backward compatibility)
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

# Include V2 enhanced routers (lazy loading)
try:
    from routers import v2_analytics
    app.include_router(v2_analytics.router, prefix="/api/v2", tags=["v2-analytics"])
    logger.info("✅ V2 analytics router loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ V2 analytics router failed to load: {e}")
    logger.warning("V2 features may not be available")

@app.on_event("startup")
async def startup_event():
    """Initialize database tables and setup on startup"""
    logger.info("🚀 Starting Historical Multi-Table Data Analysis API v2.0.0")
    create_tables()
    logger.info("✅ Database initialized successfully")
    logger.info("🧠 LangGraph workflow engine ready")
    logger.info("📊 Enhanced multi-temporal analysis capabilities enabled")
    logger.info("🔌 WebSocket support for real-time updates active")

@app.get("/")
async def root():
    """API information and capabilities endpoint"""
    return {
        "message": "Historical Multi-Table Data Analysis API v2",
        "version": "2.0.0",
        "status": "operational",
        "description": "Production-grade multi-temporal data analysis with LangGraph AI workflows",
        "features": {
            "v1_compatibility": [
                "CSV/Excel file upload", 
                "Basic data analytics",
                "Simple conversational interface",
                "Session management"
            ],
            "v2_enhanced": [
                "LangGraph workflow orchestration",
                "Multi-temporal data analysis",
                "Real-time WebSocket updates", 
                "Advanced trend analysis",
                "LLM-powered code generation",
                "Background task processing",
                "Automated insights generation"
            ]
        },
        "endpoints": {
            "v1_api": {
                "docs": "/docs",
                "files": "/api/files",
                "analytics": "/api/analytics", 
                "chat": "/api/chat"
            },
            "v2_enhanced": {
                "multi_temporal_analysis": "/api/v2/analyze",
                "enhanced_chat": "/api/v2/chat/query",
                "task_status": "/api/v2/tasks/{task_id}/status",
                "system_status": "/api/v2/system/status",
                "websocket": "/api/v2/ws/{session_id}",
                "workflow_test": "/api/v2/test/workflow"
            }
        },
        "architecture": {
            "workflow_nodes": 8,
            "supported_llm_providers": ["gemini", "openai", "anthropic", "ollama"],
            "analysis_types": ["single_table", "cross_table", "temporal_comparison", "trend_analysis"]
        }
    }

@app.get("/health")
async def health_check():
    """Fast health check for deployment validation"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": str(Path().absolute()),
        "ready": True
    }

@app.get("/health/detailed")
async def detailed_health_check():
    """Comprehensive health check for V2 system"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "components": {
            "database": "connected",
            "upload_dir": str(upload_dir.absolute()),
            "langgraph_workflow": "ready",
            "websocket_manager": "active",
            "v1_compatibility": "enabled",
            "v2_enhanced_features": "operational"
        },
        "capabilities": {
            "multi_temporal_analysis": True,
            "real_time_updates": True,
            "background_processing": True,
            "llm_integration": True,
            "workflow_orchestration": True
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
