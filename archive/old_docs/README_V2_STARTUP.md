# Historical Multi-Table Data Analysis V2 - Startup Scripts

This document explains how to use the V2 startup scripts to run the enhanced Historical Multi-Table Data Analysis system.

## 🚀 Quick Start

### Start Both Services (Recommended)
```bash
./start_v2.sh
```

This will:
- ✅ Check system requirements (Python 3, Node.js, npm)
- ✅ Start the FastAPI backend on port 8000
- ✅ Start the React frontend on port 3000
- ✅ Display system status and URLs

### Stop All Services
```bash
./stop_v2.sh
```

## 📋 Available Commands

### Basic Usage
```bash
./start_v2.sh                 # Start both services
./start_v2.sh --help          # Show help message
./start_v2.sh --status        # Show current status only
```

### Advanced Options
```bash
./start_v2.sh --test          # Start services and run system tests
./start_v2.sh --logs          # Start services and show live logs
```

### Service Management
```bash
./stop_v2.sh                  # Stop all services
```

## 🌐 Access Points

After successful startup, you can access:

- **Frontend Application**: http://localhost:3000
  - File Upload: http://localhost:3000/upload
  - AI Assistant: http://localhost:3000/chat
  - Analysis Results: http://localhost:3000/results

- **Backend API**: http://localhost:8000
  - API Documentation: http://localhost:8000/docs
  - V2 Health Check: http://localhost:8000/api/v2/health
  - System Status: http://localhost:8000/api/v2/system/status

## 🛠️ Development Tools

### View Logs
```bash
# Backend logs
tail -f logs/backend.log

# Frontend logs
tail -f logs/frontend.log

# Live logs (both services)
./start_v2.sh --logs
```

### System Testing
```bash
# Run comprehensive system tests
./start_v2.sh --test
```

The test suite includes:
- Backend health check
- V2 API availability
- LangGraph workflow testing
- Frontend connectivity
- End-to-end integration

## 📁 File Structure

```
GoLLM_task/
├── start_v2.sh              # Main startup script
├── stop_v2.sh               # Stop script
├── logs/                    # Auto-created log directory
│   ├── backend.log         # Backend service logs
│   └── frontend.log        # Frontend service logs
├── backend/                 # FastAPI backend
│   ├── venv/               # Python virtual environment
│   └── app/                # Application code
└── frontend/               # React frontend
    ├── node_modules/       # Node.js dependencies
    └── src/                # Application code
```

## ⚙️ Configuration

The startup script automatically configures:

### Backend
- **Port**: 8000
- **Environment**: Development with auto-reload
- **Dependencies**: FastAPI, LangGraph, pandas, etc.
- **Virtual Environment**: Automatically created/activated

### Frontend
- **Port**: 3000
- **API URL**: http://localhost:8000 (auto-configured)
- **Environment**: Development with hot reload
- **Dependencies**: React, Material-UI, etc.

## 🔧 Troubleshooting

### Common Issues

#### "Port already in use"
```bash
./stop_v2.sh  # Stop existing services
./start_v2.sh # Restart
```

#### "Python 3 not found"
Install Python 3:
```bash
brew install python3  # macOS with Homebrew
```

#### "Node.js not found"
Install Node.js:
```bash
brew install node     # macOS with Homebrew
```

#### Backend fails to start
Check the logs:
```bash
tail -f logs/backend.log
```

Common solutions:
- Ensure virtual environment dependencies are installed
- Check that port 8000 is available
- Verify Python path in virtual environment

#### Frontend fails to start
Check the logs:
```bash
tail -f logs/frontend.log
```

Common solutions:
- Run `npm install` in the frontend directory
- Ensure port 3000 is available
- Check Node.js version compatibility

### Manual Debugging

#### Check Process Status
```bash
lsof -i :8000  # Check backend port
lsof -i :3000  # Check frontend port
ps aux | grep -E "(uvicorn|npm)" # Check running processes
```

#### Manual Service Start
```bash
# Backend only
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Frontend only
cd frontend
npm start
```

## 🚦 System Requirements

- **Operating System**: macOS, Linux, or Windows WSL
- **Python**: 3.8+ (with pip)
- **Node.js**: 16+ (with npm)
- **Memory**: 4GB+ recommended
- **Storage**: 2GB+ free space

## 🎯 Features Enabled

The V2 startup script enables:

### Backend Features
- ✅ FastAPI v2.0.0 with enhanced routing
- ✅ LangGraph 8-node workflow system
- ✅ WebSocket support for real-time updates
- ✅ Multi-temporal data analysis capabilities
- ✅ Advanced error handling and logging
- ✅ Production-grade API endpoints

### Frontend Features
- ✅ React v2.0.0 with Material-UI
- ✅ Drag-and-drop file upload
- ✅ Real-time chat interface with AI
- ✅ Interactive analysis results dashboard
- ✅ Responsive design for all devices
- ✅ WebSocket integration for live updates

### Development Features
- ✅ Auto-reload for both services
- ✅ Comprehensive logging
- ✅ System health monitoring
- ✅ Automated testing suite
- ✅ Easy service management

## 📝 Examples

### Basic Development Workflow
```bash
# Start development environment
./start_v2.sh

# Open browser to http://localhost:3000
# Upload some CSV files
# Test the AI chat interface
# View analysis results

# When done
./stop_v2.sh
```

### Production Testing
```bash
# Start with comprehensive testing
./start_v2.sh --test

# Monitor system with live logs
./start_v2.sh --logs

# Check status anytime
./start_v2.sh --status
```

## 🆘 Support

If you encounter issues:

1. **Check the logs**: `./start_v2.sh --logs`
2. **Run system tests**: `./start_v2.sh --test`
3. **Restart services**: `./stop_v2.sh && ./start_v2.sh`
4. **Check requirements**: Ensure Python 3, Node.js, and npm are installed

---

**Happy analyzing!** 🎉 The V2 Enhanced System is ready for production use.