import os
from typing import List, Dict, Any
from tavily import TavilyClient
from google import genai

class RestaurantReviewScraper:
    def __init__(self):
        self.client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        self.gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    def generate_search_queries(self, restaurant_name: str, location: str = "") -> List[str]:
        """Use Gemini to generate optimal search queries"""
        
        prompt = f"""
        Generate 5 highly effective web search queries to find customer reviews and feedback for "{restaurant_name}" in "{location}".
        
        The queries should:
        - Be optimized for finding review sites, social media posts, and customer feedback
        - Include variations that would catch different types of review platforms
        - Be specific enough to find relevant content but broad enough to not miss sources
        - Include local/regional search terms if applicable
        
        Restaurant: {restaurant_name}
        Location: {location}
        
        Return only the search queries, one per line, no numbering or extra text.
        """
        
        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            if response and hasattr(response, 'text'):
                queries = [q.strip() for q in response.text.strip().split('\n') if q.strip()]
                print(f"🤖 Generated {len(queries)} optimized search queries")
                return queries[:5]  # Limit to 5 queries
                
        except Exception as e:
            print(f"⚠️  Failed to generate optimized queries: {e}")
        
        # Fallback queries
        fallback_queries = [
            f"{restaurant_name} reviews {location}".strip(),
            f"{restaurant_name} customer feedback {location}".strip(),
            f"{restaurant_name} restaurant rating {location}".strip(),
            f"{restaurant_name} dining experience {location}".strip(),
            f"{restaurant_name} food review {location}".strip()
        ]
        print(f"🔄 Using fallback search queries")
        return fallback_queries
    
    def validate_content_relevance(self, content: str, restaurant_name: str, location: str) -> bool:
        """Use LLM to validate if extracted content is relevant to the target restaurant"""
        
        # Take a sample of the content to avoid token limits
        content_sample = content[:3000] if len(content) > 3000 else content
        
        validation_prompt = f"""
        VALIDATION TASK: Is this content about "{restaurant_name}" in "{location}"?

        TARGET RESTAURANT: "{restaurant_name}"
        TARGET LOCATION: "{location}"
        
        CONTENT TO VALIDATE:
        {content_sample}
        
        VALIDATION RULES:
        1. The content should mention "{restaurant_name}" or very similar variations
        2. Closely related business names are acceptable (e.g., "Ravon Bakers" could be related to "Revon Restaurant")
        3. The content must be about THIS restaurant or closely related businesses, not completely different ones
        4. Generic content about food/restaurants without any mention of the target = NOT RELEVANT
        5. Content about clearly different restaurants in different areas = NOT RELEVANT
        
        RESPOND WITH ONLY ONE WORD:
        "RELEVANT" - if this content is about "{restaurant_name}" or closely related business
        "NOT_RELEVANT" - if this is about a completely different restaurant or unrelated content
        
        When in doubt and the content seems related, lean towards "RELEVANT".
        """
        
        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-pro",
                contents=validation_prompt
            )
            
            if response and hasattr(response, 'text'):
                result = response.text.strip().upper()
                is_relevant = "RELEVANT" in result and "NOT_RELEVANT" not in result
                return is_relevant
            else:
                print("   ⚠️  Validation failed - rejecting content")
                return False  # Default to NOT relevant if validation fails
                
        except Exception as e:
            print(f"   ⚠️  Validation error: {e} - rejecting content")
            return False  # Default to NOT relevant if validation fails
    
    def scrape_restaurant_reviews(self, restaurant_name: str, location: str = "", target_extractions: int = 5) -> List[Dict[str, Any]]:
        """Search and extract until we get target_extractions successful extractions"""
        
        print(f"🔍 Searching for '{restaurant_name}' {location}...")
        
        # Generate optimized search queries
        search_queries = self.generate_search_queries(restaurant_name, location)
        
        successful_extractions = []
        search_attempts = 0
        max_search_attempts = 5  # Increased to 5 attempts
        
        while len(successful_extractions) < target_extractions and search_attempts < max_search_attempts:
            search_attempts += 1
            
            # Use the generated queries cyclically
            query = search_queries[(search_attempts - 1) % len(search_queries)]
            
            print(f"📡 Search attempt {search_attempts}/5: '{query}'")
            
            try:
                # Search with raw content
                response = self.client.search(
                    query=query,
                    num_results=15,  # Increased to get more results
                    include_raw_content=True,
                    search_depth="advanced"  # Use advanced search depth
                )
                
                results = response.get("results", [])
                print(f"Found {len(results)} search results")
                
                # Process each result
                for i, result in enumerate(results):
                    if len(successful_extractions) >= target_extractions:
                        break
                    
                    url = result.get('url', '')
                    raw_content = result.get('raw_content', '')
                    
                    print(f"📄 Processing result {i+1}: {url}")
                    
                    # Try raw content first
                    content = raw_content
                    
                    # If no raw content, try extract API
                    if not content or len(content) < 200:
                        try:
                            print("   🔄 Trying extract API...")
                            extract_result = self.client.extract(url)
                            
                            if isinstance(extract_result, dict):
                                content = extract_result.get("raw_content", "")
                            elif hasattr(extract_result, 'results') and extract_result.results:
                                content = extract_result.results[0].get("raw_content", "")
                            else:
                                content = ""
                                
                        except Exception as e:
                            print(f"   ❌ Extract failed: {e}")
                            continue
                    
                    # Check if we got meaningful content
                    if content and len(content) > 500:
                        print(f"   📄 Extracted {len(content)} characters - validating relevance...")
                        
                        # Validate if content is relevant to the restaurant
                        if self.validate_content_relevance(content, restaurant_name, location):
                            print(f"   ✅ Content validated as relevant to {restaurant_name}")
                            successful_extractions.append({
                                'url': url,
                                'content': content,
                                'title': result.get('title', ''),
                                'search_query': query,
                                'snippet': result.get('content', '')[:200] + "..."
                            })
                            print(f"   📊 Total successful extractions: {len(successful_extractions)}")
                        else:
                            print(f"   ❌ Content not relevant to {restaurant_name} - skipping")
                    else:
                        print(f"   ⏭️  Insufficient content ({len(content) if content else 0} chars)")
                
            except Exception as e:
                print(f"❌ Search attempt {search_attempts} failed: {e}")
                continue
            
            print(f"   🎯 Progress: {len(successful_extractions)}/{target_extractions} extractions completed\n")
        
        print(f"🎯 Final result: {len(successful_extractions)} successful extractions from {search_attempts} search attempts")
        
        if not successful_extractions:
            print("❌ No content could be extracted")
            return []
        
        # Return the extractions for Gemini to process
        return successful_extractions