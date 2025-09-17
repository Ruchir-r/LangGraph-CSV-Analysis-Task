#!/bin/bash

# Version 1 Quick Setup Script
# Historical Multi-Table Data Analysis with Conversational Interface

echo "🚀 Setting up Historical Data Analysis System - Version 1"
echo "================================================="

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p uploads
mkdir -p db

# Backend setup
echo "🔧 Setting up backend environment..."
cd backend

echo "📦 Installing Python dependencies..."
if command -v python3 &> /dev/null; then
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "❌ Python 3 not found. Please install Python 3.11+ first."
    exit 1
fi

echo "🗄️ Initializing database..."
python app/database.py

cd ..

# Frontend setup (optional for Version 1)
echo "🎨 Setting up frontend (optional)..."
if command -v node &> /dev/null && command -v npm &> /dev/null; then
    cd frontend
    echo "📦 Installing Node.js dependencies..."
    npm install
    cd ..
else
    echo "⚠️ Node.js/npm not found. Frontend setup skipped."
    echo "   You can install Node.js later to use the web interface."
fi

# Environment configuration
echo "⚙️ Setting up environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Environment file created (.env)"
    echo "   You can modify it if needed."
fi

echo ""
echo "🎉 Setup completed! Version 1 is ready to use."
echo ""
echo "🚀 Quick Start Commands:"
echo "======================="
echo ""
echo "1. Start the backend API:"
echo "   cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo ""
echo "2. (Optional) Start the frontend:"
echo "   cd frontend && npm start"
echo ""
echo "3. Test the API:"
echo "   curl http://localhost:8000/"
echo ""
echo "4. View API documentation:"
echo "   http://localhost:8000/docs"
echo ""
echo "📊 Sample data files are available in the sample_data/ directory"
echo "💬 Try uploading a CSV and asking questions like:"
echo "   - 'What is the average revenue?'"
echo "   - 'Show me total sales by region'"
echo "   - 'Help me analyze my data'"
echo ""
echo "📚 Read the README.md for detailed documentation"
echo "🔧 Version 2 and 3 will add LLM integration and advanced features!"
