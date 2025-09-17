#!/bin/bash
# Historical Multi-Table Data Analysis with Conversational Interface
# Production-Grade Startup Script - Phase 2 Complete
# Features: Multi-temporal analysis, Conversational AI, Statistical Analysis, Session Persistence

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="/Users/ruchir/Desktop/GoLLM_task"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
BACKEND_PORT=8000
FRONTEND_PORT=3000
LOG_DIR="$PROJECT_ROOT/logs"
BACKEND_LOG="$LOG_DIR/backend.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

print_success() {
    echo -e "${CYAN}✅ $1${NC}"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -i :$port >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill processes on specific ports
kill_port() {
    local port=$1
    local pids=$(lsof -t -i :$port 2>/dev/null)
    if [ -n "$pids" ]; then
        print_warning "Killing existing processes on port $port"
        echo "$pids" | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Function to check system requirements
check_requirements() {
    print_header "🔍 Checking System Requirements..."
    
    # Check if Python 3 is available
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    print_success "Python 3: $(python3 --version)"
    
    # Check if Node.js is available
    if ! command -v node &> /dev/null; then
        print_error "Node.js is required but not installed"
        exit 1
    fi
    print_success "Node.js: $(node --version)"
    
    # Check if npm is available
    if ! command -v npm &> /dev/null; then
        print_error "npm is required but not installed"
        exit 1
    fi
    print_success "npm: $(npm --version)"
    
    # Check project directories
    if [ ! -d "$BACKEND_DIR" ]; then
        print_error "Backend directory not found: $BACKEND_DIR"
        exit 1
    fi
    print_success "Backend directory: $BACKEND_DIR"
    
    if [ ! -d "$FRONTEND_DIR" ]; then
        print_error "Frontend directory not found: $FRONTEND_DIR"
        exit 1
    fi
    print_success "Frontend directory: $FRONTEND_DIR"
    
    echo ""
}

# Function to start the backend
start_backend() {
    print_header "🚀 Starting Backend (FastAPI V2)..."
    
    cd "$BACKEND_DIR"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_warning "Virtual environment not found. Creating one..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install/update dependencies
    print_status "Installing backend dependencies..."
    pip install --quiet --upgrade pip
    pip install --quiet fastapi uvicorn pandas numpy python-multipart openpyxl python-dotenv
    pip install --quiet langgraph langchain langchain-core
    
    # Check if the backend can start
    print_status "Testing backend configuration..."
    if ! python -c "from app.main import app; print('Backend configuration: OK')" 2>/dev/null; then
        print_error "Backend configuration test failed"
        exit 1
    fi
    
    # Kill any existing backend processes
    kill_port $BACKEND_PORT
    
    # Start backend in background
    print_status "Starting FastAPI server on port $BACKEND_PORT..."
    nohup uvicorn app.main:app --reload --host 0.0.0.0 --port $BACKEND_PORT > "$BACKEND_LOG" 2>&1 &
    BACKEND_PID=$!
    
    # Wait for backend to start
    print_status "Waiting for backend to start..."
    for i in {1..30}; do
        if curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
            print_success "Backend started successfully (PID: $BACKEND_PID)"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Backend failed to start within 30 seconds"
            print_error "Check logs: tail -f $BACKEND_LOG"
            exit 1
        fi
        sleep 1
        echo -n "."
    done
    echo ""
    
    # Test V2 endpoints
    print_status "Testing V2 API endpoints..."
    if curl -s http://localhost:$BACKEND_PORT/api/v2/health > /dev/null 2>&1; then
        print_success "V2 API endpoints are responding"
    else
        print_warning "V2 API endpoints may not be fully ready"
    fi
    
    echo ""
}

# Function to start the frontend
start_frontend() {
    print_header "🎨 Starting Frontend (React V2)..."
    
    cd "$FRONTEND_DIR"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
        print_success "Frontend dependencies installed"
    else
        print_status "Frontend dependencies already installed"
    fi
    
    # Kill any existing frontend processes
    kill_port $FRONTEND_PORT
    
    # Start frontend in background
    print_status "Starting React development server on port $FRONTEND_PORT..."
    
    # Set environment variables for the frontend
    export REACT_APP_API_URL=http://localhost:$BACKEND_PORT
    export REACT_APP_USE_MOCK_API=false
    
    nohup npm start > "$FRONTEND_LOG" 2>&1 &
    FRONTEND_PID=$!
    
    # Wait for frontend to start
    print_status "Waiting for frontend to start..."
    for i in {1..60}; do
        if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
            print_success "Frontend started successfully (PID: $FRONTEND_PID)"
            break
        fi
        if [ $i -eq 60 ]; then
            print_error "Frontend failed to start within 60 seconds"
            print_error "Check logs: tail -f $FRONTEND_LOG"
            exit 1
        fi
        sleep 1
        echo -n "."
    done
    echo ""
}

# Function to display system status
show_status() {
    print_header "📊 System Status"
    echo ""
    
    # Backend status
    if curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
        backend_version=$(curl -s http://localhost:$BACKEND_PORT/ | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
        print_success "Backend (v$backend_version): http://localhost:$BACKEND_PORT"
        print_success "  └── API Documentation: http://localhost:$BACKEND_PORT/docs"
        print_success "  └── V2 Health Check: http://localhost:$BACKEND_PORT/api/v2/health"
    else
        print_error "Backend: Not responding"
    fi
    
    # Frontend status  
    if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
        print_success "Frontend: http://localhost:$FRONTEND_PORT"
        print_success "  └── Upload Files: http://localhost:$FRONTEND_PORT/upload"
        print_success "  └── AI Assistant: http://localhost:$FRONTEND_PORT/chat"
        print_success "  └── Results: http://localhost:$FRONTEND_PORT/results"
    else
        print_error "Frontend: Not responding"
    fi
    
    echo ""
    print_header "🛠️  Development Tools"
    print_status "Backend logs: tail -f $BACKEND_LOG"
    print_status "Frontend logs: tail -f $FRONTEND_LOG"
    print_status "Stop services: pkill -f 'uvicorn\\|npm start'"
    
    echo ""
}

# Function to run system tests
run_tests() {
    print_header "🧪 Running System Tests..."
    
    # Test backend health
    print_status "Testing backend health..."
    backend_health=$(curl -s http://localhost:$BACKEND_PORT/health | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    if [ "$backend_health" = "healthy" ]; then
        print_success "Backend health check: PASSED"
    else
        print_error "Backend health check: FAILED"
        return 1
    fi
    
    # Test V2 API
    print_status "Testing V2 API..."
    v2_status=$(curl -s http://localhost:$BACKEND_PORT/api/v2/health | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    if [ "$v2_status" = "healthy" ]; then
        print_success "V2 API health check: PASSED"
    else
        print_error "V2 API health check: FAILED"
        return 1
    fi
    
    # Test workflow
    print_status "Testing LangGraph workflow..."
    workflow_status=$(curl -s http://localhost:$BACKEND_PORT/api/v2/test/workflow | grep -o '"integration_status":"[^"]*"' | cut -d'"' -f4)
    if [ "$workflow_status" = "production_ready" ]; then
        print_success "LangGraph workflow test: PASSED"
    else
        print_error "LangGraph workflow test: FAILED"
        return 1
    fi
    
    # Test frontend
    print_status "Testing frontend..."
    if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
        print_success "Frontend connectivity: PASSED"
    else
        print_error "Frontend connectivity: FAILED"
        return 1
    fi
    
    print_success "All system tests PASSED!"
    echo ""
}

# Function to handle cleanup on exit
cleanup() {
    print_header "🛑 Shutting down services..."
    
    # Kill background processes
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Kill processes on ports
    kill_port $BACKEND_PORT
    kill_port $FRONTEND_PORT
    
    print_success "Services stopped"
    exit 0
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help, -h     Show this help message"
    echo "  --test, -t     Run system tests after startup"
    echo "  --logs, -l     Show logs after startup"
    echo "  --status, -s   Show status only (don't start services)"
    echo ""
    echo "Examples:"
    echo "  $0              # Start both services"
    echo "  $0 --test       # Start services and run tests"
    echo "  $0 --logs       # Start services and show logs"
    echo "  $0 --status     # Show current status"
    echo ""
}

# Main execution
main() {
    # Handle command line arguments
    SHOW_LOGS=false
    RUN_TESTS=false
    STATUS_ONLY=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_usage
                exit 0
                ;;
            --test|-t)
                RUN_TESTS=true
                shift
                ;;
            --logs|-l)
                SHOW_LOGS=true
                shift
                ;;
            --status|-s)
                STATUS_ONLY=true
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Set up signal handlers
    trap cleanup SIGINT SIGTERM
    
    # Show header
    clear
    print_header "
╔════════════════════════════════════════════════════════════╗
║        Historical Multi-Table Data Analysis V2            ║
║           Enhanced System Startup Script                  ║
╚════════════════════════════════════════════════════════════╝
"
    
    if [ "$STATUS_ONLY" = true ]; then
        show_status
        exit 0
    fi
    
    # Run startup sequence
    check_requirements
    start_backend
    start_frontend
    show_status
    
    # Run tests if requested
    if [ "$RUN_TESTS" = true ]; then
        run_tests
    fi
    
    # Show logs if requested
    if [ "$SHOW_LOGS" = true ]; then
        print_header "📋 Live Logs (Press Ctrl+C to stop)"
        echo ""
        print_status "Backend logs (port $BACKEND_PORT):"
        echo "─────────────────────────────────"
        tail -f "$BACKEND_LOG" &
        TAIL_PID1=$!
        
        sleep 2
        print_status "Frontend logs (port $FRONTEND_PORT):"
        echo "─────────────────────────────────"
        tail -f "$FRONTEND_LOG" &
        TAIL_PID2=$!
        
        # Wait for interrupt
        wait
    else
        # Keep script running
        print_header "🎉 System Started Successfully!"
        echo ""
        print_success "Frontend: http://localhost:$FRONTEND_PORT"
        print_success "Backend:  http://localhost:$BACKEND_PORT"
        print_success "API Docs: http://localhost:$BACKEND_PORT/docs"
        echo ""
        print_status "Press Ctrl+C to stop all services"
        print_status "Or run: $0 --logs to see live logs"
        
        # Wait for interrupt
        while true; do
            sleep 1
        done
    fi
}

# Run main function
main "$@"