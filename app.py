"""
Stock AI Predictor - Streamlit Application
AI-driven stock market prediction using pattern recognition from news and social media.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import Database
from utils.data_collector import DataCollector
from utils.ai_analyzer import AIAnalyzer

# Page configuration
st.set_page_config(
    page_title="Stock AI Predictor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components
@st.cache_resource
def init_components():
    """Initialize database, data collector, and AI analyzer."""
    db = Database()
    collector = DataCollector()
    analyzer = AIAnalyzer()
    return db, collector, analyzer

db, collector, analyzer = init_components()

# Sidebar
st.sidebar.title("📈 Stock AI Predictor")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["Overview", "Predictions", "Performance", "Market Insights", "Settings"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
### About
AI-driven stock prediction using:
- Pattern recognition from news
- Social media sentiment analysis
- Correlation analysis
- Adaptive strategies
""")

# Main content
if page == "Overview":
    st.title("📊 Stock Market AI Predictor")
    st.markdown("### AI-Powered Pattern Recognition for Stock Market Predictions")
    
    # Market overview
    st.subheader("Market Overview")
    
    with st.spinner("Fetching market data..."):
        market_data = collector.get_market_overview()
    
    if market_data:
        cols = st.columns(len(market_data))
        for i, (name, data) in enumerate(market_data.items()):
            with cols[i]:
                change = data['change_percent']
                color = "🟢" if change >= 0 else "🔴"
                st.metric(
                    label=name,
                    value=f"${data['price']:,.2f}",
                    delta=f"{change:+.2f}%"
                )
    
    st.markdown("---")
    
    # Current predictions
    st.subheader("📈 Current Week Predictions")
    
    # Get predictions for current week
    today = datetime.now()
    week_end = today + timedelta(days=7)
    target_date = week_end.strftime('%Y-%m-%d')
    
    predictions = db.get_predictions(target_date=target_date, limit=20)
    
    if predictions:
        pred_df = pd.DataFrame(predictions)
        
        # Display predictions in a nice format
        for _, pred in pred_df.iterrows():
            with st.expander(f"{pred['symbol']} - {pred['name']} | Direction: {pred['direction'].upper()} | Confidence: {pred['confidence']:.0%}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Strategy:** {pred['strategy']}")
                    st.markdown(f"**Reasoning:** {pred['reasoning']}")
                
                with col2:
                    st.markdown(f"**Prediction Date:** {pred['prediction_date']}")
                    st.markdown(f"**Target Date:** {pred['target_date']}")
    else:
        st.info("No predictions available for this week. Run the prediction generation process.")
    
    st.markdown("---")
    
    # Overall accuracy
    st.subheader("🎯 Overall Performance")
    
    accuracy = db.get_overall_accuracy()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Overall Accuracy", f"{accuracy:.1f}%")
    
    with col2:
        instruments = db.get_instruments()
        st.metric("Tracked Instruments", len(instruments))
    
    with col3:
        all_predictions = db.get_predictions(limit=1000)
        st.metric("Total Predictions", len(all_predictions))

