"""
Evaluation script - Run this to evaluate past predictions against actual results.
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import Database
from utils.data_collector import DataCollector


def main():
    """Evaluate predictions against actual results."""
    print(f"Starting prediction evaluation - {datetime.now()}")
    
    # Initialize components
    db = Database()
    collector = DataCollector()
    
    # Get predictions that need evaluation (target_date has passed)
    today = datetime.now().strftime('%Y-%m-%d')
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Find predictions that haven't been evaluated yet
    cursor.execute("""
        SELECT p.id, p.instrument_id, i.symbol, p.target_date, p.direction, p.strategy
        FROM predictions p
        JOIN instruments i ON p.instrument_id = i.id
        LEFT JOIN results r ON p.id = r.prediction_id
        WHERE p.target_date <= ?
        AND r.id IS NULL
        ORDER BY p.target_date DESC
    """, (today,))
    
    predictions_to_evaluate = cursor.fetchall()
    conn.close()
    
    if not predictions_to_evaluate:
        print("No predictions to evaluate.")
        return
    
    print(f"Found {len(predictions_to_evaluate)} predictions to evaluate")
    
    evaluated_count = 0
    strategy_results = {}
    
    for pred in predictions_to_evaluate:
        pred_id, inst_id, symbol, target_date, predicted_direction, strategy = pred
        
        print(f"\nEvaluating prediction for {symbol} (target: {target_date})")
        
        # Get price data around target date
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get price before target date
        cursor.execute("""
            SELECT close FROM price_history
            WHERE instrument_id = ?
            AND date < ?
            ORDER BY date DESC
            LIMIT 1
        """, (inst_id, target_date))
        
        before_price_row = cursor.fetchone()
        
        # Get price at or after target date
        cursor.execute("""
            SELECT close FROM price_history
            WHERE instrument_id = ?
            AND date >= ?
            ORDER BY date ASC
            LIMIT 1
        """, (inst_id, target_date))
        
        after_price_row = cursor.fetchone()
        conn.close()
        
        if not before_price_row or not after_price_row:
            print(f"  ✗ Missing price data for evaluation")
            continue
        
        before_price = before_price_row[0]
        after_price = after_price_row[0]
        
        # Calculate actual direction
        price_change_percent = ((after_price - before_price) / before_price) * 100
        
        # Determine actual direction (threshold of 0.5% to avoid noise)
        if price_change_percent > 0.5:
            actual_direction = 'up'
        elif price_change_percent < -0.5:
            actual_direction = 'down'
        else:
            actual_direction = 'neutral'
        
        # Check if prediction was correct
        correct = (predicted_direction == actual_direction)
        
        # Save result
        db.add_result(pred_id, actual_direction, correct, price_change_percent)
        
        evaluated_count += 1
        
        # Track strategy performance
        if strategy not in strategy_results:
            strategy_results[strategy] = {'total': 0, 'correct': 0}
        
        strategy_results[strategy]['total'] += 1
        if correct:
            strategy_results[strategy]['correct'] += 1
        
        result_icon = "✓" if correct else "✗"
        print(f"  {result_icon} Predicted: {predicted_direction}, Actual: {actual_direction}")
        print(f"    Price change: {price_change_percent:+.2f}%")
        print(f"    Strategy: {strategy}")
    
    # Update strategy performance in database
    print("\n=== Updating Strategy Performance ===")
    
    # Get week start for grouping
    week_start = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    for strategy, results in strategy_results.items():
        db.update_strategy_performance(
            strategy,
            week_start,
            results['total'],
            results['correct']
        )
        
        accuracy = (results['correct'] / results['total'] * 100) if results['total'] > 0 else 0
        print(f"{strategy}: {results['correct']}/{results['total']} = {accuracy:.1f}%")
    
    # Calculate overall accuracy
    overall_accuracy = db.get_overall_accuracy()
    
    print(f"\n=== Evaluation Complete ===")
    print(f"Evaluated {evaluated_count} predictions")
    print(f"Overall accuracy: {overall_accuracy:.1f}%")
    print(f"Finished at {datetime.now()}")


if __name__ == "__main__":
    main()
