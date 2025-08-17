"""
Crop Advisor Agent - Specialized agent for crop selection and cultivation advice
"""

import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

from ..models.llm_interface import LLMInterface
from ..data.collectors.crop_data_collector import CropDataCollector
from ..utils.location_utils import LocationUtils
from config.settings import settings, AGRICULTURAL_SEASONS

logger = logging.getLogger(__name__)

class CropAdvisorAgent:
    """
    Specialized agent for crop selection, planting schedules, 
    cultivation practices, and yield optimization
    """
    
    def __init__(self):
        self.llm_interface = LLMInterface()
        self.crop_data_collector = CropDataCollector()
        self.location_utils = LocationUtils()
        
        # Load crop database
        self.crop_database = self._load_crop_database()
        
    def _load_crop_database(self) -> Dict[str, Any]:
        """Load comprehensive crop database"""
        return {
            "rice": {
                "hindi_name": "चावल",
                "seasons": ["kharif"],
                "duration": "120-150 days",
                "water_requirement": "high",
                "soil_type": ["clay", "loam"],
                "temperature": "20-35°C",
                "rainfall": "150-300cm",
                "states": ["WB", "UP", "AP", "TN", "OR", "PB", "HR"],
                "varieties": {
                    "basmati": {"duration": "140-150 days", "yield": "3-4 tonnes/hectare"},
                    "IR64": {"duration": "120-125 days", "yield": "5-6 tonnes/hectare"},
                    "swarna": {"duration": "145-150 days", "yield": "4-5 tonnes/hectare"}
                },
                "cultivation_practices": {
                    "land_preparation": "Puddle the field thoroughly",
                    "sowing": "Transplant 25-30 day old seedlings",
                    "spacing": "20cm x 15cm",
                    "fertilizer": "120:60:40 kg NPK per hectare",
                    "irrigation": "Maintain 2-5cm water level",
                    "pest_management": "Monitor for stem borer, brown plant hopper"
                }
            },
            "wheat": {
                "hindi_name": "गेहूं",
                "seasons": ["rabi"],
                "duration": "120-150 days",
                "water_requirement": "medium",
                "soil_type": ["loam", "sandy loam"],
                "temperature": "15-25°C",
                "rainfall": "75-100cm",
                "states": ["UP", "PB", "HR", "MP", "RJ", "BR"],
                "varieties": {
                    "HD2967": {"duration": "135-140 days", "yield": "4-5 tonnes/hectare"},
                    "PBW343": {"duration": "145-150 days", "yield": "5-6 tonnes/hectare"},
                    "WH147": {"duration": "125-130 days", "yield": "3-4 tonnes/hectare"}
                },
                "cultivation_practices": {
                    "land_preparation": "Deep plowing and leveling",
                    "sowing": "Line sowing with seed drill",
                    "spacing": "22.5cm row spacing",
                    "fertilizer": "120:60:40 kg NPK per hectare",
                    "irrigation": "6-8 irrigations required",
                    "pest_management": "Monitor for aphids, termites"
                }
            },
            "sugarcane": {
                "hindi_name": "गन्ना",
                "seasons": ["kharif", "rabi"],
                "duration": "12-18 months",
                "water_requirement": "very high",
                "soil_type": ["loam", "clay loam"],
                "temperature": "20-30°C",
                "rainfall": "100-150cm",
                "states": ["UP", "MH", "KA", "TN", "AP", "GJ"],
                "varieties": {
                    "Co86032": {"duration": "12 months", "yield": "80-100 tonnes/hectare"},
                    "Co238": {"duration": "14 months", "yield": "90-110 tonnes/hectare"}
                },
                "cultivation_practices": {
                    "land_preparation": "Deep furrows at 90cm spacing",
                    "sowing": "Plant 2-3 budded sets per furrow",
                    "spacing": "90cm between rows",
                    "fertilizer": "280:92:92 kg NPK per hectare",
                    "irrigation": "15-20 irrigations required",
                    "pest_management": "Monitor for red rot, smut"
                }
            }
            # Add more crops as needed
        }
    
    async def get_advice(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get comprehensive crop advice based on query and context
        
        Args:
            query: User's crop-related query
            context: User context (location, current crops, farm size, etc.)
            
        Returns:
            Dictionary containing crop advice and recommendations
        """
        try:
            # Extract user location and farm details
            location_info = await self._extract_location_info(context)
            
            # Analyze query intent
            query_intent = await self._analyze_crop_query(query)
            
            # Get relevant crop data
            relevant_crops = await self._get_relevant_crops(query_intent, location_info)
            
            # Generate advice based on intent
            advice = await self._generate_crop_advice(query, query_intent, relevant_crops, location_info)
            
            return {
                "answer": advice["response"],
                "confidence": advice["confidence"],
                "recommendations": advice["recommendations"],
                "sources": advice["sources"],
                "crop_suggestions": advice.get("crop_suggestions", []),
                "timing_advice": advice.get("timing_advice", {}),
                "practices": advice.get("practices", {}),
                "agent": "crop_advisor"
            }
            
        except Exception as e:
            logger.error(f"Crop advisor error: {e}")
            return {
                "answer": "क्षमा करें, मुझे फसल संबंधी सलाह देने में कुछ समस्या हो रही है।",
                "confidence": 0.0,
                "error": str(e),
                "agent": "crop_advisor"
            }
    
    async def _extract_location_info(self, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Extract and enhance location information"""
        location_info = {
            "state": "KA",  # Default to Karnataka
            "district": "",
            "latitude": 12.9716,  # Bangalore
            "longitude": 77.5946,
            "climate_zone": "tropical",
            "soil_type": "red loam"
        }
        
        if context:
            location_info.update({
                "state": context.get("state", location_info["state"]),
                "district": context.get("district", ""),
                "latitude": context.get("latitude", location_info["latitude"]),
                "longitude": context.get("longitude", location_info["longitude"])
            })
        
        # Get climate and soil data for location
        try:
            enhanced_info = await self.location_utils.get_location_details(
                location_info["latitude"], 
                location_info["longitude"]
            )
            location_info.update(enhanced_info)
        except Exception as e:
            logger.warning(f"Location enhancement failed: {e}")
        
        return location_info
    
    async def _analyze_crop_query(self, query: str) -> Dict[str, Any]:
        """Analyze crop-related query to understand intent"""
        
        analysis_prompt = f"""
        Analyze this crop-related query and classify the intent:
        
        Query: "{query}"
        
        Classify into one or more categories and return JSON:
        {{
            "primary_intent": "crop_selection|planting_time|cultivation_practices|variety_selection|yield_improvement|disease_pest|harvest_timing|general",
            "specific_crops": ["list of crops mentioned"],
            "season_mentioned": "kharif|rabi|zaid|none",
            "location_specific": true/false,
            "time_sensitive": true/false,
            "technical_level": "basic|intermediate|advanced",
            "keywords": ["relevant keywords"]
        }}
        """
        
        try:
            response = await self.llm_interface.get_completion(analysis_prompt)
            return json.loads(response)
        except Exception as e:
            logger.warning(f"Query analysis failed: {e}")
            return {
                "primary_intent": "general",
                "specific_crops": [],
                "season_mentioned": "none",
                "location_specific": False,
                "time_sensitive": False,
                "technical_level": "basic",
                "keywords": query.split()
            }
    
    async def _get_relevant_crops(self, query_intent: Dict, location_info: Dict) -> List[Dict[str, Any]]:
        """Get crops relevant to the query and location"""
        
        relevant_crops = []
        state = location_info.get("state", "KA")
        current_season = self._get_current_season()
        
        # If specific crops mentioned, prioritize them
        if query_intent.get("specific_crops"):
            for crop_name in query_intent["specific_crops"]:
                crop_name_lower = crop_name.lower()
                if crop_name_lower in self.crop_database:
                    crop_data = self.crop_database[crop_name_lower].copy()
                    crop_data["name"] = crop_name_lower
                    crop_data["suitability_score"] = self._calculate_suitability(crop_data, location_info)
                    relevant_crops.append(crop_data)
        
        # Otherwise, get crops suitable for location and season
        else:
            for crop_name, crop_data in self.crop_database.items():
                crop_copy = crop_data.copy()
                crop_copy["name"] = crop_name
                
                # Check if crop is suitable for state
                if state in crop_data.get("states", []):
                    # Check season compatibility
                    if current_season in crop_data.get("seasons", []):
                        crop_copy["suitability_score"] = self._calculate_suitability(crop_copy, location_info)
                        relevant_crops.append(crop_copy)
        
        # Sort by suitability score
        relevant_crops.sort(key=lambda x: x.get("suitability_score", 0), reverse=True)
        
        return relevant_crops[:5]  # Return top 5 relevant crops
    
    def _calculate_suitability(self, crop_data: Dict, location_info: Dict) -> float:
        """Calculate crop suitability score for given location"""
        
        score = 0.0
        
        # State compatibility (40% weight)
        if location_info.get("state") in crop_data.get("states", []):
            score += 0.4
        
        # Season compatibility (30% weight)
        current_season = self._get_current_season()
        if current_season in crop_data.get("seasons", []):
            score += 0.3
        
        # Soil type compatibility (20% weight)
        location_soil = location_info.get("soil_type", "").lower()
        crop_soils = [soil.lower() for soil in crop_data.get("soil_type", [])]
        if any(soil in location_soil for soil in crop_soils):
            score += 0.2
        
        # Climate zone compatibility (10% weight)
        # This would need more sophisticated climate matching
        score += 0.1
        
        return score
    
    def _get_current_season(self) -> str:
        """Determine current agricultural season"""
        current_month = datetime.now().month
        
        if current_month in [6, 7, 8, 9, 10]:
            return "kharif"
        elif current_month in [11, 12, 1, 2, 3]:
            return "rabi"
        else:
            return "zaid"
    
    async def _generate_crop_advice(self, 
                                  query: str,
                                  query_intent: Dict,
                                  relevant_crops: List[Dict],
                                  location_info: Dict) -> Dict[str, Any]:
        """Generate comprehensive crop advice"""
        
        current_season = self._get_current_season()
        season_info = AGRICULTURAL_SEASONS.get(current_season, {})
        
        advice_prompt = f"""
        You are an expert agricultural advisor specializing in Indian farming practices.
        
        User Query: "{query}"
        Query Intent: {json.dumps(query_intent)}
        Location: {location_info.get('state', 'Unknown')} state, {location_info.get('district', 'Unknown')} district
        Current Season: {current_season} ({season_info.get('name', 'Unknown')})
        
        Relevant Crops:
        {json.dumps(relevant_crops, indent=2)}
        
        Provide comprehensive advice covering:
        1. Direct answer to the user's question
        2. Specific crop recommendations for their location and season
        3. Optimal planting timing
        4. Cultivation practices
        5. Expected yields and duration
        6. Risk factors and mitigation
        
        Format as JSON:
        {{
            "response": "Detailed response in Hindi and English",
            "confidence": 0.0-1.0,
            "recommendations": ["actionable recommendations"],
            "crop_suggestions": [
                {{
                    "crop": "crop name",
                    "variety": "best variety",
                    "planting_window": "optimal planting time",
                    "expected_yield": "yield estimate",
                    "investment": "approximate cost",
                    "risk_level": "low|medium|high"
                }}
            ],
            "timing_advice": {{
                "current_season_action": "what to do now",
                "next_season_prep": "preparation for next season"
            }},
            "practices": {{
                "land_preparation": "land prep advice",
                "sowing": "sowing guidance",
                "irrigation": "irrigation schedule",
                "fertilization": "fertilizer recommendations",
                "pest_management": "pest control measures"
            }},
            "sources": ["ICAR", "Agricultural Universities", "Government Guidelines"]
        }}
        
        Make advice practical, culturally appropriate, and economically viable for Indian farmers.
        Include both traditional wisdom and modern scientific practices.
        """
        
        try:
            response = await self.llm_interface.get_completion(advice_prompt)
            advice = json.loads(response)
            
            # Add metadata
            advice["generated_at"] = datetime.now().isoformat()
            advice["location_context"] = location_info
            advice["season_context"] = current_season
            
            return advice
            
        except Exception as e:
            logger.error(f"Advice generation failed: {e}")
            
            # Fallback response
            return {
                "response": f"आपके क्षेत्र में {current_season} सीजन के लिए उपयुक्त फसलों की सिफारिश करने के लिए मुझे और जानकारी चाहिए।",
                "confidence": 0.3,
                "recommendations": ["अपने स्थानीय कृषि विशेषज्ञ से सलाह लें"],
                "sources": ["स्थानीय कृषि विभाग"],
                "error": str(e)
            }
    
    async def get_crop_calendar(self, location: Dict[str, Any]) -> Dict[str, Any]:
        """Get seasonal crop calendar for specific location"""
        
        try:
            state = location.get("state", "KA")
            suitable_crops = []
            
            # Get crops suitable for each season
            for season, season_data in AGRICULTURAL_SEASONS.items():
                season_crops = []
                for crop_name, crop_data in self.crop_database.items():
                    if (season in crop_data.get("seasons", []) and 
                        state in crop_data.get("states", [])):
                        season_crops.append({
                            "name": crop_name,
                            "hindi_name": crop_data.get("hindi_name", ""),
                            "duration": crop_data.get("duration", ""),
                            "sowing_time": season_data.get("sowing", ""),
                            "harvest_time": season_data.get("harvesting", "")
                        })
                
                suitable_crops.append({
                    "season": season,
                    "season_name": season_data.get("name", ""),
                    "crops": season_crops
                })
            
            return {
                "location": location,
                "crop_calendar": suitable_crops,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Crop calendar generation failed: {e}")
            return {"error": str(e)}
    
    async def get_variety_comparison(self, crop_name: str, location: Dict[str, Any]) -> Dict[str, Any]:
        """Compare different varieties of a specific crop"""
        
        try:
            crop_name_lower = crop_name.lower()
            if crop_name_lower not in self.crop_database:
                return {"error": f"Crop '{crop_name}' not found in database"}
            
            crop_data = self.crop_database[crop_name_lower]
            varieties = crop_data.get("varieties", {})
            
            variety_comparison = []
            for variety_name, variety_data in varieties.items():
                variety_comparison.append({
                    "name": variety_name,
                    "duration": variety_data.get("duration", ""),
                    "yield": variety_data.get("yield", ""),
                    "characteristics": variety_data.get("characteristics", ""),
                    "suitability": variety_data.get("suitability", "")
                })
            
            return {
                "crop": crop_name,
                "location": location,
                "varieties": variety_comparison,
                "recommendation": "Best variety based on location and current conditions"
            }
            
        except Exception as e:
            logger.error(f"Variety comparison failed: {e}")
            return {"error": str(e)}