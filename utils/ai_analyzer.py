"""
AI-powered analysis using OpenAI for pattern recognition and predictions.
"""
from openai import OpenAI
import json
from typing import List, Dict, Optional
import os
from datetime import datetime, timedelta


class AIAnalyzer:
    """AI-powered stock market analyzer."""
    
    def __init__(self):
        self.client = OpenAI()  # API key from environment
        self.model = "gpt-4.1-mini"  # Cost-effective model
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of a text using AI.
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with sentiment score and label
        """
        try:
            prompt = f"""Analyze the sentiment of the following text related to stock market/finance.
Return a JSON object with:
- sentiment_score: a number between -1 (very negative) and 1 (very positive)
- sentiment_label: one of "positive", "negative", or "neutral"
- key_points: list of key points that influenced the sentiment

Text: {text[:1000]}

Return only valid JSON, no other text."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial sentiment analysis expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if content.startswith('```'):
                content = content.split('\n', 1)[1]
                content = content.rsplit('\n```', 1)[0]
            result = json.loads(content)
            return result
            
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return {
                'sentiment_score': 0.0,
                'sentiment_label': 'neutral',
                'key_points': []
            }
    
    def find_correlations(self, instruments_data: List[Dict]) -> List[Dict]:
        """
        Find correlations between different instruments using AI pattern recognition.
        
        Args:
            instruments_data: List of instruments with their price history
        
        Returns:
            List of identified correlations
        """
        try:
            # Prepare data summary for AI
            data_summary = []
            for inst in instruments_data[:10]:  # Limit to avoid token limits
                symbol = inst['symbol']
                history = inst.get('history', [])
                
                if len(history) < 30:
                    continue
                
                # Calculate recent trend
                recent_prices = [h['close'] for h in history[-30:]]
                trend = "up" if recent_prices[-1] > recent_prices[0] else "down"
                change_pct = ((recent_prices[-1] - recent_prices[0]) / recent_prices[0]) * 100
                
                data_summary.append({
                    'symbol': symbol,
                    'trend': trend,
                    'change_percent': round(change_pct, 2),
                    'recent_high': round(max(recent_prices), 2),
                    'recent_low': round(min(recent_prices), 2)
                })
            
            prompt = f"""Analyze the following stock market data and identify potential correlations or inverse relationships between instruments.

Data: {json.dumps(data_summary, indent=2)}

Identify:
1. Instruments that tend to move in opposite directions (inverse correlation)
2. Instruments that tend to move together (positive correlation)
3. Any interesting patterns or relationships

Return a JSON array of correlations with this structure:
[
  {{
    "instrument1": "SYMBOL1",
    "instrument2": "SYMBOL2",
    "relationship": "inverse" or "positive",
    "strength": "strong", "moderate", or "weak",
    "explanation": "Brief explanation of the relationship"
  }}
]

Return only valid JSON, no other text."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in financial market analysis and pattern recognition."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            
            content = response.choices[0].message.content.strip()
            if content.startswith('```'):
                content = content.split('\n', 1)[1]
                content = content.rsplit('\n```', 1)[0]
            correlations = json.loads(content)
            return correlations
            
        except Exception as e:
            print(f"Error finding correlations: {e}")
            return []
    
    def generate_predictions(self, instrument: Dict, news: List[Dict], 
                           social_posts: List[Dict], market_context: Dict,
                           correlations: List[Dict]) -> Dict:
        """
        Generate prediction for an instrument using all available data.
        
        Args:
            instrument: Instrument data with price history
            news: Recent news items
            social_posts: Recent social media posts
            market_context: General market conditions
            correlations: Known correlations with other instruments
        
        Returns:
            Prediction dictionary
        """
        try:
            # Prepare context
            symbol = instrument['symbol']
            name = instrument.get('name', symbol)
            history = instrument.get('history', [])
            
            if len(history) < 30:
                return None
            
            # Recent price trend
            recent_prices = [h['close'] for h in history[-30:]]
            price_change = ((recent_prices[-1] - recent_prices[0]) / recent_prices[0]) * 100
            
            # Summarize news sentiment
            news_summary = []
            for item in news[:10]:
                news_summary.append({
                    'title': item.get('title', '')[:100],
                    'sentiment': item.get('sentiment_label', 'neutral')
                })
            
            # Summarize social sentiment
            social_summary = {
                'total_posts': len(social_posts),
                'avg_sentiment': sum([p.get('sentiment', 0) for p in social_posts]) / len(social_posts) if social_posts else 0,
                'high_engagement_posts': len([p for p in social_posts if p.get('score', 0) > 100])
            }
            
            # Relevant correlations
            relevant_corr = [c for c in correlations if symbol in [c.get('instrument1'), c.get('instrument2')]]
            
            prompt = f"""As an AI stock market analyst, predict the direction of {name} ({symbol}) for the next week.

