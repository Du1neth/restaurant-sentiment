#!/usr/bin/env python3

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from web_scraper import RestaurantReviewScraper
from gemini_analyzer import GeminiAnalyzer

def load_env_file():
    """Load environment variables from .env file if it exists"""
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

def validate_environment():
    """Validate required environment variables"""
    required_vars = ["TAVILY_API_KEY", "GEMINI_API_KEY"]
    missing = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\n💡 Please set these in your .env file or as environment variables")
        print("   Check .env.example for reference")
        sys.exit(1)

def main():
    """Main function to run restaurant sentiment analysis"""
    
    # Load environment variables
    load_env_file()
    validate_environment()
    
    print("🍽️  Restaurant Sentiment Analysis Tool")
    print("=" * 50)
    
    # Get restaurant name from user or use test data
    try:
        restaurant_name = input("Enter restaurant name: ").strip()
        if not restaurant_name:
            print("❌ Restaurant name is required")
            sys.exit(1)
        
        # Get optional location
        location = input("Enter location (optional): ").strip()
        
        # Get max reviews (optional)
        max_reviews_input = input("Max reviews to analyze (default: 30): ").strip()
        try:
            max_reviews = int(max_reviews_input) if max_reviews_input else 30
            max_reviews = min(max_reviews, 100)  # Cap at 100
        except ValueError:
            max_reviews = 30
    except EOFError:
        print("❌ No input provided")
        sys.exit(1)
    
    print(f"\n🔍 Analyzing '{restaurant_name}' {location}...")
    print(f"📊 Target: {max_reviews} reviews")
    print("-" * 50)
    
    try:
        # Step 1: Extract content from web
        print("\n1️⃣ Extracting content from the web...")
        scraper = RestaurantReviewScraper()
        extracted_content = scraper.scrape_restaurant_reviews(
            restaurant_name=restaurant_name,
            location=location,
            target_extractions=5
        )
        
        if not extracted_content:
            print("❌ No content could be extracted. Please check the restaurant name and try again.")
            sys.exit(1)
        
        print(f"✅ Successfully extracted from {len(extracted_content)} sources")
        
        # Step 2: Analyze with Gemini
        print("\n2️⃣ Analyzing content with AI...")
        analyzer = GeminiAnalyzer()
        analysis = analyzer.analyze_restaurant_content(restaurant_name, extracted_content)
        
        # Step 3: Save results
        print("\n3️⃣ Saving results...")
        
        # Create output directory
        output_dir = Path("reports")
        output_dir.mkdir(exist_ok=True)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        restaurant_slug = restaurant_name.lower().replace(" ", "_").replace("/", "_")
        
        # Save JSON report
        json_file = output_dir / f"{restaurant_slug}_{timestamp}.json"
        report_data = {
            "restaurant_name": restaurant_name,
            "analysis_date": timestamp,
            "sources_analyzed": len(extracted_content),
            "analysis": analysis.model_dump()
        }
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print("\n" + "=" * 50)
        print("📈 ANALYSIS COMPLETE")
        print("=" * 50)
        print(f"Restaurant: {restaurant_name}")
        print(f"Sources Analyzed: {len(extracted_content)}")
        print(f"Overall Rating: {analysis.overall_rating:.1f}/5.0")
        print(f"Overall Sentiment: {analysis.overall_sentiment}")
        
        print("\n🎯 TOP STRENGTHS:")
        for i, strength in enumerate(analysis.strengths[:3], 1):
            print(f"  {i}. {strength}")
        
        print("\n⚠️  TOP WEAKNESSES:")
        for i, weakness in enumerate(analysis.weaknesses[:3], 1):
            print(f"  {i}. {weakness}")
        
        print("\n💡 KEY ACTIONABLE INSIGHTS:")
        for i, insight in enumerate(analysis.actionable_insights[:5], 1):
            print(f"  {i}. {insight}")
        
        print(f"\n📄 Report saved:")
        print(f"  📊 JSON: {json_file}")
        
        print("\n✨ Analysis complete!")
        
    except KeyboardInterrupt:
        print("\n\n❌ Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        print("Please check your API keys and internet connection")
        sys.exit(1)

if __name__ == "__main__":
    main()