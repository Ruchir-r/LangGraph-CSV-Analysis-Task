#!/usr/bin/env python3
"""
Database table creation script
Ensures all required tables exist including the new comprehensive_analysis table
"""

import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.database import create_tables

if __name__ == "__main__":
    print("🔧 Creating database tables...")
    try:
        create_tables()
        print("✅ Database tables created successfully!")
        print("📊 Tables include:")
        print("   - files (file uploads)")
        print("   - sessions (chat sessions)")
        print("   - messages (chat history)")
        print("   - analysis_results (basic analytics)")
        print("   - comprehensive_analysis (LangGraph workflow results)")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        sys.exit(1)