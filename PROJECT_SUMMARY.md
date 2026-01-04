# Stock AI Predictor - Project Summary

## Overview
Stock AI Predictor är ett komplett AI-drivet aktieanalysprogram som använder mönsterigenkänning från nyheter, sociala medier och marknadsdata för att prediktera aktierörelser.

## Key Features
✓ AI-driven pattern recognition using OpenAI GPT-4.1-mini
✓ Multi-source data collection (stocks, news, Reddit)
✓ Sentiment analysis from news and social media
✓ Correlation analysis between instruments
✓ Adaptive strategy selection
✓ Weekly accuracy reporting
✓ Interactive Streamlit dashboard
✓ Ready for Render deployment
✓ Automated daily updates and weekly predictions

## Technology Stack
- **Frontend**: Streamlit
- **AI/ML**: OpenAI GPT-4.1-mini
- **Data Sources**: yfinance, Finnhub, News API, Reddit (PRAW)
- **Database**: SQLite
- **Visualization**: Plotly
- **Deployment**: Render
- **Version Control**: Git/GitHub

## Project Structure
```
stock-ai-predictor/
├── models/
│   └── database.py          # Database models and operations
├── utils/
│   ├── ai_analyzer.py       # AI-powered analysis
│   └── data_collector.py    # Data collection from APIs
├── app.py                   # Main Streamlit application
├── run_daily_update.py      # Daily data collection script
├── run_weekly_prediction.py # Weekly prediction generation
├── run_evaluation.py        # Prediction evaluation script
├── requirements.txt         # Python dependencies
├── render.yaml             # Render deployment config
├── README.md               # Main documentation
├── DEPLOYMENT.md           # Deployment guide
├── GITHUB_SETUP.md         # GitHub setup guide
└── LICENSE                 # MIT License
```

## Core Components

### 1. Database Layer (models/database.py)
- SQLite database with 7 tables
- Stores instruments, prices, news, social posts, predictions, results
- Tracks strategy performance over time

### 2. Data Collection (utils/data_collector.py)
- Fetches stock prices via yfinance
- Collects news from Finnhub and News API
- Gathers Reddit posts from multiple subreddits
- Provides market overview data

### 3. AI Analysis (utils/ai_analyzer.py)
- Sentiment analysis using OpenAI
- Pattern recognition and correlation discovery
- Multi-strategy prediction generation
- Strategy performance evaluation

### 4. Streamlit Dashboard (app.py)
- Overview: Current predictions and market status
- Predictions: Detailed prediction view with filtering
- Performance: Strategy accuracy analysis
- Market Insights: AI-generated market analysis
- Settings: Instrument management and API configuration

## Strategies Implemented

1. **Momentum Strategy**: Follows strong trends in price and sentiment
2. **Contrarian Strategy**: Identifies overreactions and potential reversals
3. **Correlation Strategy**: Uses instrument relationships for predictions
4. **News Impact Strategy**: Analyzes market reactions to news events

## Data Flow

1. **Daily**: Collect prices, news, social media → Analyze sentiment
2. **Weekly**: Generate predictions using AI → Store in database
3. **Weekly**: Evaluate past predictions → Update accuracy metrics
4. **Continuous**: Display results in Streamlit dashboard

## API Requirements

### Required:
- OpenAI API Key (for AI analysis)

### Optional but Recommended:
- Finnhub API Key (news and sentiment)
- News API Key (additional news sources)
- Reddit API Credentials (social media sentiment)

## Deployment Options

### Local Development:
```bash
streamlit run app.py
```

### Render (Recommended):
- Web Service: Streamlit dashboard
- Cron Jobs: Automated updates and predictions
- Free tier available

## Cost Estimation

- **Free Components**: yfinance, Reddit API, Render free tier
- **Paid Components**: 
  - OpenAI: ~$5-20/month
  - Render (optional upgrade): $7/month
  - Other APIs: Free tiers available

**Total**: $5-30/month for basic usage

## Key Files

- `app.py`: Main Streamlit application (350+ lines)
- `models/database.py`: Database operations (450+ lines)
- `utils/ai_analyzer.py`: AI analysis engine (320+ lines)
- `utils/data_collector.py`: Data collection (280+ lines)
- `README.md`: Complete documentation (400+ lines)
- `DEPLOYMENT.md`: Deployment guide (350+ lines)

## Testing Status

✓ Database initialization and operations
✓ Stock data collection via yfinance
✓ AI sentiment analysis with OpenAI
✓ All core modules import successfully
✓ Test instrument (AAPL) added successfully

## Next Steps for Users

1. Clone/download the project
2. Install dependencies: `pip install -r requirements.txt`
3. Configure API keys in `.env` file
4. Add instruments via Streamlit Settings
5. Run daily update: `python run_daily_update.py`
6. Generate predictions: `python run_weekly_prediction.py`
7. View results in Streamlit dashboard
8. Deploy to Render for production use

## Limitations and Disclaimers

⚠️ **IMPORTANT**: This is for educational purposes only, NOT financial advice
- Predictions are not guaranteed
- Past performance doesn't guarantee future results
- Always consult a financial advisor
- Use at your own risk

## Future Enhancements

- [ ] Support for more data sources (Twitter/X, StockTwits)
- [ ] Backtesting functionality
- [ ] Email notifications
- [ ] Portfolio tracking
- [ ] Risk management tools
- [ ] Multi-language support
- [ ] Mobile app

## License

MIT License - See LICENSE file for details

## Created

January 2026 - Built with AI assistance

---

**Total Lines of Code**: ~2,500+
**Total Files**: 16
**Documentation**: 1,200+ lines across multiple files
**Status**: Production-ready ✓
