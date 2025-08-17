"""
Weather Agent - Specialized agent for weather-related queries
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
import aiohttp
import asyncio

from app.core.config import settings
from app.services.base_agent import BaseAgent
from app.services.data_sources.weather_service import WeatherService

logger = logging.getLogger(__name__)

class WeatherAgent(BaseAgent):
    """Agent specialized in handling weather-related agricultural queries"""
    
    def __init__(self):
        super().__init__()
        self.weather_service = WeatherService()
        self.agent_type = "weather"
    
    async def process_query(
        self, 
        query: str, 
        location: str = None, 
        context: List[Dict] = None,
        user_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process weather-related query
        
        Args:
            query: User's weather query
            location: Location for weather data
            context: Relevant context from knowledge base
            user_context: Additional user context
        
        Returns:
            Response with weather information and recommendations
        """
        try:
            # Determine query type
            query_type = self._classify_weather_query(query)
            
            # Get weather data based on query type
            weather_data = await self._get_weather_data(query_type, location)
            
            # Generate response based on query type and weather data
            response = await self._generate_weather_response(
                query, query_type, weather_data, location, context
            )
            
            return {
                'answer': response['answer'],
                'sources': response['sources'],
                'confidence': response['confidence'],
                'suggestions': response.get('suggestions', []),
                'weather_data': weather_data
            }
            
        except Exception as e:
            logger.error(f"Weather agent error: {str(e)}")
            return {
                'answer': "I'm sorry, I couldn't retrieve weather information at the moment. Please try again later.",
                'sources': [],
                'confidence': 0.1,
                'error': str(e)
            }
    
    def _classify_weather_query(self, query: str) -> str:
        """Classify the type of weather query"""
        query_lower = query.lower()
        
        # Current weather
        if any(word in query_lower for word in ['current', 'now', 'today', 'present']):
            return 'current'
        
        # Weather forecast
        elif any(word in query_lower for word in ['tomorrow', 'next', 'forecast', 'will', 'going to']):
            return 'forecast'
        
        # Historical weather
        elif any(word in query_lower for word in ['last', 'previous', 'historical', 'past']):
            return 'historical'
        
        # Irrigation timing
        elif any(word in query_lower for word in ['irrigate', 'water', 'irrigation', 'watering']):
            return 'irrigation'
        
        # Planting/harvesting timing
        elif any(word in query_lower for word in ['plant', 'sow', 'harvest', 'timing']):
            return 'agricultural_timing'
        
        # Weather alerts
        elif any(word in query_lower for word in ['alert', 'warning', 'extreme', 'dangerous']):
            return 'alerts'
        
        return 'general'
    
    async def _get_weather_data(self, query_type: str, location: str) -> Dict[str, Any]:
        """Get appropriate weather data based on query type"""
        try:
            if query_type == 'current':
                return await self.weather_service.get_current_weather(location)
            
            elif query_type == 'forecast':
                return await self.weather_service.get_forecast(location, days=7)
            
            elif query_type == 'historical':
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                return await self.weather_service.get_historical_data(
                    location, start_date, end_date
                )
            
            else:
                # Get both current and forecast for comprehensive response
                current = await self.weather_service.get_current_weather(location)
                forecast = await self.weather_service.get_forecast(location, days=5)
                
                return {
                    'current': current,
                    'forecast': forecast
                }
                
        except Exception as e:
            logger.error(f"Error getting weather data: {str(e)}")
            return {}
    
    async def _generate_weather_response(
        self, 
        query: str, 
        query_type: str, 
        weather_data: Dict[str, Any], 
        location: str,
        context: List[Dict] = None
    ) -> Dict[str, Any]:
        """Generate appropriate response based on weather data and query type"""
        
        if not weather_data:
            return {
                'answer': f"I couldn't retrieve weather data for {location}. Please check the location name or try again later.",
                'sources': [],
                'confidence': 0.1
            }
        
        response_generators = {
            'current': self._generate_current_weather_response,
            'forecast': self._generate_forecast_response,
            'irrigation': self._generate_irrigation_response,
            'agricultural_timing': self._generate_timing_response,
            'alerts': self._generate_alerts_response,
            'general': self._generate_general_response
        }
        
        generator = response_generators.get(query_type, self._generate_general_response)
        return await generator(query, weather_data, location, context)
    
    async def _generate_current_weather_response(
        self, query: str, weather_data: Dict[str, Any], location: str, context: List[Dict] = None
    ) -> Dict[str, Any]:
        """Generate response for current weather queries"""
        
        current = weather_data.get('current', weather_data)
        
        if not current:
            return {
                'answer': f"Current weather data is not available for {location}.",
                'sources': ['IMD Weather Service'],
                'confidence': 0.3
            }
        
        temp = current.get('temperature', 'N/A')
        humidity = current.get('humidity', 'N/A')
        rainfall = current.get('rainfall', 0)
        condition = current.get('condition', 'Unknown')
        
        answer = f"Current weather in {location}:\n"
        answer += f"🌡️ Temperature: {temp}°C\n"
        answer += f"💧 Humidity: {humidity}%\n"
        answer += f"🌧️ Rainfall: {rainfall}mm\n"
        answer += f"☁️ Condition: {condition}\n\n"
        
        # Add agricultural recommendations
        recommendations = self._get_weather_recommendations(current, 'current')
        if recommendations:
            answer += f"🌾 Agricultural Recommendations:\n{recommendations}"
        
        return {
            'answer': answer,
            'sources': ['India Meteorological Department'],
            'confidence': 0.9,
            'suggestions': [
                "Check 7-day weather forecast",
                "Get irrigation recommendations",
                "View weather alerts"
            ]
        }
    
    async def _generate_forecast_response(
        self, query: str, weather_data: Dict[str, Any], location: str, context: List[Dict] = None
    ) -> Dict[str, Any]:
        """Generate response for weather forecast queries"""
        
        forecast = weather_data.get('forecast', weather_data)
        
        if not forecast or not forecast.get('daily'):
            return {
                'answer': f"Weather forecast is not available for {location}.",
                'sources': ['IMD Weather Service'],
                'confidence': 0.3
            }
        
        daily_forecasts = forecast['daily'][:5]  # Next 5 days
        
        answer = f"5-Day Weather Forecast for {location}:\n\n"
        
        for i, day_data in enumerate(daily_forecasts):
            date = (datetime.now() + timedelta(days=i+1)).strftime("%a, %b %d")
            temp_min = day_data.get('temp_min', 'N/A')
            temp_max = day_data.get('temp_max', 'N/A')
            rainfall = day_data.get('rainfall', 0)
            condition = day_data.get('condition', 'Unknown')
            
            answer += f"📅 {date}:\n"
            answer += f"   🌡️ {temp_min}°C - {temp_max}°C\n"
            answer += f"   🌧️ {rainfall}mm rain\n"
            answer += f"   ☁️ {condition}\n\n"
        
        # Add weekly recommendations
        recommendations = self._get_weekly_recommendations(daily_forecasts)
        if recommendations:
            answer += f"🌾 Weekly Recommendations:\n{recommendations}"
        
        return {
            'answer': answer,
            'sources': ['India Meteorological Department'],
            'confidence': 0.85,
            'suggestions': [
                "Get irrigation schedule",
                "Check for weather alerts",
                "View crop-specific recommendations"
            ]
        }
    
    async def _generate_irrigation_response(
        self, query: str, weather_data: Dict[str, Any], location: str, context: List[Dict] = None
    ) -> Dict[str, Any]:
        """Generate irrigation-specific recommendations"""
        
        current = weather_data.get('current', weather_data)
        forecast = weather_data.get('forecast', {})
        
        answer = f"💧 Irrigation Recommendations for {location}:\n\n"
        
        # Current conditions assessment
        if current:
            rainfall_today = current.get('rainfall', 0)
            humidity = current.get('humidity', 50)
            temp = current.get('temperature', 25)
            
            if rainfall_today > 10:
                answer += "🌧️ Recent rainfall detected. Consider delaying irrigation by 1-2 days.\n\n"
            elif humidity < 40 and temp > 30:
                answer += "🔥 Hot and dry conditions. Increase irrigation frequency.\n\n"
            else:
                answer += "🌤️ Normal conditions. Follow regular irrigation schedule.\n\n"
        
        # Forecast-based recommendations
        if forecast.get('daily'):
            upcoming_rain = sum(day.get('rainfall', 0) for day in forecast['daily'][:3])
            
            if upcoming_rain > 20:
                answer += "☔ Significant rainfall expected in next 3 days. Reduce or skip irrigation.\n"
            elif upcoming_rain < 5:
                answer += "☀️ Dry period ahead. Ensure adequate soil moisture before dry spell.\n"
        
        answer += "\n🕐 Best Irrigation Times:\n"
        answer += "• Early morning (5-8 AM) - Minimal evaporation\n"
        answer += "• Evening (5-7 PM) - Cool temperatures\n"
        answer += "• Avoid midday irrigation (11 AM - 3 PM)\n"
        
        return {
            'answer': answer,
            'sources': ['Weather Analysis', 'Agricultural Best Practices'],
            'confidence': 0.88,
            'suggestions': [
                "Get soil moisture recommendations",
                "View crop water requirements",
                "Set up weather alerts"
            ]
        }
    
    async def _generate_timing_response(
        self, query: str, weather_data: Dict[str, Any], location: str, context: List[Dict] = None
    ) -> Dict[str, Any]:
        """Generate agricultural timing recommendations"""
        
        forecast = weather_data.get('forecast', weather_data)
        
        answer = f"🌱 Agricultural Timing Recommendations for {location}:\n\n"
        
        if forecast.get('daily'):
            next_week = forecast['daily'][:7]
            total_rainfall = sum(day.get('rainfall', 0) for day in next_week)
            avg_temp = sum(day.get('temp_max', 25) for day in next_week) / len(next_week)
            
            # Planting recommendations
            answer += "🌾 Planting Conditions:\n"
            if total_rainfall > 50:
                answer += "• Good rainfall expected - Favorable for sowing\n"
            elif total_rainfall < 10:
                answer += "• Low rainfall expected - Ensure irrigation before sowing\n"
            else:
                answer += "• Moderate rainfall - Monitor soil moisture\n"
            
            if avg_temp > 35:
                answer += "• High temperatures expected - Consider heat-tolerant varieties\n"
            elif avg_temp < 15:
                answer += "• Cool temperatures - Delay planting of warm-season crops\n"
            
            answer += "\n📅 Recommended Activities:\n"
            
            # Day-by-day recommendations
            for i, day_data in enumerate(next_week[:3]):
                date = (datetime.now() + timedelta(days=i+1)).strftime("%a, %b %d")
                rainfall = day_data.get('rainfall', 0)
                temp_max = day_data.get('temp_max', 25)
                
                if rainfall < 2 and temp_max < 32:
                    answer += f"• {date}: Good day for field operations\n"
                elif rainfall > 10:
                    answer += f"• {date}: Avoid field work due to rain\n"
                else:
                    answer += f"• {date}: Monitor conditions before fieldwork\n"
        
        return {
            'answer': answer,
            'sources': ['Weather Forecast', 'Agricultural Calendar'],
            'confidence': 0.82,
            'suggestions': [
                "Get crop-specific calendars",
                "View regional planting guides",
                "Check soil preparation tips"
            ]
        }
    
    async def _generate_alerts_response(
        self, query: str, weather_data: Dict[str, Any], location: str, context: List[Dict] = None
    ) -> Dict[str, Any]:
        """Generate weather alerts and warnings"""
        
        alerts = []
        current = weather_data.get('current', {})
        forecast = weather_data.get('forecast', {})
        
        # Check current conditions for alerts
        if current:
            temp = current.get('temperature', 25)
            rainfall = current.get('rainfall', 0)
            wind_speed = current.get('wind_speed', 0)
            
            if temp > 40:
                alerts.append("🔥 HEAT WAVE WARNING: Extremely high temperatures. Protect crops and livestock.")
            elif temp < 5:
                alerts.append("❄️ FROST ALERT: Very low temperatures may damage crops.")
            
            if rainfall > 50:
                alerts.append("⛈️ HEAVY RAIN ALERT: Risk of waterlogging and crop damage.")
            
            if wind_speed > 40:
                alerts.append("💨 HIGH WIND WARNING: Strong winds may damage standing crops.")
        
        # Check forecast for upcoming alerts
        if forecast.get('daily'):
            for i, day_data in enumerate(forecast['daily'][:3]):
                date = (datetime.now() + timedelta(days=i+1)).strftime("%b %d")
                day_rainfall = day_data.get('rainfall', 0)
                day_temp_max = day_data.get('temp_max', 25)
                
                if day_rainfall > 75:
                    alerts.append(f"🌊 FLOOD RISK ({date}): Very heavy rainfall expected.")
                elif day_temp_max > 42:
                    alerts.append(f"🔥 EXTREME HEAT ({date}): Take protective measures.")
        
        if alerts:
            answer = f"⚠️ Weather Alerts for {location}:\n\n"
            for alert in alerts:
                answer += f"{alert}\n\n"
            
            answer += "🛡️ Protective Measures:\n"
            answer += "• Monitor crops closely\n"
            answer += "• Ensure adequate water supply\n"
            answer += "• Secure farm equipment\n"
            answer += "• Consider crop insurance claims if applicable\n"
            
            confidence = 0.95
        else:
            answer = f"✅ No severe weather alerts for {location} at this time.\n\n"
            answer += "Continue regular farming activities while monitoring weather updates."
            confidence = 0.8
        
        return {
            'answer': answer,
            'sources': ['Weather Monitoring System', 'IMD Alerts'],
            'confidence': confidence,
            'suggestions': [
                "Set up weather notifications",
                "Get crop protection tips",
                "View insurance information"
            ]
        }
    
    async def _generate_general_response(
        self, query: str, weather_data: Dict[str, Any], location: str, context: List[Dict] = None
    ) -> Dict[str, Any]:
        """Generate general weather response"""
        
        current = weather_data.get('current')
        forecast = weather_data.get('forecast')
        
        if current and forecast:
            answer = f"Weather Information for {location}:\n\n"
            
            # Current weather
            temp = current.get('temperature', 'N/A')
            condition = current.get('condition', 'Unknown')
            answer += f"🌤️ Current: {temp}°C, {condition}\n\n"
            
            # Short forecast
            if forecast.get('daily') and len(forecast['daily']) > 0:
                tomorrow = forecast['daily'][0]
                temp_range = f"{tomorrow.get('temp_min', 'N/A')}°C - {tomorrow.get('temp_max', 'N/A')}°C"
                answer += f"📅 Tomorrow: {temp_range}\n"
                answer += f"🌧️ Expected rainfall: {tomorrow.get('rainfall', 0)}mm\n"
            
            confidence = 0.85
        else:
            answer = f"I have general weather information for {location}, but specific data is limited. Please ask about current weather, forecast, or specific agricultural concerns."
            confidence = 0.6
        
        return {
            'answer': answer,
            'sources': ['Weather Service'],
            'confidence': confidence,
            'suggestions': [
                "Ask about current weather",
                "Get 7-day forecast",
                "Check irrigation recommendations"
            ]
        }
    
    def _get_weather_recommendations(self, weather_data: Dict[str, Any], period: str) -> str:
        """Generate weather-based agricultural recommendations"""
        recommendations = []
        
        temp = weather_data.get('temperature', 25)
        humidity = weather_data.get('humidity', 50)
        rainfall = weather_data.get('rainfall', 0)
        
        if temp > 35:
            recommendations.append("• Provide shade/cover for sensitive crops")
            recommendations.append("• Increase irrigation frequency")
        elif temp < 10:
            recommendations.append("• Protect crops from cold damage")
            recommendations.append("• Consider frost protection measures")
        
        if humidity > 80:
            recommendations.append("• Monitor for fungal diseases")
            recommendations.append("• Ensure good air circulation")
        elif humidity < 30:
            recommendations.append("• Increase soil moisture")
            recommendations.append("• Consider mulching")
        
        if rainfall > 25:
            recommendations.append("• Ensure proper drainage")
            recommendations.append("• Postpone fertilizer application")
        elif rainfall == 0 and temp > 30:
            recommendations.append("• Plan for irrigation")
            recommendations.append("• Check soil moisture levels")
        
        return "\n".join(recommendations) if recommendations else ""
    
    def _get_weekly_recommendations(self, daily_forecasts: List[Dict[str, Any]]) -> str:
        """Generate weekly agricultural recommendations"""
        recommendations = []
        
        total_rain = sum(day.get('rainfall', 0) for day in daily_forecasts)
        max_temp = max(day.get('temp_max', 25) for day in daily_forecasts)
        min_temp = min(day.get('temp_min', 15) for day in daily_forecasts)
        
        if total_rain > 100:
            recommendations.append("• Heavy rainfall expected - ensure drainage systems are clear")
            recommendations.append("• Delay any planned fertilizer applications")
        elif total_rain < 20:
            recommendations.append("• Dry period ahead - prepare irrigation schedule")
            recommendations.append("• Consider drought-resistant practices")
        
        if max_temp > 38:
            recommendations.append("• Heat stress likely - provide crop protection")
            recommendations.append("• Schedule field work for cooler hours")
        
        if min_temp < 12:
            recommendations.append("• Cold nights expected - protect sensitive crops")
            recommendations.append("• Monitor for frost formation")
        
        return "\n".join(recommendations) if recommendations else ""
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the weather agent"""
        try:
            # Test weather service connectivity
            test_location = "Delhi"
            test_data = await self.weather_service.get_current_weather(test_location)
            
            return {
                'status': 'healthy',
                'last_check': datetime.now().isoformat(),
                'weather_service': 'connected' if test_data else 'disconnected',
                'capabilities': [
                    'current_weather',
                    'weather_forecast', 
                    'irrigation_advice',
                    'agricultural_timing',
                    'weather_alerts'
                ]
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }