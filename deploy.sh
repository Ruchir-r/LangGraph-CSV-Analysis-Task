#!/bin/bash

# =============================================================================
# Historical Multi-Table Data Analysis - Production Deployment Script
# Version 2.0.0 - Clean & Production Ready
# =============================================================================

set -euo pipefail  # Exit on any error, undefined variable, or pipe failure

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
LOGS_DIR="$SCRIPT_DIR/logs"

# Ensure logs directory exists
mkdir -p "$LOGS_DIR"

print_header() {
    echo -e "\n${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║   Historical Multi-Table Data Analysis System               ║${NC}"
    echo -e "${BLUE}║                Production Deployment                         ║${NC}"
    echo -e "${BLUE}║                    Version 2.0.0                            ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}\n"
}

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}✅${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠️${NC} $1"; }
print_error() { echo -e "${RED}❌${NC} $1"; }

check_requirements() {
    print_info "Checking system requirements..."
    
    # Check Python 3
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        print_success "Python 3: $PYTHON_VERSION"
    else
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js: $NODE_VERSION"
    else
        print_error "Node.js is required but not installed"
        exit 1
    fi
    
    # Check npm
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        print_success "npm: $NPM_VERSION"
    else
        print_error "npm is required but not installed"
        exit 1
    fi
    
    # Check directories
    for dir in "$BACKEND_DIR" "$FRONTEND_DIR"; do
        if [[ -d "$dir" ]]; then
            print_success "Directory exists: $(basename "$dir")"
        else
            print_error "Required directory not found: $dir"
            exit 1
        fi
    done
}

setup_backend() {
    print_info "Setting up backend..."
    
    cd "$BACKEND_DIR"
    
    # Create virtual environment if it doesn't exist
    if [[ ! -d "venv" ]]; then
        print_info "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install/update dependencies (like old script)
    print_info "Installing backend dependencies..."
    pip install --quiet --upgrade pip
    pip install --quiet fastapi uvicorn pandas numpy python-multipart openpyxl python-dotenv
    pip install --quiet langgraph langchain langchain-core || true  # Optional LLM deps
    
    # Test backend configuration (like old script)
    print_info "Testing backend configuration..."
    if python -c "from app.main import app; print('Backend configuration: OK')" 2>/dev/null; then
        print_success "Backend configuration validated"
    else
        print_error "Backend configuration test failed"
        return 1
    fi
}

setup_frontend() {
    print_info "Setting up frontend..."
    
    cd "$FRONTEND_DIR"
    
    # Install dependencies if needed
    if [[ ! -d "node_modules" ]] || [[ -z "$(ls -A node_modules 2>/dev/null)" ]]; then
        print_info "Installing Node.js dependencies..."
        npm install --silent
    else
        print_success "Frontend dependencies already installed"
    fi
}

# Function to kill processes on specific ports (from old script)
kill_port() {
    local port=$1
    local pids=$(lsof -t -i :$port 2>/dev/null)
    if [ -n "$pids" ]; then
        print_info "Stopping existing processes on port $port"
        echo "$pids" | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

stop_existing_services() {
    print_info "Stopping any existing services..."
    
    # Kill processes on both ports (like old script)
    kill_port 8000
    kill_port 3000
    
    print_success "Existing services stopped"
}

start_backend() {
    print_info "Starting backend (FastAPI)..."
    
    cd "$BACKEND_DIR"
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Kill any existing backend processes (like old script)
    kill_port 8000
    
    # Start backend in background (exact same as old script)
    print_info "Starting FastAPI server on port 8000..."
    nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > "$LOGS_DIR/backend.log" 2>&1 &
    BACKEND_PID=$!
    
    # Wait for backend to start (exact same as old script)
    print_info "Waiting for backend to start..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            print_success "Backend started successfully (PID: $BACKEND_PID)"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Backend failed to start within 30 seconds"
            print_error "Check logs: tail -f $LOGS_DIR/backend.log"
            return 1
        fi
        sleep 1
        echo -n "."
    done
    echo ""
    
    # Test V2 endpoints (like old script)
    print_info "Testing V2 API endpoints..."
    if curl -s http://localhost:8000/api/v2/health > /dev/null 2>&1; then
        print_success "V2 API endpoints are responding"
    else
        print_warning "V2 API endpoints may not be fully ready"
    fi
}

start_frontend() {
    print_info "Starting frontend (React)..."
    
    cd "$FRONTEND_DIR"
    
    # Kill any existing frontend processes (like old script)
    kill_port 3000
    
    # Start frontend in background (exact same as old script)
    print_info "Starting React development server on port 3000..."
    
    # Set environment variables for the frontend
    export REACT_APP_API_URL=http://localhost:8000
    export REACT_APP_USE_MOCK_API=false
    export BROWSER=none  # Prevent automatic browser opening
    
    nohup npm start > "$LOGS_DIR/frontend.log" 2>&1 &
    FRONTEND_PID=$!
    
    # Wait for frontend to start (exact same as old script)
    print_info "Waiting for frontend to start..."
    for i in {1..60}; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            print_success "Frontend started successfully (PID: $FRONTEND_PID)"
            break
        fi
        if [ $i -eq 60 ]; then
            print_error "Frontend failed to start within 60 seconds"
            print_error "Check logs: tail -f $LOGS_DIR/frontend.log"
            return 1
        fi
        sleep 1
        echo -n "."
    done
    echo ""
}

run_system_tests() {
    print_info "Running system health checks..."
    
    # Test backend health
    if curl -s http://localhost:8000/api/v2/health | grep -q '"status":"healthy"'; then
        print_success "Backend health check: PASSED"
    else
        print_warning "Backend health check: FAILED"
    fi
    
    # Test frontend connectivity
    if curl -s http://localhost:3000 &> /dev/null; then
        print_success "Frontend connectivity: PASSED"
    else
        print_warning "Frontend connectivity: FAILED"
    fi
}

show_status() {
    echo ""
    echo -e "${GREEN}🎉 Deployment Complete!${NC}\n"
    
    echo -e "${BLUE}📊 System Status${NC}"
    echo -e "${GREEN}✅ Backend:${NC}  http://localhost:8000"
    echo -e "${GREEN}✅   └── API Documentation:${NC} http://localhost:8000/docs"
    echo -e "${GREEN}✅   └── Health Check:${NC} http://localhost:8000/api/v2/health"
    echo -e "${GREEN}✅ Frontend:${NC} http://localhost:3000"
    echo ""
    
    echo -e "${BLUE}🛠️  Management Commands${NC}"
    echo -e "${GREEN}• View backend logs:${NC}  tail -f $LOGS_DIR/backend.log"
    echo -e "${GREEN}• View frontend logs:${NC} tail -f $LOGS_DIR/frontend.log"
    echo -e "${GREEN}• Stop all services:${NC}  ./stop.sh"
    echo ""
    
    echo -e "${BLUE}🚀 Quick Start${NC}"
    echo "1. Open http://localhost:3000 in your browser"
    echo "2. Upload CSV files with your data (samples available in sample_data/)"
    echo "3. Start analyzing with AI-powered insights"
    echo ""
}

show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --test       Run deployment with system tests"
    echo "  --status     Show current system status"
    echo "  --logs       Show live logs"
    echo "  --help       Show this help message"
    echo ""
}

show_logs() {
    echo -e "${BLUE}📋 Live Logs (Press Ctrl+C to exit)${NC}\n"
    
    if [[ -f "$LOGS_DIR/backend.log" ]] && [[ -f "$LOGS_DIR/frontend.log" ]]; then
        tail -f "$LOGS_DIR/backend.log" "$LOGS_DIR/frontend.log"
    else
        print_warning "Log files not found. Services may not be running."
    fi
}

main() {
    local run_tests=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --test) run_tests=true; shift ;;
            --status) show_status; exit 0 ;;
            --logs) show_logs; exit 0 ;;
            --help) show_usage; exit 0 ;;
            *) echo "Unknown option: $1"; show_usage; exit 1 ;;
        esac
    done
    
    # Main deployment sequence
    print_header
    check_requirements
    setup_backend
    setup_frontend
    stop_existing_services
    
    if start_backend && start_frontend; then
        if [[ "$run_tests" == true ]]; then
            run_system_tests
        fi
        show_status
    else
        print_error "Deployment failed. Check logs for details:"
        echo "  Backend: $LOGS_DIR/backend.log"
        echo "  Frontend: $LOGS_DIR/frontend.log"
        exit 1
    fi
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${YELLOW}Deployment interrupted by user${NC}"; exit 130' INT

# Run main function with all arguments
main "$@"