elif page == "Predictions":
    st.title("🔮 Prediction Details")
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        view_mode = st.selectbox("View", ["Current Week", "All Predictions", "By Date"])
    
    with col2:
        if view_mode == "By Date":
            selected_date = st.date_input("Select Date")
            target_date = selected_date.strftime('%Y-%m-%d')
        else:
            target_date = None
    
    # Get predictions
    if view_mode == "Current Week":
        week_end = datetime.now() + timedelta(days=7)
        predictions = db.get_predictions(target_date=week_end.strftime('%Y-%m-%d'), limit=50)
    elif view_mode == "By Date":
        predictions = db.get_predictions(target_date=target_date, limit=50)
    else:
        predictions = db.get_predictions(limit=100)
    
    if predictions:
        pred_df = pd.DataFrame(predictions)
        
        # Summary statistics
        st.subheader("Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Predictions", len(pred_df))
        
        with col2:
            up_count = len(pred_df[pred_df['direction'] == 'up'])
            st.metric("Bullish Predictions", up_count)
        
        with col3:
            down_count = len(pred_df[pred_df['direction'] == 'down'])
            st.metric("Bearish Predictions", down_count)
        
        with col4:
            avg_confidence = pred_df['confidence'].mean()
            st.metric("Avg Confidence", f"{avg_confidence:.0%}")
        
        st.markdown("---")
        
        # Predictions by strategy
        st.subheader("Predictions by Strategy")
        
        strategy_counts = pred_df['strategy'].value_counts()
        fig = px.pie(
            values=strategy_counts.values,
            names=strategy_counts.index,
            title="Distribution of Strategies"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Detailed predictions table
        st.subheader("Detailed Predictions")
        
        # Format dataframe for display
        display_df = pred_df[['symbol', 'name', 'direction', 'confidence', 'strategy', 'prediction_date', 'target_date']].copy()
        display_df['confidence'] = display_df['confidence'].apply(lambda x: f"{x:.0%}")
        
        st.dataframe(display_df, use_container_width=True)
        
    else:
        st.info("No predictions found for the selected criteria.")

elif page == "Performance":
    st.title("📊 Strategy Performance Analysis")
    
    # Get strategy performance data
    performance_data = db.get_strategy_performance(weeks=12)
    
    if performance_data:
        perf_df = pd.DataFrame(performance_data)
        
        # Overall accuracy by strategy
        st.subheader("Accuracy by Strategy")
        
        strategy_accuracy = perf_df.groupby('strategy').agg({
            'total_predictions': 'sum',
            'correct_predictions': 'sum'
        }).reset_index()
        
        strategy_accuracy['accuracy'] = (
            strategy_accuracy['correct_predictions'] / 
            strategy_accuracy['total_predictions'] * 100
        )
        
        fig = px.bar(
            strategy_accuracy,
            x='strategy',
            y='accuracy',
            title='Average Accuracy by Strategy',
            labels={'accuracy': 'Accuracy (%)', 'strategy': 'Strategy'},
            color='accuracy',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Performance over time
        st.subheader("Performance Trends Over Time")
        
        fig = px.line(
            perf_df,
            x='week_start',
            y='accuracy',
            color='strategy',
            title='Strategy Accuracy Over Time',
            labels={'accuracy': 'Accuracy (%)', 'week_start': 'Week'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Detailed statistics
        st.subheader("Detailed Statistics")
        
        display_df = strategy_accuracy[['strategy', 'total_predictions', 'correct_predictions', 'accuracy']].copy()
        display_df['accuracy'] = display_df['accuracy'].apply(lambda x: f"{x:.1f}%")
        display_df.columns = ['Strategy', 'Total Predictions', 'Correct', 'Accuracy']
        
        st.dataframe(display_df, use_container_width=True)
        
    else:
        st.info("No performance data available yet. Predictions need to be evaluated first.")
    
    st.markdown("---")
    
    # Overall metrics
    st.subheader("Overall Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        accuracy = db.get_overall_accuracy()
        st.metric("Overall Accuracy", f"{accuracy:.1f}%")
    
    with col2:
        all_preds = db.get_predictions(limit=1000)
        st.metric("Total Evaluated Predictions", len(all_preds))

elif page == "Market Insights":
    st.title("💡 Market Insights & Analysis")
    
    st.markdown("""
    This section provides AI-generated insights based on current market conditions,
    news sentiment, and social media trends.
    """)
    
    if st.button("Generate Fresh Insights"):
        with st.spinner("Analyzing market data and generating insights..."):
            # Get market data
            market_data = collector.get_market_overview()
            
            # Get some recent news
            news_items = collector.get_general_news("stock market", days_back=3)
            
            # Prepare data for AI analysis
            all_data = {
                'market_overview': market_data,
                'recent_news_count': len(news_items),
                'news_headlines': [item['title'] for item in news_items[:10]]
            }
            
            # Generate insights
            insights = analyzer.generate_market_insights(all_data)
            
            st.markdown("### Current Market Analysis")
            st.markdown(insights)
    
    st.markdown("---")
    
    # Show tracked instruments
    st.subheader("Tracked Instruments")
    
    instruments = db.get_instruments()
    
    if instruments:
        inst_df = pd.DataFrame(instruments)
        st.dataframe(inst_df[['symbol', 'name', 'sector']], use_container_width=True)
    else:
        st.info("No instruments are currently being tracked.")

elif page == "Settings":
    st.title("⚙️ Settings & Configuration")
    
    st.subheader("Tracked Instruments")
    
    # Show current instruments
    instruments = db.get_instruments()
    
    if instruments:
        st.markdown("**Currently tracking:**")
        for inst in instruments:
            st.text(f"• {inst['symbol']} - {inst['name']} ({inst['sector']})")
    
    st.markdown("---")
    
    # Add new instrument
    st.subheader("Add New Instrument")
    
    with st.form("add_instrument"):
        col1, col2 = st.columns(2)
        
        with col1:
            symbol = st.text_input("Stock Symbol (e.g., AAPL)", "").upper()
        
        with col2:
            sector = st.text_input("Sector (optional)", "")
        
        submitted = st.form_submit_button("Add Instrument")
        
        if submitted and symbol:
            with st.spinner(f"Fetching data for {symbol}..."):
                stock_data = collector.get_stock_data(symbol)
                
                if stock_data:
                    name = stock_data['name']
                    detected_sector = stock_data.get('sector', sector)
                    
                    inst_id = db.add_instrument(symbol, name, detected_sector)
                    
                    # Add price history
                    for record in stock_data['history']:
                        db.add_price_data(
                            inst_id,
                            record['Date'].strftime('%Y-%m-%d'),
                            record['Open'],
                            record['High'],
                            record['Low'],
                            record['Close'],
                            record['Volume']
                        )
                    
                    st.success(f"Added {symbol} - {name} successfully!")
                    st.rerun()
                else:
                    st.error(f"Could not fetch data for {symbol}. Please check the symbol.")
    
    st.markdown("---")
    
    # API Configuration
    st.subheader("API Configuration")
    
    st.markdown("""
    Configure API keys in your environment variables:
    - `OPENAI_API_KEY` - Required for AI analysis
    - `FINNHUB_API_KEY` - Optional, for news and sentiment
    - `NEWS_API_KEY` - Optional, for additional news sources
    - `REDDIT_CLIENT_ID` - Optional, for Reddit sentiment
    - `REDDIT_CLIENT_SECRET` - Optional, for Reddit sentiment
    """)
    
    # Check which APIs are configured
    st.markdown("**API Status:**")
    st.text(f"✓ OpenAI: Configured" if os.getenv('OPENAI_API_KEY') else "✗ OpenAI: Not configured")
    st.text(f"✓ Finnhub: Configured" if os.getenv('FINNHUB_API_KEY') else "✗ Finnhub: Not configured (optional)")
    st.text(f"✓ News API: Configured" if os.getenv('NEWS_API_KEY') else "✗ News API: Not configured (optional)")
    st.text(f"✓ Reddit: Configured" if os.getenv('REDDIT_CLIENT_ID') else "✗ Reddit: Not configured (optional)")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("© 2026 Stock AI Predictor")
st.sidebar.markdown("Powered by AI Pattern Recognition")
