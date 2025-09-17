# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a **production-grade Historical Multi-Table Data Analysis system** with an AI-powered conversational interface. The project follows a versioned development roadmap (V1 → V2 → V3) with clear evolution from MVP to production.

**Current Status**: Version 2 (Enhanced) - Multi-temporal analysis with LangGraph orchestration and LLM integration
**Architecture**: Full-stack application with FastAPI backend, React frontend, PostgreSQL database, Redis caching, and advanced LangGraph workflow system

## Development Commands

### Quick Start (Version 1)
```bash
# Full setup using provided script
bash setup_v1.sh

# Manual setup - Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app/database.py
uvicorn app.main:app --reload

# Frontend (optional for V1)
cd frontend
npm install
npm start
```

### Quick Start (Version 2) - ENHANCED
```bash
# V2 setup with PostgreSQL, Redis, and LangGraph
cp .env.v2 .env  # Use V2 configuration
cd backend

# Install V2 dependencies
pip install -r ../config/requirements-v2.txt

# Set up PostgreSQL database (requires PostgreSQL running)
alembic upgrade head

# Start backend with V2 features
uvicorn app.main:app --reload --env-file ../.env

# Start Celery workers (background tasks)
celery -A app.celery_app worker --loglevel=info

# Frontend with WebSocket support
cd ../frontend
npm install
npm start
```

### Testing
```bash
# Backend tests
cd backend && python -m pytest
cd backend && python -m pytest --cov=app  # with coverage
cd backend && python -m pytest tests/test_analytics.py  # specific test file

# V2: LangGraph workflow tests
cd backend && python -m pytest tests/test_langgraph_workflow.py  # LangGraph tests
cd backend && python -m pytest tests/test_llm_providers.py  # LLM provider tests

# V2: Integration tests
cd backend && python -m pytest tests/integration/  # Full workflow tests

# Frontend tests
cd frontend && npm test
cd frontend && npm test -- --coverage
```

### Development Servers
```bash
# Backend API (default: http://localhost:8000)
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend React app (default: http://localhost:3000)
cd frontend && npm start

# API documentation
# - Swagger UI: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

### Docker Operations
```bash
# Version 1 (SQLite-based)
docker-compose up -d
docker-compose logs -f backend
docker-compose down

# Version 2 (PostgreSQL + Redis + LangGraph)
docker-compose -f docker-compose.v2.yml up -d
docker-compose -f docker-compose.v2.yml up --profile monitoring  # includes Prometheus/Grafana
docker-compose -f docker-compose.v2.yml down
```

### Database Operations
```bash
# V1: SQLite database
cd backend && python app/database.py  # Initialize tables

# V2: PostgreSQL with migrations
cd backend
alembic upgrade head  # Apply migrations
alembic revision --autogenerate -m "Migration name"  # Create new migration
alembic downgrade -1  # Rollback one migration

