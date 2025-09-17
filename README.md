# LangGraph CSV Analysis Platform

A comprehensive data analysis platform that enables natural language querying of CSV files using advanced AI workflows and real-time processing.

## Overview

This platform provides an intuitive interface for analyzing CSV and Excel files through natural language queries. Built with LangGraph workflows, it supports multi-file analysis, temporal data processing, and advanced statistical operations.

### Key Features

- **Natural Language Queries**: Ask questions about your data in plain English
- **Multi-file Analysis**: Process and correlate data across multiple CSV/Excel files
- **Real-time Processing**: WebSocket-powered progress updates during analysis
- **Advanced Analytics**: Statistical correlation, anomaly detection, and forecasting
- **Multi-LLM Support**: Supports OpenAI, Anthropic, and Google Gemini APIs
- **Session Persistence**: Maintains conversation context across sessions
- **Production Ready**: Comprehensive error handling and retry mechanisms

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn
- LLM API key (OpenAI, Anthropic, or Google)

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
   ```env
   OPENAI_API_KEY=your_api_key_here
   # OR
   ANTHROPIC_API_KEY=your_api_key_here
   # OR
   GOOGLE_API_KEY=your_api_key_here
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
| `OPENAI_API_KEY` | OpenAI API key | Yes* |
| `ANTHROPIC_API_KEY` | Anthropic API key | Yes* |
| `GOOGLE_API_KEY` | Google Gemini API key | Yes* |
| `DEFAULT_PROVIDER` | Default LLM provider (openai/anthropic/google) | No |
| `DATABASE_URL` | Database connection string | No |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | No |

*At least one API key is required

### API Configuration

The system automatically detects available API keys and configures providers accordingly. Priority order:
1. OpenAI (if API key available)
2. Anthropic (if API key available)
3. Google Gemini (if API key available)

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

1. **API Key Errors**
   - Ensure API key is correctly set in `.env` file
   - Verify API key has sufficient credits/permissions
   - Check API key format (should start with appropriate prefix)

2. **Port Conflicts**
   - Backend runs on port 8000, frontend on port 3000
   - Use `./deploy.sh --port 8080` to change backend port
   - Check for running processes: `lsof -i :8000`

3. **Installation Issues**
   - Ensure Python 3.8+ and Node.js 14+ are installed
   - Use virtual environment for Python dependencies
   - Clear npm cache: `npm cache clean --force`

4. **File Upload Issues**
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
