# 🚨 Cancellable Content Checker

An AI-powered web application that analyzes content for potential "cancellation" risk in social media contexts. Built with Streamlit and powered by Groq AI.

## 🌟 Features

- **Multi-Input Analysis**: Analyze text, files (PDF, DOCX, TXT, images), and URLs
- **Real-time Risk Assessment**: Get instant feedback on content cancellation risk
- **Comprehensive Categories**: 6 risk categories with weighted scoring
- **Platform-Aware**: Context-aware analysis for different social media platforms
- **Visual Results**: Risk meters, color-coded levels, and detailed breakdowns
- **Actionable Recommendations**: Specific suggestions for content improvement

## 🎯 Risk Assessment Framework

The tool analyzes content across 6 categories:

1. **Identity & Discrimination** (25%) - Offensive language, discriminatory statements
2. **Political Sensitivity** (20%) - Extreme positions, conspiracy theories
3. **Social Issues** (20%) - Controversial takes on current events
4. **Professional Appropriateness** (15%) - Workplace conduct, ethics
5. **Platform Violations** (10%) - Harassment, terms of service violations
6. **Timing & Context** (10%) - Current events sensitivity, trending topics

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd Cancel-detector

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

1. Get your Groq API key from [console.groq.com](https://console.groq.com/keys)
2. Edit `.streamlit/secrets.toml` and add your API key:

```toml
GROQ_API_KEY = "your_actual_api_key_here"
```

### 3. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📱 Usage

### Text Analysis
1. Go to the "Text Analysis" tab
2. Paste your content in the text area
3. Configure analysis settings in the sidebar
4. Click "Analyze Content"

### File Upload
1. Go to the "File Upload" tab
2. Upload supported files (TXT, PDF, DOCX, JPG, PNG)
3. Click "Analyze File"

### URL Analysis
1. Go to the "URL Analysis" tab
2. Enter a URL to analyze
3. Click "Analyze URL"

## ⚙️ Configuration Options

### Analysis Settings
- **Target Platform**: Twitter, LinkedIn, Instagram, Facebook, YouTube, TikTok, General
- **Author Type**: Individual, Public Figure, Corporate, Influencer, Journalist, Politician
- **Audience Size**: < 1K to > 1M followers
- **Analysis Sensitivity**: 1-10 scale (higher = more conservative)

### API Models
- **Primary Model**: `llama-3.1-70b-versatile` (comprehensive analysis)
- **Fallback Model**: `llama-3.1-8b-instant` (faster responses)

## 🔧 Technical Details

### Dependencies
- **Streamlit**: Web application framework
- **Groq**: AI analysis engine
- **BeautifulSoup4**: HTML parsing for URL analysis
- **PyPDF2**: PDF text extraction
- **python-docx**: DOCX file processing
- **Pillow + pytesseract**: OCR for image text extraction

### File Structure
```
Cancel-detector/
├── app.py                 # Main Streamlit application
├── analyzer.py           # Core analysis logic with Groq
├── extractors.py         # Content extraction utilities
├── prompts.py            # AI prompts and templates
├── requirements.txt      # Dependencies
├── .streamlit/
│   └── secrets.toml      # API keys and configuration
└── README.md            # Documentation
```

## 🎨 Features in Detail

### Risk Visualization
- **Progress Bar**: Visual risk percentage display
- **Color Coding**: Green (Low), Yellow (Medium), Red (High)
- **Category Breakdown**: Individual scores for each risk category
- **Risk Factors**: Specific issues identified in the content

### Content Processing
- **Text Limiting**: Analysis limited to first 4000 characters for cost efficiency
- **Caching**: Recent analyses cached to avoid duplicate API calls
- **Error Handling**: Graceful handling of API failures and invalid inputs
- **Batch Processing**: Support for analyzing multiple content pieces

### Cost Optimization
- **Groq Pricing**: ~$0.59/1M input tokens (extremely competitive)
- **Smart Model Selection**: Use faster model for simple analyses
- **Content Truncation**: Limit analysis length to control costs
- **Result Caching**: Avoid redundant API calls

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py
```

### Streamlit Community Cloud
1. Push code to GitHub
2. Connect repository to Streamlit Cloud
3. Add `GROQ_API_KEY` to secrets in Streamlit Cloud dashboard

### Production Deployment (Railway/Similar)
1. Set environment variables
2. Deploy with `streamlit run app.py`
3. Configure domain and SSL

## ⚠️ Important Notes

- **Educational Purpose**: This tool is for educational and awareness purposes
- **Human Judgment**: Always use your best judgment when posting content
- **API Costs**: Monitor Groq API usage to control costs
- **Privacy**: Content is processed by Groq AI - ensure compliance with your privacy requirements

## 🔮 Future Enhancements

- Real-time social media monitoring
- Browser extension for in-platform analysis
- Team collaboration features
- Historical trend analysis
- Multi-language support
- Advanced vision model integration

## 📊 Success Metrics

- Analysis accuracy and relevance
- User engagement and retention
- Response time performance (< 3 seconds target)
- Cost per analysis optimization
- User feedback on recommendations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues:

1. Check the console logs for error messages
2. Verify your Groq API key is correct
3. Ensure all dependencies are installed
4. Check that your internet connection is stable

For additional support, please open an issue in the repository.

---

**Built with ❤️ using Streamlit and powered by Groq AI**
