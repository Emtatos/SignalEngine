"""
Daily update script - Run this daily to collect data and update analysis.
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import Database
from utils.data_collector import DataCollector
from utils.ai_analyzer import AIAnalyzer


def main():
    """Run daily data collection and analysis."""
    print(f"Starting daily update - {datetime.now()}")
    
    # Initialize components
    db = Database()
    collector = DataCollector()
    analyzer = AIAnalyzer()
    
    # Get all tracked instruments
    instruments = db.get_instruments()
    
    if not instruments:
        print("No instruments to track. Add instruments first.")
        return
    
    print(f"Tracking {len(instruments)} instruments")
    
    # Update price data for each instrument
    print("\n=== Updating Price Data ===")
    for inst in instruments:
        symbol = inst['symbol']
        inst_id = inst['id']
        
        print(f"Fetching data for {symbol}...")
        stock_data = collector.get_stock_data(symbol, period="3mo")
        
        if stock_data and stock_data.get('history'):
            for record in stock_data['history']:
                try:
                    db.add_price_data(
                        inst_id,
                        record['Date'].strftime('%Y-%m-%d'),
                        record['Open'],
                        record['High'],
                        record['Low'],
                        record['Close'],
                        record['Volume']
                    )
                except Exception as e:
                    print(f"Error adding price data: {e}")
            
            print(f"✓ Updated {len(stock_data['history'])} price records for {symbol}")
        else:
            print(f"✗ Failed to fetch data for {symbol}")
    
    # Collect news for each instrument
    print("\n=== Collecting News ===")
    for inst in instruments:
        symbol = inst['symbol']
        inst_id = inst['id']
        
        print(f"Fetching news for {symbol}...")
        news_items = collector.get_finnhub_news(symbol, days_back=1)
        
        for item in news_items:
            # Analyze sentiment
            sentiment_result = analyzer.analyze_sentiment(
                f"{item['title']} {item['content']}"
            )
            
            try:
                db.add_news(
                    inst_id,
                    item['title'],
                    item['content'],
                    item['source'],
                    item['url'],
                    item['published_at'],
                    sentiment_result['sentiment_score'],
                    sentiment_result['sentiment_label']
                )
            except Exception as e:
                print(f"Error adding news: {e}")
        
        print(f"✓ Added {len(news_items)} news items for {symbol}")
    
    # Collect social media data
    print("\n=== Collecting Social Media Data ===")
    for inst in instruments:
        symbol = inst['symbol']
        inst_id = inst['id']
        
        print(f"Fetching social data for {symbol}...")
        posts = collector.get_reddit_sentiment_data(symbol)
        
        for post in posts[:20]:  # Limit to avoid overwhelming
            # Analyze sentiment
            sentiment_result = analyzer.analyze_sentiment(
                f"{post.get('title', '')} {post.get('content', '')}"
            )
            
            try:
                db.add_social_post(
                    inst_id,
                    'reddit',
                    post['post_id'],
                    f"{post.get('title', '')} {post.get('content', '')}",
                    post['author'],
                    post['score'],
                    post['comments_count'],
                    post['posted_at'],
                    sentiment_result['sentiment_score'],
                    sentiment_result['sentiment_label']
                )
            except Exception as e:
                print(f"Error adding social post: {e}")
        
        print(f"✓ Added {len(posts)} social posts for {symbol}")
    
    print("\n=== Daily Update Complete ===")
    print(f"Finished at {datetime.now()}")


if __name__ == "__main__":
    main()
