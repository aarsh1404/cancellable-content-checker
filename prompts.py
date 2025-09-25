"""
AI prompts and templates for content analysis
"""

def get_analysis_prompt(content: str, settings: dict, risk_categories: dict, visual_context: str = None) -> str:
    """
    Generate the analysis prompt for Groq AI
    
    Args:
        content: Text content to analyze
        settings: Analysis settings (platform, author_type, etc.)
        risk_categories: Dictionary of risk categories with weights
        visual_context: Optional visual content context (images, metadata, etc.)
        
    Returns:
        Formatted prompt string
    """
    
    platform = settings.get('platform', 'General')
    author_type = settings.get('author_type', 'Individual')
    audience_size = settings.get('audience_size', '< 1K followers')
    sensitivity = settings.get('sensitivity', 5)
    
    # Prepare visual context section
    visual_context_section = f"VISUAL CONTEXT:\n{visual_context}\n" if visual_context else ""
    
    prompt = f"""
You are an expert content analyst specializing in social media risk assessment. Analyze the following content for potential "cancellation" risk and provide a comprehensive assessment.

CONTENT TO ANALYZE:
"{content}"

{visual_context_section if visual_context else ""}
ANALYSIS CONTEXT:
- Target Platform: {platform}
- Author Type: {author_type}
- Audience Size: {audience_size}
- Analysis Sensitivity: {sensitivity}/10

RISK ASSESSMENT FRAMEWORK:
Analyze the content across these categories with the specified weights:

1. Identity & Discrimination (Weight: 25%)
   - Content targeting protected characteristics
   - Use of offensive language or slurs
   - Discriminatory statements or stereotypes
   - Exclusionary language

2. Political Sensitivity (Weight: 20%)
   - Extreme political positions
   - Conspiracy theories or misinformation
   - Election-related false claims
   - Polarizing political rhetoric

3. Social Issues (Weight: 20%)
   - Controversial takes on current events
   - Dismissing social movements
   - Insensitive commentary on sensitive topics
   - Tone-deaf responses to crises

4. Professional Appropriateness (Weight: 15%)
   - Workplace conduct violations
   - Industry ethics concerns
   - Employer conflicts
   - Unprofessional behavior

5. Platform Violations (Weight: 10%)
   - Harassment or bullying
   - Doxxing or privacy violations
   - Terms of service violations
   - Spam or manipulative behavior

6. Timing & Context (Weight: 10%)
   - Insensitive timing of posts
   - Trending topic risks
   - Anniversary date considerations
   - Current event sensitivity

INSTRUCTIONS:
1. Rate each category from 0-100 based on risk level
2. Calculate overall risk percentage (0-100)
3. Identify specific risk factors
4. Provide actionable recommendations
5. Consider the author type and platform context
6. If visual context is provided, consider images, metadata, and visual elements in your analysis
7. Be thorough but concise

RESPONSE FORMAT:
Respond ONLY with valid JSON in this exact format:
{{
    "risk_percentage": <0-100>,
    "risk_level": "<Low/Medium/High>",
    "categories": {{
        "Identity & Discrimination": <0-100>,
        "Political Sensitivity": <0-100>,
        "Social Issues": <0-100>,
        "Professional Appropriateness": <0-100>,
        "Platform Violations": <0-100>,
        "Timing & Context": <0-100>
    }},
    "risk_factors": [
        "<specific risk factor 1>",
        "<specific risk factor 2>",
        "<additional factors>"
    ],
    "recommendations": [
        "<actionable recommendation 1>",
        "<actionable recommendation 2>",
        "<additional recommendations>"
    ],
    "explanation": "<detailed explanation of the analysis and reasoning>"
}}

RISK LEVEL GUIDELINES:
- Low Risk (0-39%): Minimal concern, generally safe to post
- Medium Risk (40-69%): Potential controversy, suggest revisions
- High Risk (70-100%): Immediate backlash likely, recommend not posting

IMPORTANT NOTES:
- Consider the sensitivity setting: higher values = more conservative analysis
- Account for platform-specific norms and community standards
- Factor in author type and audience reach
- Be objective and evidence-based in your assessment
- Focus on actionable insights, not just criticism
"""
    
    return prompt

