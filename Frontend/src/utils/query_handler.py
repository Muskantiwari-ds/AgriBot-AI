"""
API Routes for Query Handling
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import asyncio
import uuid
import logging
from datetime import datetime

from ...agents.coordinator import AgentCoordinator
from ...utils.location_utils import LocationUtils
from ...data.processors.text_processor import TextProcessor
from config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize components
coordinator = AgentCoordinator()
location_utils = LocationUtils()
text_processor = TextProcessor()

# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="User's agricultural query")
    language: Optional[str] = Field(default="hi", description="Query language code")
    location: Optional[Dict[str, Any]] = Field(default=None, description="User location details")
    user_context: Optional[Dict[str, Any]] = Field(default=None, description="Additional user context")
    session_id: Optional[str] = Field(default=None, description="Session identifier")

class LocationRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    state: Optional[str] = None
    district: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    language: str
    sources: List[str] = []
    recommendations: List[str] = []
    follow_up_questions: List[str] = []
    processing_time: float
    agents_used: List[str] = []
    query_type: str
    urgency: str = "normal"
    session_id: str

class ErrorResponse(BaseModel):
    error: str
    message: str
    timestamp: str

# Session management
active_sessions = {}

def get_session_id(session_id: Optional[str] = None) -> str:
    """Get or create session ID"""
    if session_id and session_id in active_sessions:
        return session_id
    
    new_session_id = str(uuid.uuid4())
    active_sessions[new_session_id] = {
        "created_at": datetime.now(),
        "queries": [],
        "context": {}
    }
    return new_session_id

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process an agricultural query and return AI-generated advice
    """
    try:
        # Validate and clean input
        query = text_processor.clean_text(request.query)
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Get or create session
        session_id = get_session_id(request.session_id)
        
        # Prepare user context
        user_context = {
            **(request.user_context or {}),
            **(request.location or {}),
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Process query through agent coordinator
        response = await coordinator.process_query(
            query=query,
            user_context=user_context,
            session_id=session_id
        )
        
        # Store query in session
        if session_id in active_sessions:
            active_sessions[session_id]["queries"].append({
                "query": query,
                "response": response["answer"],
                "timestamp": datetime.now().isoformat()
            })
        
        # Return response
        return QueryResponse(
            answer=response["answer"],
            confidence=response.get("confidence", 0.5),
            language=response.get("language", request.language),
            sources=response.get("sources", []),
            recommendations=response.get("recommendations", []),
            follow_up_questions=response.get("follow_up_questions", []),
            processing_time=response.get("processing_time", 0.0),
            agents_used=response.get("agents_used", []),
            query_type=response.get("query_type", "general"),
            urgency=response.get("urgency", "normal"),
            session_id=session_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query processing error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/query/voice")
async def process_voice_query(
    audio_file: UploadFile = File(...),
    language: str = "hi",
    location: Optional[str] = None,
    session_id: Optional[str] = None
):
    """
    Process voice query (speech-to-text + AI response)
    """
    try:
        # Validate file
        if not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Invalid audio file")
        
        # Read audio data
        audio_data = await audio_file.read()
        
        # Convert speech to text
        # This would integrate with speech recognition service
        # For now, returning placeholder
        transcribed_text = "आज मौसम कैसा है?"  # Placeholder
        
        # Process as regular query
        query_request = QueryRequest(
            query=transcribed_text,
            language=language,
            session_id=session_id
        )
        
        response = await process_query(query_request)
        
        return {
            "transcribed_text": transcribed_text,
            **response.dict()
        }
        
    except Exception as e:
        logger.error(f"Voice query error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weather/{location}")
async def get_weather_info(location: str, lang: str = "hi"):
    """
    Get weather information for specific location
    """
    try:
        # This would integrate with weather APIs
        weather_data = {
            "location": location,
            "temperature": "28°C",
            "humidity": "65%",
            "rainfall": "5mm expected",
            "forecast": "Partly cloudy with chance of rain",
            "farming_advice": "Good conditions for planting, avoid irrigation today"
        }
        
        return weather_data
        
    except Exception as e:
        logger.error(f"Weather API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/crops/{region}")
async def get_crop_recommendations(region: str, season: Optional[str] = None):
    """
    Get crop recommendations for specific region and season
    """
    try:
        # This would use the crop advisor agent
        recommendations = await coordinator.crop_advisor.get_advice(
            f"Best crops for {region}" + (f" in {season}" if season else ""),
            {"region": region, "season": season}
        )
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Crop recommendations error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market/{commodity}")
async def get_market_prices(commodity: str, state: Optional[str] = None):
    """
    Get current market prices for agricultural commodities
    """
    try:
        # This would integrate with market data APIs
        market_data = {
            "commodity": commodity,
            "state": state or "Karnataka",
            "current_price": "₹2500/quintal",
            "trend": "increasing",
            "last_updated": datetime.now().isoformat(),
            "markets": [
                {"name": "Bangalore APMC", "price": "₹2600/quintal"},
                {"name": "Mysore Market", "price": "₹2400/quintal"}
            ]
        }
        
        return market_data
        
    except Exception as e:
        logger.error(f"Market data error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/schemes")
async def get_government_schemes(
    state: Optional[str] = None,
    category: Optional[str] = None,
    lang: str = "hi"
):
    """
    Get information about government agricultural schemes
    """
    try:
        # This would integrate with government APIs
        schemes = [
            {
                "name": "PM-KISAN",
                "description": "Direct income support to farmers",
                "eligibility": "All landholding farmers",
                "benefit": "₹6000 per year",
                "how_to_apply": "Online at pmkisan.gov.in"
            },
            {
                "name": "Soil Health Card",
                "description": "Free soil testing and recommendations",
                "eligibility": "All farmers",
                "benefit": "Free soil analysis",
                "how_to_apply": "Contact local agriculture office"
            }
        ]
        
        return {"schemes": schemes, "total_count": len(schemes)}
        
    except Exception as e:
        logger.error(f"Schemes API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/location/detect")
async def detect_location(request: LocationRequest):
    """
    Get location details from coordinates
    """
    try:
        location_details = await location_utils.get_location_details(
            request.latitude,
            request.longitude
        )
        
        return location_details
        
    except Exception as e:
        logger.error(f"Location detection error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}/history")
async def get_session_history(session_id: str):
    """
    Get conversation history for a session
    """
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = active_sessions[session_id]
        return {
            "session_id": session_id,
            "created_at": session_data["created_at"].isoformat(),
            "queries": session_data["queries"],
            "context": session_data["context"]
        }
        
    except Exception as e:
        logger.error(f"Session history error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """
    Clear session data
    """
    try:
        if session_id in active_sessions:
            del active_sessions[session_id]
        
        # Clear agent memory for this session
        coordinator.clear_memory()
        
        return {"message": "Session cleared successfully"}
        
    except Exception as e:
        logger.error(f"Session clear error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/suggestions")
async def get_follow_up_suggestions(
    session_id: Optional[str] = None,
    context: Optional[str] = None
):
    """
    Get contextual follow-up question suggestions
    """
    try:
        # Get conversation history if session exists
        conversation_history = []
        user_context = {}
        
        if session_id and session_id in active_sessions:
            session_data = active_sessions[session_id]
            conversation_history = session_data["queries"]
            user_context = session_data["context"]
        
        # Generate suggestions
        suggestions = await coordinator.get_follow_up_suggestions(
            conversation_history,
            user_context
        )
        
        return {"suggestions": suggestions}
        
    except Exception as e:
        logger.error(f"Suggestions error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback")
async def submit_feedback(
    session_id: str,
    query_id: str,
    rating: int = Field(ge=1, le=5),
    feedback: Optional[str] = None
):
    """
    Submit feedback for a query response
    """
    try:
        # Store feedback (would integrate with database)
        feedback_data = {
            "session_id": session_id,
            "query_id": query_id,
            "rating": rating,
            "feedback": feedback,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Feedback received: {feedback_data}")
        
        return {"message": "Feedback submitted successfully"}
        
    except Exception as e:
        logger.error(f"Feedback submission error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@router.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            message="An error occurred while processing your request",
            timestamp=datetime.now().isoformat()
        ).dict()
    )

@router.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            message="An unexpected error occurred. Please try again later.",
            timestamp=datetime.now().isoformat()
        ).dict()
    )