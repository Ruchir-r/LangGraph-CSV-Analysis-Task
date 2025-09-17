# LangGraph CSV Analysis Platform

A comprehensive data analysis platform that enables natural language querying of CSV files using advanced AI workflows and real-time processing.

## Overview

This platform provides an intuitive interface for analyzing CSV and Excel files through natural language queries. Built with LangGraph workflows, it supports multi-file analysis, temporal data processing, and advanced statistical operations.

### Key Features

- **Natural Language Queries**: Ask questions about your data in plain English
- **Multi-file Analysis**: Process and correlate data across multiple CSV/Excel files
- **Real-time Processing**: WebSocket-powered progress updates during analysis
- **Advanced Analytics**: Statistical correlation, anomaly detection, and forecasting
- **Multi-LLM Support**: Google Gemini (recommended), Groq, OpenAI, and Anthropic APIs
- **Session Persistence**: Maintains conversation context across sessions
- **Production Ready**: Comprehensive error handling and retry mechanisms

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn
- AI API key (see API Key Setup below)

### API Key Setup (Required)

You need an API key from one of the supported providers. **Google Gemini is recommended** for the best balance of performance, cost, and reliability.

#### Option 1: Google Gemini (Recommended)
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key (starts with `AIzaSy...`)
5. **Free tier includes**: 15 requests per minute, 1 million tokens per day

#### Option 2: OpenAI
1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Sign in and create a new secret key
3. Copy your API key (starts with `sk-...`)
4. **Note**: Requires payment after free trial

#### Option 3: Anthropic
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign in and generate an API key
3. Copy your API key (starts with `sk-ant-...`)
4. **Note**: Requires payment

