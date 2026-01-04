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
    "Navigering",
    ["Översikt", "Prediktioner", "Prestanda", "Marknadsinsikter", "Inställningar"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
### Om tjänsten
AI-driven aktieanalys med:
- Mönsterigenkänning från nyheter
- Sentimentanalys från sociala medier
- Korrelationsanalys
- Adaptiva strategier
""")

# Main content
if page == "Översikt":
    st.title("📊 Stock Market AI Predictor")
    st.markdown("### AI-driven mönsterigenkänning för aktiemarknaden")
    
    # Market overview
    st.subheader("Marknadsöversikt")
    
    with st.spinner("Hämtar marknadsdata..."):
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
    st.subheader("📈 Prediktioner för kommande vecka")
    
    # Get predictions for current week
    today = datetime.now()
    week_end = today + timedelta(days=7)
    target_date = week_end.strftime('%Y-%m-%d')
    
    predictions = db.get_predictions(target_date=target_date, limit=20)
    
    if predictions:
        pred_df = pd.DataFrame(predictions)
        
        # Display predictions in a nice format
        for _, pred in pred_df.iterrows():
            direction_sv = "UPP" if pred['direction'].lower() == 'up' else "NER"
            with st.expander(f"{pred['symbol']} - {pred['name']} | Riktning: {direction_sv} | Tillförlitlighet: {pred['confidence']:.0%}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Strategi:** {pred['strategy']}")
                    st.markdown(f"**Resonemang:** {pred['reasoning']}")
                
                with col2:
                    st.markdown(f"**Prediktionsdatum:** {pred['prediction_date']}")
                    st.markdown(f"**Måldatum:** {pred['target_date']}")
    else:
        st.info("Inga prediktioner tillgängliga för denna vecka. Kör prediktionsprocessen.")
    
    st.markdown("---")
    
    # Overall accuracy
    st.subheader("🎯 Total Prestanda")
    
    accuracy = db.get_overall_accuracy()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Träffsäkerhet", f"{accuracy:.1f}%")
    
    with col2:
        instruments = db.get_instruments()
        st.metric("Spårade Instrument", len(instruments))
    
    with col3:
        all_predictions = db.get_predictions(limit=1000)
        st.metric("Totalt antal Prediktioner", len(all_predictions))

elif page == "Prediktioner":
    st.title("🔮 Detaljerade Prediktioner")
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        view_mode = st.selectbox("Visa", ["Denna vecka", "Alla prediktioner", "Per datum"])
    
    with col2:
        if view_mode == "Per datum":
            selected_date = st.date_input("Välj datum")
            target_date = selected_date.strftime('%Y-%m-%d')
        else:
            target_date = None
    
    # Get predictions
    if view_mode == "Denna vecka":
        week_end = datetime.now() + timedelta(days=7)
        predictions = db.get_predictions(target_date=week_end.strftime('%Y-%m-%d'), limit=50)
    elif view_mode == "Per datum":
        predictions = db.get_predictions(target_date=target_date, limit=50)
    else:
        predictions = db.get_predictions(limit=100)
    
    if predictions:
        pred_df = pd.DataFrame(predictions)
        
        # Summary statistics
        st.subheader("Sammanfattning")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Totalt antal", len(pred_df))
        
        with col2:
            up_count = len(pred_df[pred_df['direction'] == 'up'])
            st.metric("Bullish (Upp)", up_count)
        
        with col3:
            down_count = len(pred_df[pred_df['direction'] == 'down'])
            st.metric("Bearish (Ner)", down_count)
        
        with col4:
            avg_confidence = pred_df['confidence'].mean()
            st.metric("Snitt Tillförlitlighet", f"{avg_confidence:.0%}")
        
        st.markdown("---")
        
        # Predictions by strategy
        st.subheader("Prediktioner per Strategi")
        
        strategy_counts = pred_df['strategy'].value_counts()
        fig = px.pie(
            values=strategy_counts.values,
            names=strategy_counts.index,
            title="Fördelning av strategier"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Detailed predictions table
        st.subheader("Detaljerad tabell")
        
        # Format dataframe for display
        display_df = pred_df[['symbol', 'name', 'direction', 'confidence', 'strategy', 'prediction_date', 'target_date']].copy()
        display_df['confidence'] = display_df['confidence'].apply(lambda x: f"{x:.0%}")
        display_df.columns = ['Symbol', 'Namn', 'Riktning', 'Tillförlitlighet', 'Strategi', 'Datum', 'Måldatum']
        
        st.dataframe(display_df, use_container_width=True)
        
    else:
        st.info("Inga prediktioner hittades för valda kriterier.")

elif page == "Prestanda":
    st.title("📊 Analys av Strategiernas Prestanda")
    
    # Get strategy performance data
    performance_data = db.get_strategy_performance(weeks=12)
    
    if performance_data:
        perf_df = pd.DataFrame(performance_data)
        
        # Overall accuracy by strategy
        st.subheader("Träffsäkerhet per Strategi")
        
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
            title='Genomsnittlig träffsäkerhet per strategi',
            labels={'accuracy': 'Träffsäkerhet (%)', 'strategy': 'Strategi'},
            color='accuracy',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Performance over time
        st.subheader("Prestandatrender över tid")
        
        fig = px.line(
            perf_df,
            x='week_start',
            y='accuracy',
            color='strategy',
            title='Strategiernas träffsäkerhet över tid',
            labels={'accuracy': 'Träffsäkerhet (%)', 'week_start': 'Vecka'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Detailed statistics
        st.subheader("Detaljerad statistik")
        
        display_df = strategy_accuracy[['strategy', 'total_predictions', 'correct_predictions', 'accuracy']].copy()
        display_df['accuracy'] = display_df['accuracy'].apply(lambda x: f"{x:.1f}%")
        display_df.columns = ['Strategi', 'Totalt antal', 'Korrekt', 'Träffsäkerhet']
        
        st.dataframe(display_df, use_container_width=True)
        
    else:
        st.info("Ingen prestandadata tillgänglig ännu. Prediktioner måste utvärderas först.")
    
    st.markdown("---")
    
    # Overall metrics
    st.subheader("Övergripande statistik")
    
    col1, col2 = st.columns(2)
    
    with col1:
        accuracy = db.get_overall_accuracy()
        st.metric("Total Träffsäkerhet", f"{accuracy:.1f}%")
    
    with col2:
        all_preds = db.get_predictions(limit=1000)
        st.metric("Totalt utvärderade prediktioner", len(all_preds))

elif page == "Marknadsinsikter":
    st.title("💡 Marknadsinsikter & Analys")
    
    st.markdown("""
    Denna sektion innehåller AI-genererade insikter baserade på aktuella marknadsförhållanden,
    nyhetssentiment och trender i sociala medier.
    """)
    
    if st.button("Generera nya insikter"):
        with st.spinner("Analyserar marknadsdata och genererar insikter..."):
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
            
            st.markdown("### Aktuell marknadsanalys")
            st.markdown(insights)
    
    st.markdown("---")
    
    # Show tracked instruments
    st.subheader("Spårade Instrument")
    
    instruments = db.get_instruments()
    
    if instruments:
        inst_df = pd.DataFrame(instruments)
        display_inst = inst_df[['symbol', 'name', 'sector']].copy()
        display_inst.columns = ['Symbol', 'Namn', 'Sektor']
        st.dataframe(display_inst, use_container_width=True)
    else:
        st.info("Inga instrument spåras för tillfället.")

elif page == "Inställningar":
    st.title("⚙️ Inställningar & Konfiguration")
    
    st.subheader("Spårade Instrument")
    
    # Show current instruments
    instruments = db.get_instruments()
    
    if instruments:
        st.markdown("**Spåras just nu:**")
        for inst in instruments:
            st.text(f"• {inst['symbol']} - {inst['name']} ({inst['sector']})")
    
    st.markdown("---")
    
    # Add new instrument
    st.subheader("Lägg till nytt instrument")
    
    with st.form("add_instrument"):
        col1, col2 = st.columns(2)
        
        with col1:
            symbol = st.text_input("Aktiesymbol (t.ex. AAPL)", "").upper()
        
        with col2:
            sector = st.text_input("Sektor (valfritt)", "")
        
        submitted = st.form_submit_button("Lägg till instrument")
        
        if submitted and symbol:
            with st.spinner(f"Hämtar data för {symbol}..."):
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
                    
                    st.success(f"Lade till {symbol} - {name} framgångsrikt!")
                    st.rerun()
                else:
                    st.error(f"Kunde inte hämta data för {symbol}. Kontrollera symbolen.")
    
    st.markdown("---")
    
    # API Configuration
    st.subheader("API-konfiguration")
    
    st.markdown("""
    Konfigurera API-nycklar i dina miljövariabler:
    - `OPENAI_API_KEY` - Krävs för AI-analys
    - `FINNHUB_API_KEY` - Valfritt, för nyheter och sentiment
    - `NEWS_API_KEY` - Valfritt, för ytterligare nyhetskällor
    - `REDDIT_CLIENT_ID` - Valfritt, för Reddit-sentiment
    - `REDDIT_CLIENT_SECRET` - Valfritt, för Reddit-sentiment
    """)
    
    # Check which APIs are configured
    st.markdown("**API-status:**")
    st.text(f"✓ OpenAI: Konfigurerad" if os.getenv('OPENAI_API_KEY') else "✗ OpenAI: Ej konfigurerad")
    st.text(f"✓ Finnhub: Konfigurerad" if os.getenv('FINNHUB_API_KEY') else "✗ Finnhub: Ej konfigurerad (valfritt)")
    st.text(f"✓ News API: Konfigurerad" if os.getenv('NEWS_API_KEY') else "✗ News API: Ej konfigurerad (valfritt)")
    st.text(f"✓ Reddit: Konfigurerad" if os.getenv('REDDIT_CLIENT_ID') else "✗ Reddit: Ej konfigurerad (valfritt)")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("© 2026 Stock AI Predictor")
st.sidebar.markdown("Drivs av AI-mönsterigenkänning")
