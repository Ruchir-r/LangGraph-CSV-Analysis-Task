#!/bin/bash
# Historical Multi-Table Data Analysis V2 - Stop Script
# This script stops both the backend and frontend services

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_success() {
    echo -e "${CYAN}✅ $1${NC}"
}

print_header() {
    echo -e "${YELLOW}$1${NC}"
}

# Function to kill processes on specific ports
kill_port() {
    local port=$1
    local pids=$(lsof -t -i :$port 2>/dev/null)
    if [ -n "$pids" ]; then
        print_status "Stopping processes on port $port"
        echo "$pids" | xargs kill -9 2>/dev/null || true
        sleep 1
        return 0
    else
        return 1
    fi
}

print_header "🛑 Stopping Historical Multi-Table Data Analysis V2 Services"
echo ""

# Stop backend (port 8000)
if kill_port 8000; then
    print_success "Backend stopped (port 8000)"
else
    print_warning "No backend process found on port 8000"
fi

# Stop frontend (port 3000) 
if kill_port 3000; then
    print_success "Frontend stopped (port 3000)"
else
    print_warning "No frontend process found on port 3000"
fi

# Stop any remaining uvicorn or npm processes
print_status "Cleaning up remaining processes..."

# Kill uvicorn processes
pkill -f "uvicorn.*app.main:app" 2>/dev/null && print_success "Uvicorn processes stopped" || true

# Kill npm start processes
pkill -f "npm.*start" 2>/dev/null && print_success "npm processes stopped" || true

echo ""
print_success "All V2 services have been stopped"
print_status "You can restart them with: ./start_v2.sh"