"""
API Routes for AgriBot AI
"""

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import uuid

from app.core.database import get_db, QueryLog, UserFeedback
from app.services.ai_agent import AIAgentService
from app.models.schemas import (
    QueryRequest, 
    QueryResponse, 
    FeedbackRequest,
    WeatherRequest,
    CropRequest
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    req: Request = None
):
    """
    Process agricultural query using AI agents
    """
    try:
        # Get AI service from app state
        ai_service: AIAgentService = req.app.state.ai_service
        
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Process query
        result = await ai_service.process_query(
            query=request.query,
            user_id=request.user_id,
            location=request.location,
            context=request.context
        )
        
        # Log query in background
        background_tasks.add_task(
            log_query,
            db=db,
            user_id=request.user_id,
            session_id=session_id,
            query=request.query,
            response=result
        )
        
        return QueryResponse(
            session_id=session_id,
            answer=result['answer'],
            agent_type=result['agent_type'],
            language=result.get('language', 'en'),
            location=result.get('location'),
            sources=result.get('sources', []),
            confidence_score=result.get('confidence_score', 0.8),
            suggestions=result.get('suggestions', []),
            processing_time=result.get('processing_time', 0.0),
            metadata=result.get('metadata', {})
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing query")

@router.post("/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Submit user feedback for query response
    """
    try:
        feedback = UserFeedback(
            query_log_id=request.query_log_id,
            user_id=request.user_id,
            rating=request.rating,
            feedback_text=request.feedback_text,
            improvement_suggestions=request.improvement_suggestions,
            is_helpful=request.is_helpful
        )
        
        db.add(feedback)
        await db.commit()
        
        return {"message": "Feedback submitted successfully"}
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Error submitting feedback")

@router.get("/weather/{location}")
async def get_weather(
    location: str,
    days: Optional[int] = 5,
    req: Request = None
):
    """
    Get weather information for specific location
    """
    try:
        ai_service: AIAgentService = req.app.state.ai_service
        weather_agent = ai_service.agents['weather']
        
        # Create weather query
        query = f"weather forecast for {location} for next {days} days"
        
        result = await weather_agent.process_query(
            query=query,
            location=location,
            context=[],
            user_context={'forecast_days': days}
        )
        
        return {
            'location': location,
            'forecast_days': days,
            'weather_info': result['answer'],
            'confidence': result.get('confidence', 0.8),
            'sources': result.get('sources', [])
        }
        
    except Exception as e:
        logger.error(f"Error getting weather: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving weather data")

@router.get("/crops/{region}")
async def get_crop_recommendations(
    region: str,
    season: Optional[str] = None,
    crop_type: Optional[str] = None,
    req: Request = None
):
    """
    Get crop recommendations for specific region
    """
    try:
        ai_service: AIAgentService = req.app.state.ai_service
        crop_agent = ai_service.agents['crop']
        
        # Build query based on parameters
        query_parts = [f"crop recommendations for {region}"]
        if season:
            query_parts.append(f"in {season} season")
        if crop_type:
            query_parts.append(f"for {crop_type}")
        
        query = " ".join(query_parts)
        
        result = await crop_agent.process_query(
            query=query,
            location=region,
            context=[],
            user_context={'season': season, 'crop_type': crop_type}
        )
        
        return {
            'region': region,
            'season': season,
            'crop_type': crop_type,
            'recommendations': result['answer'],
            'confidence': result.get('confidence', 0.8),
            'sources': result.get('sources', [])
        }
        
    except Exception as e:
        logger.error(f"Error getting crop recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving crop recommendations")

@router.get("/health")
async def agent_health(req: Request = None):
    """
    Get health status of all AI agents
    """
    try:
        ai_service: AIAgentService = req.app.state.ai_service
        status = await ai_service.get_agent_status()
        return status
        
    except Exception as e:
        logger.error(f"Error getting agent health: {str(e)}")
        raise HTTPException(status_code=500, detail="Error checking agent health")

@router.get("/languages")
async def supported_languages():
    """
    Get list of supported languages
    """
    from app.core.config import settings
    return {
        'supported_languages': settings.SUPPORTED_LANGUAGES,
        'default_language': 'en'
    }

@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    days: Optional[int] = 7
):
    """
    Get usage statistics
    """
    try:
        from sqlalchemy import func, text
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Query statistics
        query_count = await db.execute(
            text("SELECT COUNT(*) FROM query_logs WHERE timestamp > :cutoff_date"),
            {'cutoff_date': cutoff_date}
        )
        total_queries = query_count.scalar()
        
        # Agent usage
        agent_stats = await db.execute(
            text("""
                SELECT agent_type, COUNT(*) as count 
                FROM query_logs 
                WHERE timestamp > :cutoff_date 
                GROUP BY agent_type
            """),
            {'cutoff_date': cutoff_date}
        )
        agent_usage = dict(agent_stats.fetchall())
        
        # Language statistics
        lang_stats = await db.execute(
            text("""
                SELECT query_language, COUNT(*) as count 
                FROM query_logs 
                WHERE timestamp > :cutoff_date 
                GROUP BY query_language
            """),
            {'cutoff_date': cutoff_date}
        )
        language_usage = dict(lang_stats.fetchall())
        
        # Average response time
        avg_time = await db.execute(
            text("""
                SELECT AVG(processing_time) 
                FROM query_logs 
                WHERE timestamp > :cutoff_date AND processing_time IS NOT NULL
            """),
            {'cutoff_date': cutoff_date}
        )
        avg_processing_time = avg_time.scalar() or 0.0
        
        return {
            'period_days': days,
            'total_queries': total_queries,
            'agent_usage': agent_usage,
            'language_usage': language_usage,
            'avg_processing_time': round(avg_processing_time, 2),
            'generated_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving statistics")

async def log_query(
    db: AsyncSession,
    user_id: str,
    session_id: str,
    query: str,
    response: Dict[str, Any]
):
    """Background task to log query and response"""
    try:
        query_log = QueryLog(
            user_id=user_id,
            query=query,
            query_language=response.get('language', 'en'),
            response=response.get('answer'),
            agent_type=response.get('agent_type'),
            location=response.get('location'),
            processing_time=response.get('processing_time'),
            timestamp=datetime.now()
        )
        
        db.add(query_log)
        await db.commit()
        
    except Exception as e:
        logger.error(f"Error logging query: {str(e)}")
        await db.rollback()