def get_quick_analysis_prompt(content: str, settings: dict) -> str:
    """
    Generate a simplified prompt for quick analysis using the faster model
    """
    platform = settings.get('platform', 'General')
    author_type = settings.get('author_type', 'Individual')
    
    prompt = f"""
Quickly analyze this content for cancellation risk on {platform} for a {author_type}:

"{content[:1000]}"

Respond with JSON:
{{
    "risk_percentage": <0-100>,
    "risk_level": "<Low/Medium/High>",
    "main_concerns": ["<concern1>", "<concern2>"],
    "recommendation": "<brief recommendation>"
}}
"""
    
    return prompt

def get_batch_analysis_prompt(content_list: list, settings: dict) -> str:
    """
    Generate prompt for batch analysis of multiple content pieces
    """
    platform = settings.get('platform', 'General')
    author_type = settings.get('author_type', 'Individual')
    
    content_items = "\n".join([f"{i+1}. {content[:200]}..." for i, content in enumerate(content_list)])
    
    prompt = f"""
Analyze these {len(content_list)} content pieces for cancellation risk on {platform} for a {author_type}:

{content_items}

Respond with JSON array:
[
    {{
        "item": 1,
        "risk_percentage": <0-100>,
        "risk_level": "<Low/Medium/High>",
        "main_concern": "<primary concern>"
    }},
    ...
]
"""
    
    return prompt

def get_platform_specific_guidelines(platform: str) -> str:
    """
    Get platform-specific analysis guidelines
    """
    guidelines = {
        "Twitter": """
        Twitter Guidelines:
        - Character limit creates compression issues
        - Retweets amplify controversy quickly
        - Thread context matters
        - Hashtag risks and trending topics
        - Real-time nature increases sensitivity
        """,
        
        "LinkedIn": """
        LinkedIn Guidelines:
        - Professional network expectations
        - Career impact considerations
        - Industry-specific sensitivities
        - Professional image maintenance
        - B2B audience context
        """,
        
        "Instagram": """
        Instagram Guidelines:
        - Visual content context matters
        - Stories vs. posts vs. reels differences
        - Influencer culture considerations
        - Visual storytelling risks
        - Engagement patterns impact
        """,
        
        "Facebook": """
        Facebook Guidelines:
        - Mixed personal/professional networks
        - Algorithm amplification risks
        - Older demographic considerations
        - Community group dynamics
        - Privacy settings impact
        """,
        
        "YouTube": """
        YouTube Guidelines:
        - Long-form content analysis
        - Monetization implications
        - Creator community standards
        - Comment section risks
        - Algorithm recommendation impact
        """,
        
        "TikTok": """
        TikTok Guidelines:
        - Gen Z audience sensitivity
        - Viral potential amplification
        - Short-form content compression
        - Trend participation risks
        - Music and sound context
        """
    }
    
    return guidelines.get(platform, """
    General Guidelines:
    - Consider platform norms and community standards
    - Factor in audience demographics and expectations
    - Account for content format and constraints
    - Consider viral potential and reach
    """)

def get_author_type_context(author_type: str) -> str:
    """
    Get author type specific context for analysis
    """
    contexts = {
        "Individual": """
        Individual Context:
        - Personal brand impact
        - Friend/family network considerations
        - Limited reach but personal reputation risk
        """,
        
        "Public Figure": """
        Public Figure Context:
        - High visibility and scrutiny
        - Media amplification risk
        - Fan base expectations
        - Career and endorsement impact
        """,
        
        "Corporate": """
        Corporate Context:
        - Brand reputation impact
        - Stakeholder considerations
        - Regulatory compliance
        - Market reaction risks
        """,
        
        "Influencer": """
        Influencer Context:
        - Brand partnership risks
        - Audience trust maintenance
        - Platform algorithm impact
        - Monetization concerns
        """,
        
        "Journalist": """
        Journalist Context:
        - Credibility and objectivity
        - Editorial standards
        - Source relationship risks
        - Professional ethics
        """,
        
        "Politician": """
        Politician Context:
        - Public record implications
        - Opposition research risks
        - Constituent expectations
        - Electoral impact
        """
    }
    
    return contexts.get(author_type, """
    General Author Context:
    - Consider professional standing and reputation
    - Factor in audience expectations and trust
    - Account for potential career or business impact
    """)
