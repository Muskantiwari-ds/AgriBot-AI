# AgriBot AI - Intelligent Agricultural Advisor 🌾

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)

## Overview

AgriBot AI is a comprehensive AI-powered agricultural advisor designed for the Indian agricultural ecosystem. It provides intelligent, context-aware assistance to farmers, financiers, vendors, and other stakeholders in the agricultural industry.

### Key Features

- 🌐 **Multilingual Support**: Hindi, English, and major Indian languages
- 🤖 **Intelligent Query Processing**: Natural language understanding with context awareness
- 🔍 **Multi-domain Knowledge**: Weather, crops, soil, finance, and policy information
- 📱 **Accessible Interface**: Works on low-bandwidth connections
- 🎯 **Hyperlocal Insights**: Location-based recommendations
- 📊 **Data-driven Decisions**: Integration with public agricultural datasets
- 🔒 **Reliable & Explainable**: Fact-checked responses with source attribution

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API    │    │   AI Engine     │
│   (React)       │◄──►│   (FastAPI)      │◄──►│   (Agents)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Database       │    │   Data Sources  │
                       │   (PostgreSQL)   │    │   (APIs/Files)  │
                       └──────────────────┘    └─────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/agribot-ai.git
   cd agribot-ai
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up the frontend**
   ```bash
   cd ../frontend
   npm install
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   # Terminal 1 - Backend
   cd backend
   uvicorn main:app --reload

   # Terminal 2 - Frontend
   cd frontend
   npm start
   ```

## Project Structure

```
agribot-ai/
├── README.md
├── .env.example
├── .gitignore
├── docker-compose.yml
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   ├── dockerfile
├── frontend/
│   ├── package.json
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── agents/
│   │   └── utils/
│   └── dockerfile
├── data/
└── Deployment_guide
```

## Features in Detail

### 1. Multilingual Query Processing
- Supports Hindi, English, Tamil, Telugu, Bengali, and more
- Code-switching detection and handling
- Colloquial language understanding

### 2. Multi-domain Knowledge Integration
- **Weather**: Real-time and forecast data from IMD
- **Crops**: Variety recommendations, planting calendars
- **Soil**: Health analysis, nutrient recommendations
- **Finance**: Credit options, insurance, subsidies
- **Policy**: Government schemes, regulations

### 3. AI Agent System
- **Query Router**: Determines the appropriate specialist agent
- **Weather Agent**: Handles weather-related queries
- **Crop Agent**: Provides crop-specific advice
- **Financial Agent**: Offers financial guidance
- **Policy Agent**: Explains government schemes

### 4. Data Sources
- India Meteorological Department (IMD)
- Agricultural Statistics at a Glance
- Soil Health Card Data
- Market Intelligence Portal
- Government Policy Documents

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

## Data Processing

### Dataset Integration
The system integrates multiple public datasets:

1. **Weather Data**: IMD historical and forecast data
2. **Crop Data**: Variety database from ICAR
3. **Soil Data**: Soil Health Card information
4. **Market Data**: Commodity prices from agmarknet
5. **Policy Data**: Government scheme details

### Processing Pipeline
1. Data ingestion from various sources
2. Cleaning and standardization
3. Feature extraction and embedding generation
4. Storage in vector database for retrieval

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Deployment

### Docker Deployment

```bash
docker-compose up -d
```

### Production Deployment

See [Deployment Guide](docs/deployment.md) for detailed instructions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Indian Meteorological Department for weather data
- Department of Agriculture & Cooperation for agricultural statistics
- All contributors and the open-source community


---

**Built with ❤️ for Indian Agriculture**
