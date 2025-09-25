import streamlit as st
import json
import time
from datetime import datetime
from analyzer import ContentAnalyzer
from extractors import ContentExtractor
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(
    page_title="Cancellable Content Checker",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .risk-meter {
        background: linear-gradient(90deg, #28a745 0%, #ffc107 50%, #dc3545 100%);
        height: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .risk-high {
        color: #dc3545;
        font-weight: bold;
    }
    .risk-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .risk-low {
        color: #28a745;
        font-weight: bold;
    }
    .sidebar-section {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def display_risk_meter(risk_percentage):
    """Display a visual risk meter"""
    risk_color = "#dc3545" if risk_percentage >= 70 else "#ffc107" if risk_percentage >= 40 else "#28a745"
    
    st.markdown(f"""
    <div style="margin: 20px 0;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span><strong>Risk Level:</strong></span>
            <span style="color: {risk_color}; font-weight: bold; font-size: 1.2rem;">
                {risk_percentage}%
            </span>
        </div>
        <div class="risk-meter">
            <div style="width: {risk_percentage}%; height: 100%; background-color: {risk_color}; border-radius: 10px; transition: width 0.3s ease;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_risk_level(risk_percentage):
    """Display risk level classification"""
    if risk_percentage >= 70:
        return '<span class="risk-high">🔴 HIGH RISK</span>'
    elif risk_percentage >= 40:
        return '<span class="risk-medium">🟡 MEDIUM RISK</span>'
    else:
        return '<span class="risk-low">🟢 LOW RISK</span>'

def main():
    # Header
    st.markdown('<h1 class="main-header">🚨 Cancellable Content Checker</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem; color: #666;">
        Analyze your content for potential controversy before posting. Get instant feedback on cancellation risk.
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = ContentAnalyzer()
    if 'extractor' not in st.session_state:
        st.session_state.extractor = ContentExtractor()
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("### ⚙️ Analysis Settings")
        
        # Platform selection
        platform = st.selectbox(
            "Target Platform",
            ["Twitter", "LinkedIn", "Instagram", "Facebook", "YouTube", "TikTok", "General"],
            help="Select the platform where content will be posted"
        )
        
        # Author type
        author_type = st.selectbox(
            "Author Type",
            ["Individual", "Public Figure", "Corporate", "Influencer", "Journalist", "Politician"],
            help="Select your profile type for context-aware analysis"
        )
        
        # Audience size
        audience_size = st.selectbox(
            "Estimated Audience Reach",
            ["< 1K followers", "1K - 10K followers", "10K - 100K followers", "100K - 1M followers", "> 1M followers"],
            help="Select your approximate follower count"
        )
        
        # Analysis sensitivity
        sensitivity = st.slider(
            "Analysis Sensitivity",
            min_value=1,
            max_value=10,
            value=5,
            help="Higher values = more conservative analysis"
        )
        
        # API Status
        st.markdown("### 📊 API Status")
        try:
            st.session_state.analyzer.test_connection()
            st.success("✅ Groq API Connected")
        except Exception as e:
            st.error(f"❌ API Error: {str(e)}")
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["📝 Text Analysis", "📄 File Upload", "🔗 URL Analysis"])
    
    with tab1:
        st.markdown("### Direct Text Analysis")
        
        # Text input area
        content_text = st.text_area(
            "Enter your content here:",
            height=200,
            placeholder="Paste your text, tweet, post, or comment here for analysis..."
        )
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            analyze_text_btn = st.button("🚀 Analyze Content", type="primary", use_container_width=True)
        
        if analyze_text_btn and content_text.strip():
            with st.spinner("Analyzing content..."):
                try:
                    # Get analysis settings from sidebar
                    settings = {
                        'platform': platform,
                        'author_type': author_type,
                        'audience_size': audience_size,
                        'sensitivity': sensitivity
                    }
                    
                    # Analyze the content
                    result = st.session_state.analyzer.analyze_text(content_text, settings)
                    
                    # Display results
                    st.markdown("---")
                    st.markdown("### 📊 Analysis Results")
                    
                    # Risk meter
                    display_risk_meter(result['risk_percentage'])
                    
                    # Risk level
                    st.markdown(f"**Risk Classification:** {display_risk_level(result['risk_percentage'])}", unsafe_allow_html=True)
                    
                    # Category breakdown
                    st.markdown("### 📈 Risk Category Breakdown")
                    categories = result.get('categories', {})
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        for category, score in list(categories.items())[:3]:
                            st.metric(category, f"{score}%")
                    with col2:
                        for category, score in list(categories.items())[3:]:
                            st.metric(category, f"{score}%")
                    
                    # Risk factors
                    st.markdown("### ⚠️ Identified Risk Factors")
                    risk_factors = result.get('risk_factors', [])
                    for factor in risk_factors:
                        st.markdown(f"• {factor}")
                    
                    # Recommendations
                    st.markdown("### 💡 Recommendations")
                    recommendations = result.get('recommendations', [])
                    for rec in recommendations:
                        st.markdown(f"• {rec}")
                    
                    # Detailed explanation
                    if result.get('explanation'):
                        st.markdown("### 📝 Detailed Analysis")
                        st.write(result['explanation'])
                    
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")
        elif analyze_text_btn:
            st.warning("Please enter some content to analyze.")
    
    with tab2:
        st.markdown("### File Upload Analysis")
        
        uploaded_file = st.file_uploader(
            "Upload a file for analysis",
            type=['txt', 'pdf', 'docx', 'jpg', 'png'],
            help="Supported formats: TXT, PDF, DOCX, JPG, PNG"
        )
        
        if uploaded_file is not None:
            # Display file info
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            col1, col2 = st.columns([3, 1])
            with col2:
                analyze_file_btn = st.button("🔍 Analyze File", type="primary", use_container_width=True)
            
            if analyze_file_btn:
                with st.spinner("Extracting and analyzing content..."):
                    try:
                        # Extract content from file
                        content = st.session_state.extractor.extract_from_file(uploaded_file)
                        
                        if not content.strip():
                            st.warning("No readable text found in the uploaded file.")
                        else:
                            # Display extracted content preview
                            st.markdown("### 📄 Extracted Content Preview")
                            st.text_area("Content Preview", content[:500] + "..." if len(content) > 500 else content, height=150, disabled=True)
                            
                            # Get analysis settings
                            settings = {
                                'platform': platform,
                                'author_type': author_type,
                                'audience_size': audience_size,
                                'sensitivity': sensitivity
                            }
                            
                            # Analyze the content
                            result = st.session_state.analyzer.analyze_text(content, settings)
                            
                            # Display results (same as text analysis)
                            st.markdown("---")
                            st.markdown("### 📊 Analysis Results")
                            display_risk_meter(result['risk_percentage'])
                            st.markdown(f"**Risk Classification:** {display_risk_level(result['risk_percentage'])}", unsafe_allow_html=True)
                            
                            # Risk factors and recommendations
                            st.markdown("### ⚠️ Identified Risk Factors")
                            for factor in result.get('risk_factors', []):
                                st.markdown(f"• {factor}")
                            
                            st.markdown("### 💡 Recommendations")
                            for rec in result.get('recommendations', []):
                                st.markdown(f"• {rec}")
                            
                    except Exception as e:
                        st.error(f"File analysis failed: {str(e)}")
    
    with tab3:
        st.markdown("### URL Analysis")
        st.markdown("""
        <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <h4 style="margin: 0; color: #1f77b4;">🌐 Enhanced URL Analysis</h4>
            <p style="margin: 10px 0 0 0; color: #666;">
                <strong>Supported Sites:</strong> Regular websites, X.com/Twitter, Instagram, TikTok, LinkedIn, and more<br>
                <strong>Features:</strong> JavaScript execution, visual content extraction, screenshot capture, metadata analysis
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        url_input = st.text_input(
            "Enter URL to analyze:",
            placeholder="https://example.com or https://x.com/username/status/123456"
        )
        
        col1, col2 = st.columns([3, 1])
        with col2:
            analyze_url_btn = st.button("🌐 Analyze URL", type="primary", use_container_width=True)
        
        if analyze_url_btn and url_input.strip():
            with st.spinner("Fetching and analyzing URL content with visual elements..."):
                try:
                    # Enhanced URL analysis with visual content
                    url_analysis = st.session_state.extractor.extract_from_url_enhanced(url_input)
                    
                    if url_analysis.get('error'):
                        st.error(f"URL analysis failed: {url_analysis['error']}")
                    elif not url_analysis.get('text_content', '').strip():
                        st.warning("No readable content found at the provided URL.")
                    else:
                        # Display extracted content preview
                        st.markdown("### 📄 Extracted Content Preview")
                        content_preview = url_analysis['text_content'][:500] + "..." if len(url_analysis['text_content']) > 500 else url_analysis['text_content']
                        st.text_area("Content Preview", content_preview, height=150, disabled=True)
                        
                        # Display visual elements if available
                        if url_analysis.get('images') or url_analysis.get('visual_elements'):
                            with st.expander("🖼️ Visual Elements Found", expanded=False):
                                if url_analysis.get('images'):
                                    st.markdown("**Images:**")
                                    for img in url_analysis['images'][:5]:  # Show first 5 images
                                        if img.get('description'):
                                            st.markdown(f"• {img['description']}")
                                
                                if url_analysis.get('visual_elements'):
                                    st.markdown("**Other Visual Elements:**")
                                    for element in url_analysis['visual_elements']:
                                        if element.get('description'):
                                            st.markdown(f"• {element['description']}")
                        
                        # Display metadata if available
                        metadata = url_analysis.get('metadata', {})
                        if metadata.get('title') or metadata.get('description'):
                            with st.expander("📋 Page Metadata", expanded=False):
                                if metadata.get('title'):
                                    st.markdown(f"**Title:** {metadata['title']}")
                                if metadata.get('description'):
                                    st.markdown(f"**Description:** {metadata['description']}")
                        
                        # Get analysis settings
                        settings = {
                            'platform': platform,
                            'author_type': author_type,
                            'audience_size': audience_size,
                            'sensitivity': sensitivity
                        }
                        
                        # Prepare visual context for analysis
                        visual_context = None
                        if url_analysis.get('images') or url_analysis.get('visual_elements') or metadata:
                            visual_parts = []
                            if metadata.get('title'):
                                visual_parts.append(f"Page Title: {metadata['title']}")
                            if metadata.get('description'):
                                visual_parts.append(f"Page Description: {metadata['description']}")
                            if url_analysis.get('images'):
                                for img in url_analysis['images'][:3]:  # Include first 3 images
                                    if img.get('description'):
                                        visual_parts.append(f"Image: {img['description']}")
                            visual_context = "\n".join(visual_parts)
                        
                        # Analyze the content with visual context
                        result = st.session_state.analyzer.analyze_text(
                            url_analysis['text_content'], 
                            settings, 
                            visual_context
                        )
                        
                        # Display results
                        st.markdown("---")
                        st.markdown("### 📊 Analysis Results")
                        display_risk_meter(result['risk_percentage'])
                        st.markdown(f"**Risk Classification:** {display_risk_level(result['risk_percentage'])}", unsafe_allow_html=True)
                        
                        # Risk factors and recommendations
                        st.markdown("### ⚠️ Identified Risk Factors")
                        for factor in result.get('risk_factors', []):
                            st.markdown(f"• {factor}")
                        
                        st.markdown("### 💡 Recommendations")
                        for rec in result.get('recommendations', []):
                            st.markdown(f"• {rec}")
                        
                except Exception as e:
                    st.error(f"URL analysis failed: {str(e)}")
        elif analyze_url_btn:
            st.warning("Please enter a valid URL to analyze.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>⚠️ This tool provides AI-powered analysis for educational purposes. Always use your best judgment when posting content.</p>
        <p>Built with Streamlit and powered by Groq AI</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
