import os
import json
import hashlib
from typing import Dict, List, Any
from groq import Groq
from prompts import get_analysis_prompt
import streamlit as st

class ContentAnalyzer:
    """Core analysis engine using Groq AI for cancellation risk assessment"""
    
    def __init__(self):
        """Initialize the analyzer with Groq client"""
        try:
            # Try to get API key from Streamlit secrets first (local development)
            try:
                api_key = st.secrets.get("GROQ_API_KEY")
            except:
                api_key = None
            
            # Fallback to environment variable (production deployment)
            if not api_key:
                api_key = os.getenv("GROQ_API_KEY")
            
            if not api_key:
                raise ValueError("Groq API key not found. Please set GROQ_API_KEY in secrets.toml or environment variables.")
            
            self.client = Groq(api_key=api_key)
            self.model = "llama-3.1-70b-versatile"  # Primary model for comprehensive analysis
            self.fallback_model = "llama-3.1-8b-instant"  # Fallback for faster responses
            
            # Risk categories with weights (as specified in requirements)
            self.risk_categories = {
                "Identity & Discrimination": 25,
                "Political Sensitivity": 20,
                "Social Issues": 20,
                "Professional Appropriateness": 15,
                "Platform Violations": 10,
                "Timing & Context": 10
            }
            
            # Cache for storing recent analyses
            self.cache = {}
            
        except Exception as e:
            st.error(f"Failed to initialize Groq client: {str(e)}")
            raise
    
    def test_connection(self) -> bool:
        """Test the Groq API connection"""
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": "Test"}],
                model=self.fallback_model,
                max_tokens=10
            )
            return True
        except Exception:
            return False
    
    def _get_cache_key(self, content: str, settings: Dict) -> str:
        """Generate a cache key for the analysis"""
        cache_string = f"{content}_{json.dumps(settings, sort_keys=True)}"
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _preprocess_content(self, content: str) -> str:
        """Clean and preprocess content for analysis"""
        # Limit to first 4000 characters for cost efficiency
        content = content[:4000]
        
        # Clean up text
        content = content.strip()
        content = content.replace('\n', ' ')
        content = ' '.join(content.split())  # Remove extra whitespace
        
        return content
    
    def _parse_groq_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Groq response and extract structured data"""
        try:
            # Try to parse as JSON first
            if response_text.strip().startswith('{'):
                return json.loads(response_text)
            
            # If not JSON, try to extract information from text response
            # This is a fallback for when the model doesn't return perfect JSON
            lines = response_text.strip().split('\n')
            
            result = {
                'risk_percentage': 0,
                'risk_level': 'Low',
                'categories': {},
                'risk_factors': [],
                'recommendations': [],
                'explanation': response_text
            }
            
            # Try to extract risk percentage
            for line in lines:
                if 'risk' in line.lower() and '%' in line:
                    try:
                        # Extract number before %
                        import re
                        numbers = re.findall(r'\d+', line)
                        if numbers:
                            result['risk_percentage'] = min(int(numbers[0]), 100)
                            break
                    except:
                        pass
            
            return result
            
        except json.JSONDecodeError:
            # If JSON parsing fails, return a basic structure
            return {
                'risk_percentage': 50,  # Default to medium risk if parsing fails
                'risk_level': 'Medium',
                'categories': {cat: 0 for cat in self.risk_categories.keys()},
                'risk_factors': ['Unable to parse detailed analysis'],
                'recommendations': ['Please review the content manually'],
                'explanation': response_text
            }
    
    def analyze_text(self, content: str, settings: Dict[str, Any], visual_context: str = None) -> Dict[str, Any]:
        """
        Analyze text content for cancellation risk
        
        Args:
            content: Text content to analyze
            settings: Analysis settings (platform, author_type, etc.)
            visual_context: Optional visual content context for enhanced analysis
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Preprocess content
            processed_content = self._preprocess_content(content)
            
            if not processed_content:
                return {
                    'risk_percentage': 0,
                    'risk_level': 'Low',
                    'categories': {cat: 0 for cat in self.risk_categories.keys()},
                    'risk_factors': [],
                    'recommendations': ['Content is empty or too short to analyze'],
                    'explanation': 'No meaningful content to analyze.'
                }
            
            # Check cache first
            cache_key = self._get_cache_key(processed_content, settings)
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # Get analysis prompt
            prompt = get_analysis_prompt(processed_content, settings, self.risk_categories, visual_context)
            
            # Make API call with retry logic
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    # Use primary model first, fallback to faster model on retry
                    model = self.model if attempt == 0 else self.fallback_model
                    
                    response = self.client.chat.completions.create(
                        messages=[
                            {
                                "role": "system",
                                "content": "You are an expert content analyst specializing in social media risk assessment. Always respond with valid JSON."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        model=model,
                        max_tokens=1500,
                        temperature=0.3,
                        response_format={"type": "json_object"}
                    )
                    
                    response_text = response.choices[0].message.content
                    result = self._parse_groq_response(response_text)
                    
                    # Validate and normalize results
                    result = self._validate_results(result)
                    
                    # Cache the result
                    self.cache[cache_key] = result
                    
                    return result
                    
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    continue
            
        except Exception as e:
            # Return error result
            return {
                'risk_percentage': 50,
                'risk_level': 'Medium',
                'categories': {cat: 0 for cat in self.risk_categories.keys()},
                'risk_factors': [f'Analysis failed: {str(e)}'],
                'recommendations': ['Please try again or review content manually'],
                'explanation': f'Unable to complete analysis due to: {str(e)}'
            }
    
    def _validate_results(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize analysis results"""
        # Ensure risk_percentage is within bounds
        if 'risk_percentage' not in result:
            result['risk_percentage'] = 0
        else:
            result['risk_percentage'] = max(0, min(100, int(result['risk_percentage'])))
        
        # Set risk level based on percentage
        risk_pct = result['risk_percentage']
        if risk_pct >= 70:
            result['risk_level'] = 'High'
        elif risk_pct >= 40:
            result['risk_level'] = 'Medium'
        else:
            result['risk_level'] = 'Low'
        
        # Ensure categories exist and are normalized
        if 'categories' not in result:
            result['categories'] = {}
        
        for category in self.risk_categories.keys():
            if category not in result['categories']:
                result['categories'][category] = 0
            else:
                result['categories'][category] = max(0, min(100, int(result['categories'][category])))
        
        # Ensure risk_factors is a list
        if 'risk_factors' not in result:
            result['risk_factors'] = []
        elif not isinstance(result['risk_factors'], list):
            result['risk_factors'] = [str(result['risk_factors'])]
        
        # Ensure recommendations is a list
        if 'recommendations' not in result:
            result['recommendations'] = []
        elif not isinstance(result['recommendations'], list):
            result['recommendations'] = [str(result['recommendations'])]
        
        # Ensure explanation exists
        if 'explanation' not in result:
            result['explanation'] = "Analysis completed successfully."
        
        return result
    
    def batch_analyze(self, content_list: List[str], settings: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze multiple pieces of content"""
        results = []
        for content in content_list:
            result = self.analyze_text(content, settings)
            results.append(result)
        return results
    
    def get_analysis_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get summary statistics for batch analysis"""
        if not results:
            return {}
        
        total_risk = sum(r['risk_percentage'] for r in results) / len(results)
        high_risk_count = sum(1 for r in results if r['risk_percentage'] >= 70)
        medium_risk_count = sum(1 for r in results if 40 <= r['risk_percentage'] < 70)
        low_risk_count = len(results) - high_risk_count - medium_risk_count
        
        return {
            'total_items': len(results),
            'average_risk': round(total_risk, 1),
            'high_risk_count': high_risk_count,
            'medium_risk_count': medium_risk_count,
            'low_risk_count': low_risk_count,
            'high_risk_percentage': round((high_risk_count / len(results)) * 100, 1)
        }
