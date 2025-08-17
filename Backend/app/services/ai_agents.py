"""
AI Agent Service - Main orchestrator for agricultural queries
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import json
import re

from langchain.agents import AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
from sentence_transformers import SentenceTransformer
import numpy as np

from app.core.config import settings
from app.services.agents.weather_agent import WeatherAgent
from app.services.agents.crop_agent import CropAgent
from app.services.agents.financial_agent import FinancialAgent
from app.services.agents.policy_agent import PolicyAgent
from app.services.language_processor import LanguageProcessor
from app.services.knowledge_base import KnowledgeBaseService
from app.utils.location_utils import extract_location

logger = logging.getLogger(__name__)

class AIAgentService:
    """Main AI Agent Service that coordinates different specialized agents"""
    
    def __init__(self):
        self.language_processor = LanguageProcessor()
        self.knowledge_base = KnowledgeBaseService()
        self.model = SentenceTransformer(settings.MODEL_NAME)
        
        # Initialize specialized agents
        self.agents = {
            'weather': WeatherAgent(),
            'crop': CropAgent(),
            'financial': FinancialAgent(),
            'policy': PolicyAgent()
        }
        
        # Query classification keywords
        self.agent_keywords = {
            'weather': [
                'weather', 'rain', 'temperature', 'humidity', 'climate', 
                'monsoon', 'drought', 'frost', 'मौसम', 'बारिश', 'तापमान'
            ],
            'crop': [
                'crop', 'seed', 'variety', 'planting', 'harvest', 'pest', 
                'disease', 'fertilizer', 'फसल', 'बीज', 'खाद'
            ],
            'financial': [
                'loan', 'credit', 'insurance', 'subsidy', 'price', 'market',
                'cost', 'profit', 'ऋण', 'बीमा', 'सब्सिडी', 'कीमत'
            ],
            'policy': [
                'scheme', 'policy', 'government', 'yojana', 'PM-KISAN',
                'registration', 'application', 'योजना', 'सरकार', 'आवेदन'
            ]
        }
        
        logger.info("AI Agent Service initialized")
    
    async def process_query(
        self, 
        query: str, 
        user_id: str = None,
        location: str = None,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process user query and return appropriate response
        
        Args:
            query: User's question in natural language
            user_id: Optional user identifier
            location: User's location
            context: Additional context information
        
        Returns:
            Dictionary containing response and metadata
        """
        start_time = datetime.now()
        
        try:
            # Step 1: Language detection and translation
            language_info = await self.language_processor.detect_language(query)
            original_language = language_info.get('language', 'en')
            confidence = language_info.get('confidence', 0.0)
            
            # Translate to English if needed for processing
            processed_query = query
            if original_language != 'en':
                processed_query = await self.language_processor.translate(
                    query, source_lang=original_language, target_lang='en'
                )
            
            # Step 2: Extract location if not provided
            if not location:
                location = extract_location(processed_query)
            
            # Step 3: Classify query to determine appropriate agent
            agent_type = self._classify_query(processed_query)
            
            # Step 4: Retrieve relevant context from knowledge base
            context_data = await self.knowledge_base.search_relevant_content(
                processed_query, limit=5
            )
            
            # Step 5: Process with appropriate agent
            agent = self.agents.get(agent_type)
            if not agent:
                agent = self.agents['crop']  # Default to crop agent
            
            response = await agent.process_query(
                query=processed_query,
                location=location,
                context=context_data,
                user_context=context or {}
            )
            
            # Step 6: Translate response back to original language if needed
            final_response = response['answer']
            if original_language != 'en':
                final_response = await self.language_processor.translate(
                    response['answer'], 
                    source_lang='en', 
                    target_lang=original_language
                )
            
            # Step 7: Prepare final response
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'answer': final_response,
                'original_query': query,
                'processed_query': processed_query,
                'agent_type': agent_type,
                'language': original_language,
                'language_confidence': confidence,
                'location': location,
                'sources': response.get('sources', []),
                'confidence_score': response.get('confidence', 0.8),
                'processing_time': processing_time,
                'suggestions': response.get('suggestions', []),
                'metadata': {
                    'context_used': len(context_data),
                    'agent_confidence': response.get('confidence', 0.0),
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            logger.info(f"Query processed successfully in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'answer': self._get_fallback_response(original_language),
                'original_query': query,
                'agent_type': 'fallback',
                'language': original_language,
                'error': str(e),
                'processing_time': processing_time,
                'confidence_score': 0.1
            }
    
    def _classify_query(self, query: str) -> str:
        """
        Classify query to determine which agent should handle it
        
        Args:
            query: Processed query string
            
        Returns:
            Agent type (weather, crop, financial, policy)
        """
        query_lower = query.lower()
        scores = {}
        
        # Score each agent based on keyword matches
        for agent_type, keywords in self.agent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                scores[agent_type] = score
        
        # Return agent with highest score, default to crop
        if scores:
            return max(scores, key=scores.get)
        
        # Use semantic similarity as fallback
        query_embedding = self.model.encode([query])
        
        agent_descriptions = {
            'weather': "weather forecast rain temperature climate conditions",
            'crop': "agriculture farming crops seeds planting harvesting",
            'financial': "money loan credit insurance subsidy market prices",
            'policy': "government schemes policies programs registration"
        }
        
        best_match = 'crop'
        best_score = 0.0
        
        for agent_type, description in agent_descriptions.items():
            desc_embedding = self.model.encode([description])
            similarity = np.dot(query_embedding[0], desc_embedding[0])
            
            if similarity > best_score:
                best_score = similarity
                best_match = agent_type
        
        return best_match
    
    def _get_fallback_response(self, language: str = 'en') -> str:
        """Get fallback response in case of errors"""
        fallback_responses = {
            'en': "I apologize, but I'm having trouble understanding your question right now. Please try rephrasing your agricultural query, and I'll do my best to help you.",
            'hi': "मुझे खेद है, मुझे अभी आपका प्रश्न समझने में कठिनाई हो रही है। कृपया अपना कृषि संबंधी प्रश्न दोबारा पूछें, और मैं आपकी सहायता करने की पूरी कोशिश करूंगा।"
        }
        
        return fallback_responses.get(language, fallback_responses['en'])
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        status = {}
        for name, agent in self.agents.items():
            try:
                agent_status = await agent.health_check()
                status[name] = agent_status
            except Exception as e:
                status[name] = {'status': 'error', 'error': str(e)}
        
        return {
            'overall_status': 'healthy' if all(
                s.get('status') == 'healthy' for s in status.values()
            ) else 'degraded',
            'agents': status,
            'timestamp': datetime.now().isoformat()
        }