#### Option 4: Groq (Fast, Free Alternative)
1. Visit [Groq Console](https://console.groq.com/keys)
2. Sign in and create an API key
3. Copy your API key (starts with `gsk_...`)
4. **Free tier**: High-speed inference with rate limits

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Ruchir-r/LangGraph-CSV-Analysis-Task.git
   cd LangGraph-CSV-Analysis-Task
   ```

2. **Set up environment variables**
   ```bash
   cp backend/.env.example backend/.env
   ```
   
   Edit `backend/.env` and add your API key:
   
   **For Google Gemini (Recommended):**
   ```env
   GOOGLE_API_KEY=AIzaSy...
   DEFAULT_LLM_PROVIDER=google
   DEFAULT_MODEL=gemini-1.5-flash
   ```
   
   **For Groq (Fast & Free):**
   ```env
   GROQ_API_KEY=gsk_...
   DEFAULT_LLM_PROVIDER=groq
   DEFAULT_MODEL=llama-3.1-8b-instant
   ```
   
   **For OpenAI:**
   ```env
   OPENAI_API_KEY=sk-...
   DEFAULT_LLM_PROVIDER=openai
   DEFAULT_MODEL=gpt-4o-mini
   ```
   
   **For Anthropic:**
   ```env
   ANTHROPIC_API_KEY=sk-ant-...
   DEFAULT_LLM_PROVIDER=anthropic
   DEFAULT_MODEL=claude-3-haiku-20240307
   ```

3. **Install dependencies**
   ```bash
   # Backend dependencies
   cd backend
   pip install -r requirements.txt
   cd ..
   
   # Frontend dependencies
   cd frontend
   npm install
   cd ..
   ```

4. **Start the application**
   ```bash
   # Option 1: Use deployment script (recommended)
   ./deploy.sh
   
   # Option 2: Manual startup
   # Terminal 1 - Backend
   cd backend && python main.py
   
   # Terminal 2 - Frontend
   cd frontend && npm start
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Usage

### Basic Analysis

1. **Upload Files**: Use the web interface to upload CSV or Excel files
2. **Ask Questions**: Type natural language queries about your data
3. **View Results**: Get comprehensive analysis with visualizations and insights

### Example Queries

```
"Show average revenue by region for the last two months"
"Which product had the highest growth rate?"
"Detect any anomalies in the sales data"
"What is the correlation between discount and revenue?"
"Forecast next quarter's revenue based on current trends"
```

### Multi-turn Conversations

The system maintains context across questions:

```
User: "How did Product A perform last quarter?"
System: [Provides detailed analysis]

User: "What about compared to Product B?"
System: [Compares both products using previous context]

User: "What should we do to improve performance?"
System: [Provides actionable recommendations]
```

## Architecture

### System Components

- **Frontend**: React application with Material-UI components
- **Backend**: FastAPI server with REST and WebSocket endpoints
- **AI Engine**: LangGraph workflow with 8-node processing pipeline
- **Database**: SQLite for session and file management

### Workflow Pipeline

1. **Parse Files**: Extract and validate data from uploaded files
2. **Plan Operations**: Determine analysis strategy based on query
3. **Align Timeseries**: Synchronize temporal data across files
4. **Generate Code**: Create analysis code using LLM
5. **Validate Code**: Check code safety and correctness
6. **Execute Code**: Run analysis with error handling
7. **Trend Analysis**: Perform statistical analysis and pattern detection
8. **Explain Results**: Generate human-readable insights and recommendations

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google Gemini API key (recommended) | Yes* |
| `GROQ_API_KEY` | Groq API key (fast & free) | Yes* |
| `OPENAI_API_KEY` | OpenAI API key | Yes* |
| `ANTHROPIC_API_KEY` | Anthropic API key | Yes* |
| `DEFAULT_LLM_PROVIDER` | Default LLM provider (google/groq/openai/anthropic) | No |
| `DEFAULT_MODEL` | Default model for the provider | No |
| `DATABASE_URL` | Database connection string | No |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | No |

*At least one API key is required

### Provider Recommendations

1. **Google Gemini** (Recommended)
   - **Best for**: Production use, balanced cost/performance
   - **Free tier**: 15 RPM, 1M tokens/day
   - **Model**: `gemini-1.5-flash` (fast) or `gemini-1.5-pro` (advanced)

2. **Groq** (Fast & Free)
   - **Best for**: Development, high-speed inference
   - **Free tier**: Rate-limited but very fast
   - **Model**: `llama-3.1-8b-instant`

3. **OpenAI** (Premium)
   - **Best for**: Advanced analysis, requires payment
   - **Model**: `gpt-4o-mini` (cost-effective) or `gpt-4o` (advanced)

4. **Anthropic** (Premium)
   - **Best for**: Complex reasoning, requires payment
   - **Model**: `claude-3-haiku-20240307` (fast) or `claude-3-sonnet-20240229` (balanced)

### API Configuration

The system automatically detects available API keys and uses the configured default provider. If no default is specified, priority order:
1. Google Gemini (if API key available)
2. Groq (if API key available)
3. OpenAI (if API key available)
4. Anthropic (if API key available)

## Development

### Running Tests

```bash
# Run all tests
cd tests && python -m pytest

# Run with coverage
cd tests && python -m pytest --cov=../ --cov-report=html

# Run specific test categories
cd tests && python -m pytest test_integration.py
cd tests && python -m pytest test_api.py
```

### Development Setup

```bash
# Backend development
cd backend
pip install -r requirements.txt
python main.py

# Frontend development
cd frontend
npm install
npm start

# Run in development mode with hot reload
./deploy.sh --dev
```

### Project Structure

```
├── backend/
│   ├── app/                 # FastAPI application
│   ├── services/           # Core services and utilities
│   ├── langgraph_workflow.py # AI workflow implementation
│   ├── main.py             # Application entry point
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/                # React application source
│   ├── public/             # Static assets
│   └── package.json        # Node.js dependencies
├── tests/                  # Test suite
├── sample_data/           # Example CSV files
├── deploy.sh              # Deployment script
└── README.md              # This file
```

## API Reference

### REST Endpoints

- `GET /api/v2/health` - Health check
- `POST /api/v2/files/upload` - Upload files
- `GET /api/v2/files/` - List uploaded files
- `POST /api/v2/analysis/simple` - Simple analysis query
- `POST /api/v2/analysis/comprehensive` - Comprehensive analysis
- `GET /api/v2/sessions/` - List sessions
- `GET /api/v2/sessions/{id}` - Get session details

### WebSocket

- `ws://localhost:8000/api/v2/ws/{session_id}` - Real-time progress updates

Full API documentation available at: http://localhost:8000/docs

## Troubleshooting

### Common Issues

1. **API Key Setup Issues**
   
   **Problem**: "No LLM provider configured" or "Invalid API key"
   
   **Solution**:
   ```bash
   # Check your .env file exists
   ls -la backend/.env
   
   # Verify API key format
   cat backend/.env | grep API_KEY
   ```
   
   **Expected formats**:
   - Google Gemini: `AIzaSyABC123...` (39 characters)
   - Groq: `gsk_ABC123...` (starts with gsk_)
   - OpenAI: `sk-proj-ABC123...` or `sk-ABC123...`
   - Anthropic: `sk-ant-api03-ABC123...`
   
   **Common fixes**:
   - Remove quotes around API key in .env file
   - Ensure no spaces before/after the API key
   - Copy the API key directly from provider dashboard
   - Restart the backend after updating .env file

2. **Provider-Specific Issues**
   
   **Google Gemini "API key not valid"**:
   - Ensure you've enabled the Generative AI API in Google Cloud Console
   - Check API key restrictions (if any) in Google AI Studio
   
   **Groq rate limiting**:
   - Free tier has request limits - wait a few minutes and retry
   - Consider upgrading to paid tier for higher limits
   
   **OpenAI "Insufficient quota"**:
   - Add billing information to your OpenAI account
   - Check usage limits in OpenAI dashboard
   
   **Testing your API key**:
   ```bash
   # Test Google Gemini key
   curl "https://generativelanguage.googleapis.com/v1/models?key=YOUR_API_KEY"
   
   # Test OpenAI key
   curl -H "Authorization: Bearer YOUR_API_KEY" https://api.openai.com/v1/models
   ```

3. **Port Conflicts**
   - Backend runs on port 8000, frontend on port 3000
   - Use `./deploy.sh --port 8080` to change backend port
   - Check for running processes: `lsof -i :8000`

4. **Installation Issues**
   - Ensure Python 3.8+ and Node.js 14+ are installed
   - Use virtual environment for Python dependencies
   - Clear npm cache: `npm cache clean --force`

5. **File Upload Issues**
   - Maximum file size: 10MB per file
   - Supported formats: CSV, Excel (.xlsx, .xls)
   - Ensure files have proper headers and structure

### Logs and Debugging

```bash
# View application logs
./deploy.sh --logs

# Check system status
./deploy.sh --status

# Enable debug logging
export LOG_LEVEL=DEBUG
python backend/main.py
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Run test suite: `cd tests && python -m pytest`
5. Commit changes: `git commit -am 'Add feature'`
6. Push to branch: `git push origin feature-name`
7. Create Pull Request

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section above
- Review API documentation at `/docs` endpoint

## Performance and Scalability

- Handles files up to 10MB each
- Supports multiple concurrent sessions
- WebSocket connections for real-time updates
- Optimized for datasets with thousands of rows
- Horizontal scaling ready with stateless design
