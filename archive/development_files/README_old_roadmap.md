# Historical Multi-Table Data Analysis with Conversational Interface

A production-grade application for analyzing historical data across multiple time periods with an AI-powered conversational interface.

## 🚀 Development Roadmap

### Version 1 (MVP - Current) ✅
**Target: 1 hour implementation**
- [x] Basic project structure
- [ ] Single CSV file upload
- [ ] Simple data preview and column detection
- [ ] Hardcoded analysis functions (mean, sum, count)
- [ ] Basic chat interface with predefined responses
- [ ] SQLite database for session storage
- [ ] Simple FastAPI backend

**Technologies:** FastAPI, SQLite, Pandas, React (basic), HTML/CSS

### Version 2 (Enhanced - Week 2)
**Target: Advanced multi-table analysis**
- [ ] Multiple file handling with temporal alignment
- [ ] LLM integration (OpenAI/Ollama) for query understanding
- [ ] Basic LangGraph workflow (3-4 nodes)
- [ ] PostgreSQL database with proper schema
- [ ] Enhanced frontend with data visualization
- [ ] Cross-table operations and basic temporal analysis

**Technologies:** LangGraph, PostgreSQL, OpenAI API, Chart.js, Advanced React

### Version 3 (Production - Week 3-4)
**Target: Full production system**
- [ ] Complete LangGraph workflow with all 6+ nodes
- [ ] Advanced temporal reasoning and trend analysis
- [ ] User authentication and multi-tenant support
- [ ] Redis caching and background workers
- [ ] Production deployment with Docker/K8s
- [ ] Comprehensive testing and monitoring

**Technologies:** Redis, Celery, Docker, Kubernetes, Monitoring stack

## 📁 Project Structure

```
├── README.md              # Main project documentation
├── docker-compose.yml     # Development environment
├── requirements.txt       # Python dependencies
├── .env.example          # Environment configuration template
├── frontend/             # React frontend application
├── backend/              # FastAPI backend services
├── db/                   # Database migrations and models
├── tests/                # Test suites
├── sample_data/          # Example CSV files for testing
└── docs/                 # Additional documentation
```

## 🛠 Quick Start (Version 1)

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Database Setup
```bash
# SQLite database will be created automatically
python backend/app/database.py
```

## 🔧 Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Database
DATABASE_URL=sqlite:///./data_analysis.db

# API Settings
API_HOST=localhost
API_PORT=8000

# Frontend
REACT_APP_API_URL=http://localhost:8000
```

## 📊 Sample Data Format

Version 1 expects CSV files with these columns:
- Numeric columns: Revenue, Units, Unit_Price, Discount
- Categorical columns: Region, Product, Customer_ID
- Date columns: Order_Date, Delivery_Date

See `sample_data/` for examples.

## 🧪 Testing

```bash
# Backend tests
cd backend && python -m pytest

# Frontend tests
cd frontend && npm test
```

## 📝 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🔮 Future Enhancements

- Advanced visualization with D3.js
- Real-time collaboration features
- Integration with external data sources
- Mobile-responsive design
- Advanced security features
