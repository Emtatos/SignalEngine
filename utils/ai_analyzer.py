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
            prompt = f"""Analysera sentimentet i följande text relaterad till aktiemarknaden/finans.
Svara med ett JSON-objekt som innehåller:
- sentiment_score: ett tal mellan -1 (mycket negativt) och 1 (mycket positivt)
- sentiment_label: en av "positive", "negative", eller "neutral"
- key_points: lista över nyckelpunkter som påverkade sentimentet (på svenska)

Text: {text[:1000]}

Svara endast med giltig JSON, ingen annan text."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Du är en expert på finansiell sentimentanalys."},
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
                trend = "upp" if recent_prices[-1] > recent_prices[0] else "ner"
                change_pct = ((recent_prices[-1] - recent_prices[0]) / recent_prices[0]) * 100
                
                data_summary.append({
                    'symbol': symbol,
                    'trend': trend,
                    'change_percent': round(change_pct, 2),
                    'recent_high': round(max(recent_prices), 2),
                    'recent_low': round(min(recent_prices), 2)
                })
            
            prompt = f"""Analysera följande marknadsdata och identifiera potentiella korrelationer eller inversa förhållanden mellan instrumenten.

Data: {json.dumps(data_summary, indent=2)}

Identifiera:
1. Instrument som tenderar att röra sig i motsatta riktningar (invers korrelation)
2. Instrument som tenderar att röra sig tillsammans (positiv korrelation)
3. Intressanta mönster eller förhållanden

Svara med en JSON-array av korrelationer med denna struktur:
[
  {{
    "instrument1": "SYMBOL1",
    "instrument2": "SYMBOL2",
    "relationship": "inverse" eller "positive",
    "strength": "strong", "moderate", eller "weak",
    "explanation": "Kort förklaring av förhållandet på svenska"
  }}
]

Svara endast med giltig JSON, ingen annan text."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Du är expert på finansiell marknadsanalys och mönsterigenkänning."},
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
            
            prompt = f"""Som en AI-aktieanalytiker, förutspå riktningen för {name} ({symbol}) för den kommande veckan.

Aktuell Data:
- Prisförändring senaste 30 dagarna: {price_change:.2f}%
- Aktuellt pris: ${recent_prices[-1]:.2f}

Senaste nyheterna (senaste 7 dagarna):
{json.dumps(news_summary, indent=2)}

Sentiment i sociala medier:
{json.dumps(social_summary, indent=2)}

Marknadskontext:
{json.dumps(market_context, indent=2)}

Kända korrelationer:
{json.dumps(relevant_corr, indent=2)}

Baserat på mönsterigenkänning och ovanstående data, ge en prediktion med denna JSON-struktur:
{{
  "direction": "up" eller "down",
  "confidence": 0.0 till 1.0,
  "strategy": "momentum", "contrarian", "correlation", eller "news_impact",
  "reasoning": "Detaljerad förklaring av prediktionen på svenska",
  "key_factors": ["lista", "över", "viktiga", "faktorer", "på", "svenska"],
  "risk_level": "low", "medium", eller "high"
}}

Fokusera på:
1. Mönsterigenkänning från nyheter och socialt sentiment
2. Korrelationseffekter från relaterade instrument
3. Marknadskontext och övergripande trender
4. Contrarian-möjligheter (över-negativt eller över-positivt sentiment)

Svara endast med giltig JSON, ingen annan text."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Du är en expert AI-aktieanalytiker specialiserad på mönsterigenkänning och sentimentanalys."},
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
            
            prompt = f"""Analysera prestandan för olika handelsstrategier:

{json.dumps(strategy_stats, indent=2)}

Ge rekommendationer om:
1. Vilka strategier som fungerar bäst
2. Vilka strategier som bör justeras eller undvikas
3. Potentiella förbättringar för strategier med låg prestanda

Svara med ett JSON-objekt som innehåller:
{{
  "best_strategy": "strateginamn",
  "worst_strategy": "strateginamn",
  "recommendations": ["lista", "över", "rekommendationer", "på", "svenska"],
  "market_condition_assessment": "bedömning av aktuella marknadsförhållanden på svenska"
}}

Svara endast med giltig JSON, ingen annan text."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Du är expert på optimering av handelsstrategier."},
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
            prompt = f"""Baserat på följande marknadsdata, ge viktiga insikter och trender:

{json.dumps(all_data, indent=2)[:3000]}

Ge:
1. Övergripande marknadssentiment
2. Identifierade huvudtrender
3. Sektorer som visar styrka/svaghet
4. Viktiga nyhetsteman som påverkar marknaden
5. Riskfaktorer att hålla koll på

Skriv en kortfattad analys på svenska (3-4 stycken)."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Du är en finansiell marknadsanalytiker som ger dagliga marknadsinsikter på svenska."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating market insights: {e}")
            return "Kunde inte generera marknadsinsikter för tillfället."
