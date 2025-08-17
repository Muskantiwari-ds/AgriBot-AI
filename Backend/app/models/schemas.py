"""
Pydantic models for API request/response schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class QueryRequest(BaseModel):
    """Request model for agricultural queries"""
    query: str = Field(..., description="User's agricultural question")
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    location: Optional[str] = Field(None, description="User's location")
    language: Optional[str] = Field("auto", description="Query language (auto-detect if not specified)")
    context: Optional[Dict[str, Any]] = Field({}, description="Additional context")

class QueryResponse(BaseModel):
    """Response model for agricultural queries"""
    session_id: str = Field(..., description="Session identifier")
    answer: str = Field(..., description="AI agent's response")
    agent_type: str = Field(..., description="Type of agent that handled the query")
    language: str = Field(..., description="Language of the response")
    location: Optional[str] = Field(None, description="Location context")
    sources: List[str] = Field([], description="Data sources used")
    confidence_score: float = Field(..., description="Confidence in the response (0-1)")
    suggestions: List[str] = Field([], description="Follow-up suggestions")
    processing_time: float = Field(..., description="Time taken to process query (seconds)")
    metadata: Dict[str, Any] = Field({}, description="Additional metadata")

class FeedbackRequest(BaseModel):
    """Request model for user feedback"""
    query_log_id: Optional[int] = Field(None, description="ID of the query being rated")
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5 stars")
    feedback_text: Optional[str] = Field(None, description="Detailed feedback")
    improvement_suggestions: Optional[str] = Field(None, description="Suggestions for improvement")
    is_helpful: Optional[bool] = Field(None, description="Whether the response was helpful")

class WeatherRequest(BaseModel):
    """Request model for weather queries"""
    location: str = Field(..., description="Location for weather data")
    days: Optional[int] = Field(7, ge=1, le=14, description="Number of forecast days")
    include_alerts: Optional[bool] = Field(True, description="Include weather alerts")

class WeatherResponse(BaseModel):
    """Response model for weather queries"""
    location: str
    current_weather: Optional[Dict[str, Any]] = None
    forecast: Optional[List[Dict[str, Any]]] = None
    alerts: List[str] = []
    recommendations: List[str] = []
    last_updated: datetime

class CropRequest(BaseModel):
    """Request model for crop recommendations"""
    region: str = Field(..., description="Region/location")
    season: Optional[str] = Field(None, description="Growing season")
    crop_type: Optional[str] = Field(None, description="Specific crop type")
    soil_type: Optional[str] = Field(None, description="Soil type")
    farm_size: Optional[float] = Field(None, description="Farm size in hectares")

class CropResponse(BaseModel):
    """Response model for crop recommendations"""
    region: str
    season: Optional[str]
    recommended_crops: List[Dict[str, Any]] = []
    planting_calendar: Dict[str, Any] = {}
    care_instructions: List[str] = []
    market_insights: Dict[str, Any] = {}

class FinancialRequest(BaseModel):
    """Request model for financial queries"""
    query_type: str = Field(..., description="Type of financial query (loan, insurance, subsidy)")
    amount: Optional[float] = Field(None, description="Amount in question")
    crop_type: Optional[str] = Field(None, description="Crop type for insurance/loan")
    location: Optional[str] = Field(None, description="Location for regional schemes")

class PolicyRequest(BaseModel):
    """Request model for policy/scheme queries"""
    scheme_type: Optional[str] = Field(None, description="Type of government scheme")
    location: str = Field(..., description="State/region for location-specific schemes")
    farmer_category: Optional[str] = Field(None, description="Farmer category (small, marginal, etc.)")

class HealthCheckResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Overall system status")
    timestamp: datetime = Field(..., description="Check timestamp")
    services: Dict[str, str] = Field({}, description="Individual service status")
    agents: Dict[str, Dict[str, Any]] = Field({}, description="AI agent status")

class StatsResponse(BaseModel):
    """Response model for usage statistics"""
    period_days: int
    total_queries: int
    agent_usage: Dict[str, int]
    language_usage: Dict[str, int]
    avg_processing_time: float
    generated_at: str

class ErrorResponse(BaseModel):
    """Response model for errors"""
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: Optional[str] = Field(None, description="Request identifier for tracking")

# Data models for internal use
class WeatherData(BaseModel):
    """Weather data model"""
    location: str
    timestamp: datetime
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    rainfall: Optional[float] = None
    wind_speed: Optional[float] = None
    condition: Optional[str] = None

class CropInfo(BaseModel):
    """Crop information model"""
    name: str
    variety: Optional[str] = None
    season: Optional[str] = None
    region: Optional[str] = None
    planting_date: Optional[datetime] = None
    harvest_date: Optional[datetime] = None
    water_requirement: Optional[float] = None
    fertilizer_needs: Optional[Dict[str, Any]] = None

class MarketPrice(BaseModel):
    """Market price model"""
    commodity: str
    market: str
    price_per_quintal: Optional[float] = None
    date: datetime
    trend: Optional[str] = None  # increasing, decreasing, stable

class GovernmentScheme(BaseModel):
    """Government scheme model"""
    scheme_name: str
    description: str
    eligibility: List[str] = []
    benefits: List[str] = []
    application_process: List[str] = []
    documents_required: List[str] = []
    state: Optional[str] = None
    is_active: bool = True