"""
Agent Coordinator - Orchestrates multiple specialized agents
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
from langchain.tools import Tool

from .crop_advisor import CropAdvisorAgent
from .weather_agent import WeatherAgent
from .finance_agent import FinanceAgent
from .pest_disease_agent import PestDiseaseAgent
from ..utils.language_detector import LanguageDetector
from ..utils.response_formatter import ResponseFormatter
from ..models.llm_interface import LLMInterface
from config.settings import settings

logger = logging.getLogger(__name__)

class AgentCoordinator:
    """
    Main coordinator that orchestrates multiple specialized agents
    to provide comprehensive agricultural advice
    """
    
    def __init__(self):
        self.llm_interface = LLMInterface()
        self.language_detector = LanguageDetector()
        self.response_formatter = ResponseFormatter()
        
        # Initialize specialized agents
        self.crop_advisor = CropAdvisorAgent()
        self.weather_agent = WeatherAgent()
        self.finance_agent = FinanceAgent()
        self.pest_disease_agent = PestDiseaseAgent()
        
        # Setup memory for conversation context
        self.memory = ConversationBufferWindowMemory(
            k=5,  # Remember last 5 exchanges
            return_messages=True,
            memory_key="chat_history"
        )
        
        # Initialize the main LLM
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.1,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        self.tools = self._setup_tools()
        
    def _setup_tools(self) -> List[Tool]:
        """Setup tools for the coordinator agent"""
        return [
            Tool(
                name="crop_advisor",
                description="Provides crop selection, planting schedules, cultivation practices, and yield optimization advice",
                func=self.crop_advisor.get_advice
            ),
            Tool(
                name="weather_forecast",
                description="Gets weather forecasts, alerts, and weather-based farming recommendations",
                func=self.weather_agent.get_forecast
            ),
            Tool(
                name="financial_advisor",
                description="Provides information about loans, subsidies, government schemes, and market prices",
                func=self.finance_agent.get_financial_advice
            ),
            Tool(
                name="pest_disease_expert",
                description="Identifies pests and diseases, provides treatment recommendations and prevention strategies",
                func=self.pest_disease_agent.diagnose_and_treat
            )
        ]
    
    async def process_query(self, 
                          query: str, 
                          user_context: Optional[Dict[str, Any]] = None,
                          session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user query through the agent system
        
        Args:
            query: User's agricultural query
            user_context: User location, crop, farm details etc.
            session_id: Session identifier for context
            
        Returns:
            Dictionary containing the response and metadata
        """
        try:
            start_time = datetime.now()
            
            # Detect language
            detected_language = self.language_detector.detect_language(query)
            
            # Translate to English if needed
            english_query = query
            if detected_language != 'en':
                english_query = await self.language_detector.translate_to_english(query)
            
            # Analyze query intent and complexity
            query_analysis = await self._analyze_query(english_query, user_context)
            
            # Route to appropriate agents based on analysis
            agent_responses = await self._route_to_agents(
                english_query, 
                query_analysis, 
                user_context
            )
            
            # Synthesize responses from multiple agents
            synthesized_response = await self._synthesize_responses(
                english_query,
                agent_responses,
                query_analysis,
                user_context
            )
            
            # Translate response back to user's language
            if detected_language != 'en':
                synthesized_response['answer'] = await self.language_detector.translate_from_english(
                    synthesized_response['answer'], 
                    detected_language
                )
            
            # Format the final response
            formatted_response = self.response_formatter.format_response(
                synthesized_response,
                detected_language,
                user_context
            )
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Store in memory for context
            self.memory.save_context(
                {"input": query},
                {"output": formatted_response['answer']}
            )
            
            return {
                "answer": formatted_response['answer'],
                "confidence": formatted_response['confidence'],
                "sources": formatted_response['sources'],
                "recommendations": formatted_response.get('recommendations', []),
                "follow_up_questions": formatted_response.get('follow_up_questions', []),
                "language": detected_language,
                "processing_time": processing_time,
                "agents_used": list(agent_responses.keys()),
                "query_type": query_analysis['type'],
                "urgency": query_analysis.get('urgency', 'normal')
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "answer": "मुझे खुशी होगी कि मैं आपकी मदद कर सकूं, लेकिन अभी मुझे कुछ तकनीकी समस्या का सामना करना पड़ रहा है। कृपया थोड़ी देर बाद कोशिश करें।",
                "confidence": 0.0,
                "sources": [],
                "error": str(e),
                "language": "hi"
            }
    
    async def _analyze_query(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Analyze the query to understand intent and complexity"""
        
        analysis_prompt = f"""
        Analyze this agricultural query and provide a JSON response:
        
        Query: "{query}"
        Context: {json.dumps(context) if context else "None"}
        
        Classify the query and provide:
        {{
            "type": "crop_selection|irrigation|pest_disease|weather|finance|market|general",
            "complexity": "simple|medium|complex",
            "urgency": "low|medium|high|critical",
            "required_agents": ["list of agents needed"],
            "location_required": true/false,
            "temporal_aspect": "immediate|seasonal|long_term",
            "keywords": ["key terms from query"],
            "user_intent": "brief description of what user wants"
        }}
        """
        
        try:
            response = await self.llm_interface.get_completion(analysis_prompt)
            return json.loads(response)
        except Exception as e:
            logger.warning(f"Query analysis failed: {e}")
            return {
                "type": "general",
                "complexity": "medium",
                "urgency": "medium",
                "required_agents": ["crop_advisor"],
                "location_required": True,
                "temporal_aspect": "immediate",
                "keywords": query.split(),
                "user_intent": "Agricultural advice request"
            }
    
    async def _route_to_agents(self, 
                             query: str, 
                             analysis: Dict[str, Any], 
                             context: Optional[Dict] = None) -> Dict[str, Any]:
        """Route query to appropriate specialized agents"""
        
        agent_responses = {}
        required_agents = analysis.get('required_agents', ['crop_advisor'])
        
        # Create tasks for parallel execution
        tasks = []
        
        if 'crop_advisor' in required_agents or analysis['type'] in ['crop_selection', 'general']:
            tasks.append(self._call_crop_advisor(query, context))
        
        if 'weather_agent' in required_agents or analysis['type'] == 'weather':
            tasks.append(self._call_weather_agent(query, context))
        
        if 'finance_agent' in required_agents or analysis['type'] in ['finance', 'market']:
            tasks.append(self._call_finance_agent(query, context))
        
        if 'pest_disease_agent' in required_agents or analysis['type'] == 'pest_disease':
            tasks.append(self._call_pest_disease_agent(query, context))
        
        # Execute agents in parallel
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            agent_names = ['crop_advisor', 'weather_agent', 'finance_agent', 'pest_disease_agent']
            for i, result in enumerate(results):
                if i < len(agent_names) and not isinstance(result, Exception):
                    agent_responses[agent_names[i]] = result
                elif isinstance(result, Exception):
                    logger.error(f"Agent {agent_names[i] if i < len(agent_names) else i} failed: {result}")
        
        return agent_responses
    
    async def _call_crop_advisor(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Call crop advisor agent"""
        try:
            return await self.crop_advisor.get_advice(query, context)
        except Exception as e:
            logger.error(f"Crop advisor failed: {e}")
            return {"error": str(e), "agent": "crop_advisor"}
    
    async def _call_weather_agent(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Call weather agent"""
        try:
            return await self.weather_agent.get_forecast(query, context)
        except Exception as e:
            logger.error(f"Weather agent failed: {e}")
            return {"error": str(e), "agent": "weather_agent"}
    
    async def _call_finance_agent(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Call finance agent"""
        try:
            return await self.finance_agent.get_financial_advice(query, context)
        except Exception as e:
            logger.error(f"Finance agent failed: {e}")
            return {"error": str(e), "agent": "finance_agent"}
    
    async def _call_pest_disease_agent(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Call pest and disease agent"""
        try:
            return await self.pest_disease_agent.diagnose_and_treat(query, context)
        except Exception as e:
            logger.error(f"Pest disease agent failed: {e}")
            return {"error": str(e), "agent": "pest_disease_agent"}
    
    async def _synthesize_responses(self, 
                                  query: str,
                                  agent_responses: Dict[str, Any],
                                  analysis: Dict[str, Any],
                                  context: Optional[Dict] = None) -> Dict[str, Any]:
        """Synthesize responses from multiple agents into coherent advice"""
        
        synthesis_prompt = f"""
        You are an expert agricultural advisor synthesizing information from multiple specialized agents.
        
        Original Query: "{query}"
        Query Analysis: {json.dumps(analysis)}
        User Context: {json.dumps(context) if context else "None"}
        
        Agent Responses:
        {json.dumps(agent_responses, indent=2)}
        
        Synthesize this information into a comprehensive, coherent response that:
        1. Directly answers the user's question
        2. Integrates relevant insights from all agents
        3. Provides actionable recommendations
        4. Highlights any conflicts or uncertainties
        5. Suggests follow-up actions if needed
        
        Format your response as JSON:
        {{
            "answer": "Comprehensive answer to the user's query",
            "confidence": 0.0-1.0,
            "key_recommendations": ["actionable recommendations"],
            "sources": ["data sources used"],
            "caveats": ["important limitations or warnings"],
            "follow_up_questions": ["suggested follow-up questions"]
        }}
        
        Make the response practical, culturally appropriate for Indian farmers, and easy to understand.
        """
        
        try:
            response = await self.llm_interface.get_completion(synthesis_prompt)
            synthesized = json.loads(response)
            
            # Add metadata
            synthesized['synthesis_timestamp'] = datetime.now().isoformat()
            synthesized['agents_consulted'] = list(agent_responses.keys())
            
            return synthesized
            
        except Exception as e:
            logger.error(f"Response synthesis failed: {e}")
            
            # Fallback: return best available response
            best_response = self._get_best_agent_response(agent_responses)
            return {
                "answer": best_response.get('answer', 'मुझे इस समय उत्तर देने में कुछ कठिनाई हो रही है।'),
                "confidence": 0.5,
                "sources": best_response.get('sources', []),
                "key_recommendations": best_response.get('recommendations', []),
                "caveats": ["Fallback response due to synthesis error"],
                "follow_up_questions": []
            }
    
    def _get_best_agent_response(self, agent_responses: Dict[str, Any]) -> Dict[str, Any]:
        """Get the best response when synthesis fails"""
        
        # Priority order for agents
        priority = ['crop_advisor', 'weather_agent', 'finance_agent', 'pest_disease_agent']
        
        for agent in priority:
            if agent in agent_responses and 'error' not in agent_responses[agent]:
                return agent_responses[agent]
        
        # Return any available response
        for response in agent_responses.values():
            if 'error' not in response:
                return response
        
        return {"answer": "No valid response available", "confidence": 0.0}
    
    async def get_follow_up_suggestions(self, 
                                      conversation_history: List[Dict],
                                      user_context: Optional[Dict] = None) -> List[str]:
        """Generate contextual follow-up questions"""
        
        prompt = f"""
        Based on the conversation history and user context, suggest 3-5 relevant follow-up questions
        that would help the farmer make better agricultural decisions.
        
        Conversation History: {json.dumps(conversation_history[-3:], indent=2)}
        User Context: {json.dumps(user_context) if user_context else "None"}
        
        Return as JSON array: ["question1", "question2", "question3"]
        
        Make questions practical, specific to Indian agriculture, and actionable.
        """
        
        try:
            response = await self.llm_interface.get_completion(prompt)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Follow-up generation failed: {e}")
            return [
                "What is the best time to plant crops in my region?",
                "How can I improve soil health naturally?",
                "What government schemes are available for farmers?"
            ]
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear()
    
    def get_conversation_summary(self) -> str:
        """Get summary of current conversation"""
        try:
            messages = self.memory.chat_memory.messages
            if not messages:
                return "No conversation history"
            
            summary = f"Conversation with {len(messages)} messages. "
            summary += f"Last query: {messages[-1].content[:100]}..."
            return summary
        except Exception:
            return "Unable to generate summary"