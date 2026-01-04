"""
Database models and schema for the stock AI predictor.
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import json


class Database:
    """Handle all database operations."""
    
    def __init__(self, db_path: str = "data/stock_predictor.db"):
        self.db_path = db_path
        # Ensure the directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        self.init_database()
    
    def get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database with required tables."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Instruments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS instruments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                sector TEXT,
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Price history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instrument_id INTEGER NOT NULL,
                date DATE NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                FOREIGN KEY (instrument_id) REFERENCES instruments(id),
                UNIQUE(instrument_id, date)
            )
        """)
        
        # News items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instrument_id INTEGER,
                title TEXT NOT NULL,
                content TEXT,
                source TEXT,
                url TEXT,
                published_at TIMESTAMP,
                sentiment REAL,
                sentiment_label TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (instrument_id) REFERENCES instruments(id)
            )
        """)
        
        # Social media posts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS social_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instrument_id INTEGER,
                platform TEXT NOT NULL,
                post_id TEXT UNIQUE,
                content TEXT NOT NULL,
                author TEXT,
                score INTEGER,
                comments_count INTEGER,
                posted_at TIMESTAMP,
                sentiment REAL,
                sentiment_label TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (instrument_id) REFERENCES instruments(id)
            )
        """)
        
        # Predictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instrument_id INTEGER NOT NULL,
                prediction_date DATE NOT NULL,
                target_date DATE NOT NULL,
                direction TEXT NOT NULL,
                confidence REAL NOT NULL,
                reasoning TEXT,
                strategy TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (instrument_id) REFERENCES instruments(id)
            )
        """)
        
        # Results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_id INTEGER NOT NULL,
                actual_direction TEXT NOT NULL,
                correct BOOLEAN NOT NULL,
                price_change_percent REAL,
                evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prediction_id) REFERENCES predictions(id)
            )
        """)
        
        # Strategy performance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategy_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy TEXT NOT NULL,
                week_start DATE NOT NULL,
                total_predictions INTEGER DEFAULT 0,
                correct_predictions INTEGER DEFAULT 0,
                accuracy REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(strategy, week_start)
            )
        """)
        
        # Correlations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS correlations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instrument1_id INTEGER NOT NULL,
                instrument2_id INTEGER NOT NULL,
                correlation_value REAL NOT NULL,
                period_days INTEGER NOT NULL,
                calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (instrument1_id) REFERENCES instruments(id),
                FOREIGN KEY (instrument2_id) REFERENCES instruments(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_instrument(self, symbol: str, name: str, sector: str = None) -> int:
        """Add a new instrument to track."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO instruments (symbol, name, sector) VALUES (?, ?, ?)",
                (symbol, name, sector)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Instrument already exists
            cursor.execute("SELECT id FROM instruments WHERE symbol = ?", (symbol,))
            return cursor.fetchone()[0]
        finally:
            conn.close()
    
    def get_instruments(self, active_only: bool = True) -> List[Dict]:
        """Get all instruments."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT id, symbol, name, sector FROM instruments"
        if active_only:
            query += " WHERE active = 1"
        
        cursor.execute(query)
        instruments = []
        for row in cursor.fetchall():
            instruments.append({
                'id': row[0],
                'symbol': row[1],
                'name': row[2],
                'sector': row[3]
            })
        
        conn.close()
        return instruments
    
    def add_price_data(self, instrument_id: int, date: str, open_price: float,
                       high: float, low: float, close: float, volume: int):
        """Add price data for an instrument."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO price_history 
                (instrument_id, date, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (instrument_id, date, open_price, high, low, close, volume))
            conn.commit()
        except sqlite3.IntegrityError:
            # Update existing record
            cursor.execute("""
                UPDATE price_history 
                SET open=?, high=?, low=?, close=?, volume=?
                WHERE instrument_id=? AND date=?
            """, (open_price, high, low, close, volume, instrument_id, date))
            conn.commit()
        finally:
            conn.close()
    
    def get_price_history(self, instrument_id: int, days: int = 365) -> List[Dict]:
        """Get price history for an instrument."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT date, open, high, low, close, volume
            FROM price_history
            WHERE instrument_id = ?
            ORDER BY date DESC
            LIMIT ?
        """, (instrument_id, days))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'date': row[0],
                'open': row[1],
                'high': row[2],
                'low': row[3],
                'close': row[4],
                'volume': row[5]
            })
        
        conn.close()
        return history
    
    def add_news(self, instrument_id: Optional[int], title: str, content: str,
                 source: str, url: str, published_at: str, sentiment: float,
                 sentiment_label: str):
        """Add news item."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO news_items 
            (instrument_id, title, content, source, url, published_at, sentiment, sentiment_label)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (instrument_id, title, content, source, url, published_at, sentiment, sentiment_label))
        
        conn.commit()
        conn.close()
    
    def add_social_post(self, instrument_id: Optional[int], platform: str, post_id: str,
                       content: str, author: str, score: int, comments_count: int,
                       posted_at: str, sentiment: float, sentiment_label: str):
        """Add social media post."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO social_posts 
                (instrument_id, platform, post_id, content, author, score, 
                 comments_count, posted_at, sentiment, sentiment_label)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (instrument_id, platform, post_id, content, author, score,
                  comments_count, posted_at, sentiment, sentiment_label))
            conn.commit()
        except sqlite3.IntegrityError:
            pass  # Post already exists
        finally:
            conn.close()
    
    def add_prediction(self, instrument_id: int, prediction_date: str, target_date: str,
                      direction: str, confidence: float, reasoning: str, strategy: str) -> int:
        """Add a prediction."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO predictions 
            (instrument_id, prediction_date, target_date, direction, confidence, reasoning, strategy)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (instrument_id, prediction_date, target_date, direction, confidence, reasoning, strategy))
        
        conn.commit()
        prediction_id = cursor.lastrowid
        conn.close()
        return prediction_id
    
    def add_result(self, prediction_id: int, actual_direction: str, correct: bool,
                   price_change_percent: float):
        """Add evaluation result for a prediction."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO results 
            (prediction_id, actual_direction, correct, price_change_percent)
            VALUES (?, ?, ?, ?)
        """, (prediction_id, actual_direction, correct, price_change_percent))
        
        conn.commit()
        conn.close()
    
    def get_predictions(self, target_date: str = None, limit: int = 50) -> List[Dict]:
        """Get predictions."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT p.id, i.symbol, i.name, p.prediction_date, p.target_date,
                   p.direction, p.confidence, p.reasoning, p.strategy
            FROM predictions p
            JOIN instruments i ON p.instrument_id = i.id
        """
        
        params = []
        if target_date:
            query += " WHERE p.target_date = ?"
            params.append(target_date)
        
        query += " ORDER BY p.created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        predictions = []
        for row in cursor.fetchall():
            predictions.append({
                'id': row[0],
                'symbol': row[1],
                'name': row[2],
                'prediction_date': row[3],
                'target_date': row[4],
                'direction': row[5],
                'confidence': row[6],
                'reasoning': row[7],
                'strategy': row[8]
            })
        
        conn.close()
        return predictions
    
    def get_strategy_performance(self, weeks: int = 12) -> List[Dict]:
        """Get strategy performance statistics."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT strategy, week_start, total_predictions, correct_predictions, accuracy
            FROM strategy_performance
            ORDER BY week_start DESC
            LIMIT ?
        """, (weeks,))
        
        performance = []
        for row in cursor.fetchall():
            performance.append({
                'strategy': row[0],
                'week_start': row[1],
                'total_predictions': row[2],
                'correct_predictions': row[3],
                'accuracy': row[4]
            })
        
        conn.close()
        return performance
    
    def update_strategy_performance(self, strategy: str, week_start: str,
                                   total: int, correct: int):
        """Update strategy performance metrics."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        accuracy = (correct / total * 100) if total > 0 else 0.0
        
        cursor.execute("""
            INSERT INTO strategy_performance 
            (strategy, week_start, total_predictions, correct_predictions, accuracy)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(strategy, week_start) DO UPDATE SET
                total_predictions = ?,
                correct_predictions = ?,
                accuracy = ?
        """, (strategy, week_start, total, correct, accuracy, total, correct, accuracy))
        
        conn.commit()
        conn.close()
    
    def get_overall_accuracy(self) -> float:
        """Get overall prediction accuracy."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as total, SUM(CASE WHEN correct = 1 THEN 1 ELSE 0 END) as correct
            FROM results
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if row[0] > 0:
            return (row[1] / row[0]) * 100
        return 0.0