# V2: Database management
psql -h localhost -U data_analyst -d data_analysis_v2  # Connect to database
```

## Architecture Overview

### Multi-Version Design Philosophy
The codebase is designed with clear version boundaries and progressive enhancement:

- **Version 1 (MVP)**: SQLite + Basic FastAPI + Simple React + Pattern-based chat
- **Version 2 (Enhanced)**: PostgreSQL + LangGraph + LLM integration + Advanced React
- **Version 3 (Production)**: + Redis + Celery + Authentication + Kubernetes + Monitoring

### Backend Architecture (FastAPI)
```
backend/
├── app/
│   ├── main.py          # FastAPI app with CORS, static files, router inclusion
│   ├── database.py      # SQLite models: FileModel, SessionModel, MessageModel
│   └── config.py        # Configuration management
├── routers/             # API endpoints organized by domain
│   ├── files.py         # Upload, preview, schema analysis
│   ├── analytics.py     # Basic operations (mean, sum, count, max, min)
│   └── chat.py          # Pattern-matching conversational interface
├── services/            # Business logic layer (placeholder for V2)
└── models/              # Data models (placeholder for V2)
```

### Key Backend Components

**File Processing Pipeline**:
1. `files.py`: Upload validation → DataFrame analysis → Column categorization → Database storage
2. `analytics.py`: File retrieval → DataFrame operations → Result formatting with NaN handling
3. `chat.py`: Intent parsing → Context retrieval → Response generation → Session management

**Database Schema (SQLite)**:
- `files`: File metadata with JSON column analysis (numeric/categorical/date)
- `sessions`: Chat session tracking
- `messages`: Conversational history with optional analysis results
- `analysis_results`: Cached computation results

### Frontend Architecture (React)
The frontend follows a component-based structure with Material-UI:

```
frontend/src/
├── components/
│   ├── FileUpload/      # Drag-and-drop CSV upload
│   ├── DataPreview/     # Table visualization
│   ├── Analytics/       # Operation controls & results display
│   └── Chat/            # Conversational interface
├── services/
│   └── api.js           # Centralized API client with proxy to :8000
└── hooks/               # Custom React hooks for state management
```

### Data Flow Patterns

**File Upload Flow**:
`FileUpload.jsx` → `POST /api/files/upload` → `analyze_dataframe()` → `FileModel.create()` → Database + File system storage

**Analytics Flow**:
User query → `parse_query_intent()` → `FileModel.get_by_id()` → `pd.read_csv()` → `perform_basic_analytics()` → JSON response with NaN handling

**Chat Flow**:
`ChatInterface.jsx` → `POST /api/chat/query` → Intent parsing → File context injection → Pattern-based response → Session storage

### Version 2 Enhancements (IMPLEMENTED)

**LangGraph Workflow System**: Complete 8-node workflow for multi-temporal data analysis:
1. `parse_files` - Ingest multiple files, extract schemas, align columns
2. `plan_operations` - LLM-powered analysis planning (single-table vs cross-table)
3. `align_timeseries` - Temporal alignment for cross-table reasoning
4. `generate_code` - LLM generates Python pandas code for analysis
5. `validate_code` - Syntax and logic validation with retry mechanism
6. `execute_code` - Safe code execution with error handling
7. `trend_analysis` - Pattern detection and trend analysis
8. `explain_result` - Generate narrative explanations and actionable insights

**LLM Provider Abstraction**: Unified interface supporting:
- Google Gemini (default)
- OpenAI GPT-4
- Ollama (local models)
- Mock responses for development

**Advanced Database Schema**: PostgreSQL with:
- Multi-temporal file tracking
- LangGraph execution state management
- Advanced caching and performance optimization
- Background task orchestration

**Production Features**:
- Celery background task processing
- Redis caching layer
- Comprehensive error handling and logging
- Database migrations with Alembic

## Development Guidelines

### File Structure Conventions
- Backend follows domain-driven router organization
- Database models use JSON columns for flexible schema evolution
- All pandas operations include explicit NaN handling for JSON compliance
- File uploads generate UUID-based names to prevent conflicts

### Error Handling Patterns
- FastAPI routers use HTTPException with descriptive error messages
- File operations include cleanup on failure (unlinking uploaded files)
- Database operations use proper connection management with context
- pandas operations wrap statistical calculations with NaN conversion

### API Design Principles
- RESTful endpoints with clear resource hierarchy (`/api/{domain}/{action}`)
- Consistent response formats with metadata (file_id, filename, timestamps)
- Optional parameters use Pydantic models with sensible defaults
- Analytics operations support both single-column and grouped analysis

### Session Management
- Chat sessions use UUID-based identification
- Session context includes file references for analysis context
- Message history maintains both user queries and system responses
- Analysis results are optionally stored with messages for caching

### Testing Strategy
- Backend uses pytest with asyncio support
- File upload testing requires temporary file handling
- Analytics testing validates NaN edge cases and statistical accuracy
- Chat testing focuses on intent parsing and response generation

## Environment Configuration

### Version 1 (.env)
```bash
DATABASE_URL=sqlite:///./data_analysis.db
API_HOST=localhost
API_PORT=8000
MAX_FILE_SIZE=50MB
ALLOWED_FILE_TYPES=csv,xlsx,xls
UPLOAD_DIR=./uploads
```

### Version 2 (.env.v2)
```bash
DATABASE_URL=postgresql+asyncpg://data_analyst:secure_password_2024@postgres:5432/data_analysis_v2
REDIS_URL=redis://:redis_password_2024@redis:6379/0
DEFAULT_LLM_PROVIDER=gemini
# LLM API keys configuration
```

### Sample Data Format
The system expects CSV files with these column patterns:
- **Numeric**: Revenue, Units, Unit_Price, Discount  
- **Categorical**: Region, Product, Customer_ID
- **Date**: Order_Date, Delivery_Date

Sample files in `sample_data/` demonstrate expected structure.

## Troubleshooting

### Common Issues
- **File upload fails**: Check file size (<50MB) and format (csv/xlsx/xls)
- **Analytics errors**: Ensure column names match exactly (case-sensitive)
- **Chat responses unclear**: Upload a file first for context-aware responses
- **Database connection**: Run `python backend/app/database.py` to initialize tables

### Development Mode Issues
- Frontend proxy configuration points to backend:8000
- CORS is configured for localhost:3000 and 127.0.0.1:3000
- File uploads are stored in `uploads/` directory (created automatically)

### Version Migration Path
V1 → V2 migration involves:
1. Database migration from SQLite to PostgreSQL
2. LangGraph workflow integration
3. LLM provider configuration
4. Redis cache layer addition