"""
Database configuration and setup
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, JSON
from datetime import datetime
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DATABASE_ECHO,
    future=True
)

# Create session maker
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Create base class
Base = declarative_base()

class QueryLog(Base):
    """Model for logging user queries and responses"""
    __tablename__ = "query_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    query = Column(Text, nullable=False)
    query_language = Column(String(10))
    response = Column(Text)
    agent_type = Column(String(50))
    location = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow)
    processing_time = Column(Float)
    feedback_rating = Column(Integer)

class WeatherData(Base):
    """Model for storing weather data"""
    __tablename__ = "weather_data"
    
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(100), index=True)
    date = Column(DateTime, index=True)
    temperature_min = Column(Float)
    temperature_max = Column(Float)
    humidity = Column(Float)
    rainfall = Column(Float)
    wind_speed = Column(Float)
    weather_condition = Column(String(100))
    raw_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class CropData(Base):
    """Model for storing crop information"""
    __tablename__ = "crop_data"
    
    id = Column(Integer, primary_key=True, index=True)
    crop_name = Column(String(100), index=True)
    variety = Column(String(100))
    region = Column(String(100))
    season = Column(String(50))
    planting_date = Column(DateTime)
    harvest_date = Column(DateTime)
    yield_per_hectare = Column(Float)
    water_requirement = Column(Float)
    soil_type = Column(String(100))
    fertilizer_recommendations = Column(JSON)
    pest_diseases = Column(JSON)
    market_price_range = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserFeedback(Base):
    """Model for storing user feedback"""
    __tablename__ = "user_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    query_log_id = Column(Integer, index=True)
    user_id = Column(String, index=True)
    rating = Column(Integer)  # 1-5 stars
    feedback_text = Column(Text)
    improvement_suggestions = Column(Text)
    is_helpful = Column(Boolean)
    timestamp = Column(DateTime, default=datetime.utcnow)

class DataSource(Base):
    """Model for tracking data sources and updates"""
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(100), unique=True, index=True)
    source_url = Column(String(500))
    last_updated = Column(DateTime)
    update_frequency = Column(String(50))  # daily, weekly, monthly
    status = Column(String(50))  # active, inactive, error
    record_count = Column(Integer)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class KnowledgeBase(Base):
    """Model for storing processed knowledge base entries"""
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), index=True)
    content = Column(Text, nullable=False)
    category = Column(String(100), index=True)  # weather, crops, finance, policy
    subcategory = Column(String(100))
    language = Column(String(10))
    region = Column(String(100))
    tags = Column(JSON)
    embeddings = Column(JSON)  # Store embedding vectors
    source_reference = Column(String(500))
    confidence_score = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Dependency to get database session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Initialize database
async def init_db():
    """Create database tables"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise