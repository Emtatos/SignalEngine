"""
Data collection utilities for stock prices, news, and social media.
"""
import yfinance as yf
import requests
import praw
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os
import time


class DataCollector:
    """Collect data from various sources."""
    
    def __init__(self):
        self.finnhub_api_key = os.getenv('FINNHUB_API_KEY', '')
        self.news_api_key = os.getenv('NEWS_API_KEY', '')
        self.reddit_client_id = os.getenv('REDDIT_CLIENT_ID', '')
        self.reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET', '')
        self.reddit_user_agent = 'StockAIPredictor/1.0'
        
        # Initialize Reddit client if credentials available
        self.reddit = None
        if self.reddit_client_id and self.reddit_client_secret:
            try:
                self.reddit = praw.Reddit(
                    client_id=self.reddit_client_id,
                    client_secret=self.reddit_client_secret,
                    user_agent=self.reddit_user_agent
                )
            except Exception as e:
                print(f"Reddit initialization failed: {e}")
    
    def get_stock_data(self, symbol: str, period: str = "1y") -> Optional[Dict]:
        """
        Get stock price data from Yahoo Finance.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: Time period ('1y' for 1 year, '6mo' for 6 months, etc.)
        
        Returns:
            Dictionary with price history or None if failed
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return None
            
            # Get company info
            info = ticker.info
            
            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'history': hist.reset_index().to_dict('records')
            }
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def get_finnhub_news(self, symbol: str, days_back: int = 7) -> List[Dict]:
        """
        Get news from Finnhub API.
        
        Args:
            symbol: Stock symbol
            days_back: Number of days to look back
        
        Returns:
            List of news items
        """
        if not self.finnhub_api_key:
            return []
        
        try:
            from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            to_date = datetime.now().strftime('%Y-%m-%d')
            
            url = f"https://finnhub.io/api/v1/company-news"
            params = {
                'symbol': symbol,
                'from': from_date,
                'to': to_date,
                'token': self.finnhub_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            news_items = response.json()
            
            return [{
                'title': item.get('headline', ''),
                'content': item.get('summary', ''),
                'source': item.get('source', 'Finnhub'),
                'url': item.get('url', ''),
                'published_at': datetime.fromtimestamp(item.get('datetime', 0)).isoformat()
            } for item in news_items[:20]]  # Limit to 20 items
            
        except Exception as e:
            print(f"Error fetching Finnhub news for {symbol}: {e}")
            return []
    
    def get_general_news(self, query: str, days_back: int = 7) -> List[Dict]:
        """
        Get general financial news from News API.
        
        Args:
            query: Search query
            days_back: Number of days to look back
        
        Returns:
            List of news items
        """
        if not self.news_api_key:
            return []
        
        try:
            from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'from': from_date,
                'sortBy': 'relevancy',
                'language': 'en',
                'apiKey': self.news_api_key,
                'pageSize': 20
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('articles', [])
            
            return [{
                'title': article.get('title', ''),
                'content': article.get('description', ''),
                'source': article.get('source', {}).get('name', 'NewsAPI'),
                'url': article.get('url', ''),
                'published_at': article.get('publishedAt', '')
            } for article in articles]
            
        except Exception as e:
            print(f"Error fetching general news: {e}")
            return []
    
    def get_reddit_posts(self, subreddit_name: str, symbol: str, limit: int = 50) -> List[Dict]:
        """
        Get Reddit posts mentioning a stock symbol.
        
        Args:
            subreddit_name: Name of subreddit (e.g., 'wallstreetbets')
            symbol: Stock symbol to search for
            limit: Maximum number of posts to retrieve
        
        Returns:
            List of Reddit posts
        """
        if not self.reddit:
            return []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []
            
            # Search for posts mentioning the symbol
            for submission in subreddit.search(symbol, time_filter='week', limit=limit):
                posts.append({
                    'post_id': submission.id,
                    'title': submission.title,
                    'content': submission.selftext[:500],  # Limit content length
                    'author': str(submission.author),
                    'score': submission.score,
                    'comments_count': submission.num_comments,
                    'posted_at': datetime.fromtimestamp(submission.created_utc).isoformat(),
                    'url': f"https://reddit.com{submission.permalink}"
                })
            
            return posts
            
        except Exception as e:
            print(f"Error fetching Reddit posts from r/{subreddit_name}: {e}")
            return []
    
    def get_reddit_sentiment_data(self, symbol: str) -> List[Dict]:
        """
        Get Reddit posts from multiple stock-related subreddits.
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Combined list of posts from multiple subreddits
        """
        subreddits = ['wallstreetbets', 'stocks', 'investing', 'stockmarket']
        all_posts = []
        
        for subreddit in subreddits:
            posts = self.get_reddit_posts(subreddit, symbol, limit=10)
            for post in posts:
                post['subreddit'] = subreddit
            all_posts.extend(posts)
            time.sleep(1)  # Rate limiting
        
        return all_posts
    
    def get_finnhub_sentiment(self, symbol: str) -> Optional[Dict]:
        """
        Get sentiment data from Finnhub.
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Sentiment data or None
        """
        if not self.finnhub_api_key:
            return None
        
        try:
            url = f"https://finnhub.io/api/v1/news-sentiment"
            params = {
                'symbol': symbol,
                'token': self.finnhub_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error fetching Finnhub sentiment for {symbol}: {e}")
            return None
    
    def get_market_overview(self) -> Dict:
        """
        Get general market overview data.
        
        Returns:
            Dictionary with market indices data
        """
        indices = {
            '^GSPC': 'S&P 500',
            '^DJI': 'Dow Jones',
            '^IXIC': 'NASDAQ',
            '^VIX': 'VIX'
        }
        
        market_data = {}
        
        for symbol, name in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='5d')
                
                if not hist.empty:
                    latest = hist.iloc[-1]
                    previous = hist.iloc[-2] if len(hist) > 1 else latest
                    
                    change = ((latest['Close'] - previous['Close']) / previous['Close']) * 100
                    
                    market_data[name] = {
                        'symbol': symbol,
                        'price': round(latest['Close'], 2),
                        'change_percent': round(change, 2)
                    }
            except Exception as e:
                print(f"Error fetching {name}: {e}")
        
        return market_data
