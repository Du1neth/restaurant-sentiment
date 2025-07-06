import os
from typing import List, Dict, Any
from google import genai
from pydantic import BaseModel

class ReviewAnalysis(BaseModel):
    individual_reviews: List[str]
    overall_sentiment: str
    overall_rating: float
    strengths: List[str]
    weaknesses: List[str]
    actionable_insights: List[str]
    summary: str

class GeminiAnalyzer:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    def analyze_restaurant_content(self, restaurant_name: str, extracted_content: List[Dict[str, Any]]) -> ReviewAnalysis:
        """Analyze raw extracted content and generate comprehensive insights"""
        
        print(f"🤖 Analyzing content for '{restaurant_name}' using Gemini...")
        
        # Combine all extracted content
        all_content = ""
        sources = []
        
        for extraction in extracted_content:
            content = extraction.get('content', '')
            url = extraction.get('url', '')
            title = extraction.get('title', '')
            
            all_content += f"\n--- Source: {title} ({url}) ---\n{content}\n"
            sources.append(url)
        
        print(f"📄 Total content length: {len(all_content)} characters")
        print(f"📝 Sources: {len(sources)} websites")
        
        # Create comprehensive analysis prompt
        prompt = f"""
        You are an expert restaurant business analyst. Analyze all content below for "{restaurant_name}" and extract maximum insights.
        
        EXTRACTED CONTENT FROM {len(sources)} SOURCES:
        {all_content}
        
        ANALYSIS REQUIREMENTS:
        
        1. EXTRACT INDIVIDUAL REVIEWS: Find and list actual customer reviews/comments (ignore ads, navigation, menus)
        
        2. OVERALL SENTIMENT: Determine if customers are generally satisfied, dissatisfied, or mixed
        
        3. OVERALL RATING: Based on all feedback, give a 1-5 rating (1=terrible, 5=excellent)
        
        4. STRENGTHS: What customers consistently praise (food quality, service, atmosphere, value, etc.)
        
        5. WEAKNESSES: What customers consistently complain about or suggest improvement for
        
        6. ACTIONABLE INSIGHTS: Specific, implementable recommendations for the restaurant owner:
           - Staff training needs
           - Menu improvements  
           - Service process changes
           - Facility upgrades
           - Marketing opportunities
           - Cost optimization
           - Customer experience enhancements
        
        7. SUMMARY: Comprehensive overview of the restaurant's performance and key takeaways
        
        IMPORTANT:
        - Be ruthlessly thorough in extracting insights from ALL the content
        - Focus on patterns and recurring themes in customer feedback
        - Provide specific, actionable business advice
        - If content is sparse, state that clearly but still provide analysis
        - Ignore technical website content, focus only on customer opinions
        """
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": ReviewAnalysis,
                }
            )
            
            if response and hasattr(response, 'parsed') and response.parsed:
                return response.parsed
            else:
                print("⚠️  Gemini returned empty response, using fallback analysis")
                raise ValueError("Empty response from Gemini")
            
        except Exception as e:
            print(f"❌ Error analyzing content: {e}")
            
            # Return fallback analysis
            return ReviewAnalysis(
                individual_reviews=["Analysis failed - unable to process content"],
                overall_sentiment="NEUTRAL",
                overall_rating=3.0,
                strengths=["Unable to determine strengths"],
                weaknesses=["Analysis incomplete"],
                actionable_insights=["Re-run analysis with valid API credentials"],
                summary=f"Analysis of {restaurant_name} could not be completed due to technical issues."
            )