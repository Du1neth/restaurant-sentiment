#!/usr/bin/env python3
"""
Startup script for SentimentEats web application
"""

import os
from pathlib import Path

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ["TAVILY_API_KEY", "GEMINI_API_KEY"]
    env_file = Path(".env")
    
    if not env_file.exists():
        print("⚠️  .env file not found!")
        print("📝 Please copy .env.example to .env and add your API keys:")
        print("   cp .env.example .env")
        print("   # Edit .env file with your API keys")
        print("\n🔑 Get your API keys from:")
        print("   - Tavily: https://tavily.com/")
        print("   - Gemini: https://ai.google.dev/")
        return False
    
    # Load environment variables
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var) == f"your_{var.lower()}_here":
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing or invalid API keys in .env file:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Please update your .env file with valid API keys")
        return False
    
    return True

def main():
    """Start the SentimentEats application"""
    print("🍽️  SentimentEats - Restaurant Sentiment Analysis Platform")
    print("=" * 60)
    
    if not check_environment():
        print("\n❌ Environment setup incomplete. Please fix the issues above.")
        return
    
    print("✅ Environment setup complete!")
    print("🚀 Starting web application...")
    print("📱 Visit: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 60)
    
    # Import and run the Flask app
    from app import app, db
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("✅ Database initialized")
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()