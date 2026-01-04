"""
Weekly prediction script - Run this weekly to generate predictions for the coming week.
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import Database
from utils.data_collector import DataCollector
from utils.ai_analyzer import AIAnalyzer


def main():
    """Generate weekly predictions."""
    print(f"Starting weekly prediction generation - {datetime.now()}")
    
    # Initialize components
    db = Database()
    collector = DataCollector()
    analyzer = AIAnalyzer()
    
    # Get all tracked instruments
    instruments = db.get_instruments()
    
    if not instruments:
        print("No instruments to predict. Add instruments first.")
        return
    
    print(f"Generating predictions for {len(instruments)} instruments")
    
    # Get market context
    print("\n=== Getting Market Context ===")
    market_context = collector.get_market_overview()
    print(f"Market overview: {list(market_context.keys())}")
    
    # Prepare data for each instrument
    instruments_data = []
    
    for inst in instruments:
        symbol = inst['symbol']
        inst_id = inst['id']
        
        # Get price history
        history = db.get_price_history(inst_id, days=365)
        
        instruments_data.append({
            'id': inst_id,
            'symbol': symbol,
            'name': inst['name'],
            'sector': inst['sector'],
            'history': history
        })
    
    # Find correlations
    print("\n=== Analyzing Correlations ===")
    correlations = analyzer.find_correlations(instruments_data)
    print(f"Found {len(correlations)} correlations")
    
    for corr in correlations:
        print(f"  {corr.get('instrument1')} <-> {corr.get('instrument2')}: {corr.get('relationship')} ({corr.get('strength')})")
    
    # Generate predictions for each instrument
    print("\n=== Generating Predictions ===")
    
    prediction_date = datetime.now().strftime('%Y-%m-%d')
    target_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    
    predictions_made = 0
    
    for inst_data in instruments_data:
        symbol = inst_data['symbol']
        inst_id = inst_data['id']
        
        print(f"\nAnalyzing {symbol}...")
        
        # Get recent news (from database)
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT title, content, sentiment, sentiment_label
            FROM news_items
            WHERE instrument_id = ?
            AND created_at > datetime('now', '-7 days')
            ORDER BY created_at DESC
            LIMIT 20
        """, (inst_id,))
        
        news = []
        for row in cursor.fetchall():
            news.append({
                'title': row[0],
                'content': row[1],
                'sentiment': row[2],
                'sentiment_label': row[3]
            })
        
        # Get recent social posts
        cursor.execute("""
            SELECT content, score, sentiment, sentiment_label
            FROM social_posts
            WHERE instrument_id = ?
            AND created_at > datetime('now', '-7 days')
            ORDER BY created_at DESC
            LIMIT 50
        """, (inst_id,))
        
        social_posts = []
        for row in cursor.fetchall():
            social_posts.append({
                'content': row[0],
                'score': row[1],
                'sentiment': row[2],
                'sentiment_label': row[3]
            })
        
        conn.close()
        
        print(f"  News items: {len(news)}")
        print(f"  Social posts: {len(social_posts)}")
        
        # Generate prediction
        prediction = analyzer.generate_predictions(
            inst_data,
            news,
            social_posts,
            market_context,
            correlations
        )
        
        if prediction:
            # Save prediction to database
            db.add_prediction(
                inst_id,
                prediction_date,
                target_date,
                prediction['direction'],
                prediction['confidence'],
                prediction['reasoning'],
                prediction['strategy']
            )
            
            predictions_made += 1
            
            print(f"  ✓ Prediction: {prediction['direction'].upper()}")
            print(f"    Confidence: {prediction['confidence']:.0%}")
            print(f"    Strategy: {prediction['strategy']}")
            print(f"    Risk: {prediction.get('risk_level', 'unknown')}")
        else:
            print(f"  ✗ Failed to generate prediction")
    
    print(f"\n=== Weekly Prediction Complete ===")
    print(f"Generated {predictions_made} predictions for week ending {target_date}")
    print(f"Finished at {datetime.now()}")


if __name__ == "__main__":
    main()