Current Data:
- Recent 30-day price change: {price_change:.2f}%
- Current price: ${recent_prices[-1]:.2f}

Recent News (last 7 days):
{json.dumps(news_summary, indent=2)}

Social Media Sentiment:
{json.dumps(social_summary, indent=2)}

Market Context:
{json.dumps(market_context, indent=2)}

Known Correlations:
{json.dumps(relevant_corr, indent=2)}

Based on pattern recognition and the above data, provide a prediction with this JSON structure:
{{
  "direction": "up" or "down",
  "confidence": 0.0 to 1.0,
  "strategy": "momentum", "contrarian", "correlation", or "news_impact",
  "reasoning": "Detailed explanation of the prediction",
  "key_factors": ["list", "of", "key", "factors"],
  "risk_level": "low", "medium", or "high"
}}

Focus on:
1. Pattern recognition from news and social sentiment
2. Correlation effects from related instruments
3. Market context and overall trends
4. Contrarian opportunities (over-negative or over-positive sentiment)

Return only valid JSON, no other text."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert AI stock market analyst specializing in pattern recognition and sentiment analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6
            )
            
            content = response.choices[0].message.content.strip()
            if content.startswith('```'):
                content = content.split('\n', 1)[1]
                content = content.rsplit('\n```', 1)[0]
            prediction = json.loads(content)
            prediction['symbol'] = symbol
            prediction['name'] = name
            
            return prediction
            
        except Exception as e:
            print(f"Error generating prediction for {instrument.get('symbol')}: {e}")
            return None
    
    def evaluate_strategy_performance(self, predictions: List[Dict], 
                                     results: List[Dict]) -> Dict:
        """
        Evaluate which strategies are performing best.
        
        Args:
            predictions: List of predictions made
            results: List of actual results
        
        Returns:
            Strategy performance analysis
        """
        try:
            # Group by strategy
            strategy_stats = {}
            
            for pred, result in zip(predictions, results):
                strategy = pred.get('strategy', 'unknown')
                correct = result.get('correct', False)
                
                if strategy not in strategy_stats:
                    strategy_stats[strategy] = {'total': 0, 'correct': 0}
                
                strategy_stats[strategy]['total'] += 1
                if correct:
                    strategy_stats[strategy]['correct'] += 1
            
            # Calculate accuracy
            for strategy in strategy_stats:
                total = strategy_stats[strategy]['total']
                correct = strategy_stats[strategy]['correct']
                strategy_stats[strategy]['accuracy'] = (correct / total * 100) if total > 0 else 0
            
            prompt = f"""Analyze the performance of different trading strategies:

{json.dumps(strategy_stats, indent=2)}

Provide recommendations on:
1. Which strategies are working best
2. Which strategies should be adjusted or avoided
3. Potential improvements for underperforming strategies

Return a JSON object with:
{{
  "best_strategy": "strategy name",
  "worst_strategy": "strategy name",
  "recommendations": ["list", "of", "recommendations"],
  "market_condition_assessment": "current market conditions"
}}

Return only valid JSON, no other text."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in trading strategy optimization."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            
            content = response.choices[0].message.content.strip()
            if content.startswith('```'):
                content = content.split('\n', 1)[1]
                content = content.rsplit('\n```', 1)[0]
            analysis = json.loads(content)
            analysis['strategy_stats'] = strategy_stats
            
            return analysis
            
        except Exception as e:
            print(f"Error evaluating strategies: {e}")
            return {'strategy_stats': strategy_stats}
    
    def generate_market_insights(self, all_data: Dict) -> str:
        """
        Generate overall market insights and trends.
        
        Args:
            all_data: Dictionary with all collected data
        
        Returns:
            Market insights text
        """
        try:
            prompt = f"""Based on the following market data, provide key insights and trends:

{json.dumps(all_data, indent=2)[:3000]}

Provide:
1. Overall market sentiment
2. Key trends identified
3. Sectors showing strength/weakness
4. Important news themes affecting the market
5. Risk factors to watch

Write a concise analysis (3-4 paragraphs)."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial market analyst providing daily market insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating market insights: {e}")
            return "Unable to generate market insights at this time."
