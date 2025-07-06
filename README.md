# 🍽️ Restaurant Sentiment Analysis Tool

**Dynamic Restaurant Review Analysis with Web Scraping & AI**

This tool automatically scrapes restaurant reviews from the web and generates comprehensive sentiment analysis reports using advanced AI technology.

## 🚀 Features

- **Web Scraping**: Automatically finds and extracts reviews from trusted sites (Google, Yelp, TripAdvisor, etc.)
- **AI Analysis**: Uses Google Gemini AI for sophisticated sentiment and aspect analysis
- **Comprehensive Reports**: Generates detailed HTML reports with actionable insights
- **Easy to Use**: Simple command-line interface - just provide a restaurant name
- **Trusted Sources**: Only scrapes from verified review platforms

## 📋 Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- API keys for:
  - [Tavily](https://tavily.com/) (web search)
  - [Google Gemini](https://ai.google.dev/) (AI analysis)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd restaurant-sentiment
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Get API Keys**:
   - **Tavily**: Sign up at [tavily.com](https://tavily.com/) and get your API key
   - **Gemini**: Get your API key from [Google AI Studio](https://ai.google.dev/)

## 🔧 Environment Setup

Create a `.env` file with your API keys:

```env
# API Keys
TAVILY_API_KEY=tvly-your-tavily-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here

# Configuration (optional)
MIN_REVIEWS=5
MAX_REVIEWS=50
CONFIDENCE_THRESHOLD=0.8
```

## 🎯 Usage

Simply run the tool and provide a restaurant name:

```bash
python run.py
```

The tool will:
1. 🔍 Search for restaurant reviews across the web
2. 📊 Extract and analyze reviews using AI
3. 📈 Generate a comprehensive report with actionable insights

### Example:
```bash
python run.py
> Enter restaurant name: Joe's Pizza
> Enter location (optional): New York
> Max reviews to analyze (default: 30): 25
```

## 📊 What You Get

The tool generates two types of reports:

1. **JSON Report**: Raw data and analysis results
2. **HTML Report**: Beautiful, interactive report with:
   - Overall sentiment analysis
   - Aspect-based feedback (food, service, ambiance, etc.)
   - Strengths and weaknesses
   - Actionable improvement suggestions
   - Visual charts and metrics

## 🎨 Sample Output

```
🍽️ Restaurant Sentiment Analysis Tool
==================================================
🔍 Analyzing 'Joe's Pizza' New York...
📊 Target: 25 reviews

1️⃣ Scraping reviews from the web...
✅ Found 23 reviews

2️⃣ Analyzing reviews with AI...
Analyzing review 1/23...
...

3️⃣ Generating comprehensive report...
==================================================
📈 ANALYSIS COMPLETE
==================================================
Restaurant: Joe's Pizza
Reviews Analyzed: 23
Overall Rating: 4.2/5.0
Sentiment: {'POSITIVE': 18, 'NEGATIVE': 5, 'NEUTRAL': 0}

🎯 TOP STRENGTHS:
  1. Excellent pizza quality and taste
  2. Fast service and quick delivery
  3. Good value for money

⚠️ TOP WEAKNESSES:
  1. Limited seating space
  2. Inconsistent service during peak hours
  3. Could improve ambiance

💡 KEY ACTIONABLE INSIGHTS:
  1. Consider expanding seating capacity
  2. Implement better queue management system
  3. Train staff for consistent service quality
  4. Enhance interior design and lighting
  5. Maintain food quality consistency

📄 Reports saved:
  📊 JSON: reports/joes_pizza_20241206_143022.json
  🌐 HTML: reports/joes_pizza_20241206_143022.html
```

## 🔧 Technical Details

### Architecture
- **Web Scraper** (`src/web_scraper.py`): Uses Tavily API to search and extract reviews
- **AI Analyzer** (`src/gemini_analyzer.py`): Uses Google Gemini for sentiment analysis
- **Report Generator** (`src/report_gen.py`): Creates HTML reports with insights

### Trusted Review Sources
- Google Maps/Reviews
- Yelp
- TripAdvisor
- OpenTable
- Foursquare
- Zomato
- Grubhub
- DoorDash
- Uber Eats

### AI Analysis Features
- Sentiment classification (Positive/Negative/Neutral)
- Aspect-based analysis (food, service, ambiance, etc.)
- Confidence scoring
- Actionable insight generation
- Summary creation

## 🔒 Privacy & Ethics

- Only scrapes publicly available reviews
- Respects website terms of service
- Filters content through trusted domains only
- No personal data collection
- Transparent analysis process

## 🤝 Contributing

Feel free to open issues or submit pull requests to improve the tool.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

**Built with**:
- [Tavily](https://tavily.com/) for web search
- [Google Gemini](https://ai.google.dev/) for AI analysis
- [uv](https://docs.astral.sh/uv/) for dependency management