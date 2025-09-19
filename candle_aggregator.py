#!/usr/bin/env python3
"""
Candle Aggregator Service

This service aggregates price tick data into candlestick (OHLC) data
at different time intervals for stock chart visualization.

Features:
- Configurable intervals (1h, 4h, 1d, etc.)
- Automatic aggregation from price ticks
- Handles multiple stocks simultaneously
- Backfill missing historical data
- Real-time candle updates
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Optional, Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Stock, PriceTick, CandleData


class CandleAggregator:
    def __init__(self):
        self.app = create_app()
        self.app_context = None

        # Configuration
        self.intervals = {
            '1h': 3600,    # 1 hour in seconds
            '4h': 14400,   # 4 hours in seconds
            '1d': 86400,   # 1 day in seconds
        }

        # How often to run aggregation (in seconds)
        self.aggregation_frequency = int(os.environ.get('CANDLE_AGGREGATION_FREQUENCY', '300'))  # 5 minutes default

        # Backfill days - how many days of historical data to process initially
        self.backfill_days = int(os.environ.get('CANDLE_BACKFILL_DAYS', '30'))

        self.running = False

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('CandleAggregator')

    def start(self):
        """Start the candle aggregation service"""
        self.logger.info("Starting Candle Aggregator Service...")
        self.running = True

        with self.app.app_context():
            try:
                # Initial backfill for all stocks
                self.backfill_historical_data()

                # Main aggregation loop
                while self.running:
                    self.process_all_stocks()
                    time.sleep(self.aggregation_frequency)

            except KeyboardInterrupt:
                self.logger.info("Received interrupt signal, stopping...")
                self.running = False
            except Exception as e:
                self.logger.error(f"Fatal error in aggregation service: {e}")
                raise

    def stop(self):
        """Stop the candle aggregation service"""
        self.running = False
        self.logger.info("Candle Aggregator Service stopped")

    def backfill_historical_data(self):
        """Backfill historical candle data for all stocks"""
        self.logger.info(f"Starting backfill of {self.backfill_days} days of historical data...")

        stocks = Stock.query.filter_by(is_active=True).all()
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=self.backfill_days)

        for stock in stocks:
            self.logger.info(f"Backfilling data for {stock.ticker}...")

            for interval, seconds in self.intervals.items():
                self.aggregate_interval_for_period(
                    stock_id=stock.id,
                    interval=interval,
                    interval_seconds=seconds,
                    start_time=start_time,
                    end_time=end_time,
                    is_backfill=True
                )

        self.logger.info("Historical data backfill completed")

    def process_all_stocks(self):
        """Process candle aggregation for all active stocks"""
        stocks = Stock.query.filter_by(is_active=True).all()

        for stock in stocks:
            try:
                self.process_stock_candles(stock.id)
            except Exception as e:
                self.logger.error(f"Error processing candles for stock {stock.ticker}: {e}")

    def process_stock_candles(self, stock_id: int):
        """Process candle aggregation for a specific stock"""
        for interval, seconds in self.intervals.items():
            try:
                self.aggregate_latest_candles(stock_id, interval, seconds)
            except Exception as e:
                self.logger.error(f"Error aggregating {interval} candles for stock {stock_id}: {e}")

    def aggregate_latest_candles(self, stock_id: int, interval: str, interval_seconds: int):
        """Aggregate the latest candles for a stock and interval"""

        # Get the latest candle for this stock/interval
        latest_candle = CandleData.get_latest_candle(stock_id, interval)

        # Determine the time range to aggregate
        now = datetime.now(timezone.utc)

        if latest_candle:
            # Start from the end of the latest candle
            start_time = latest_candle.timestamp_end
        else:
            # No existing candles, start from 24 hours ago
            start_time = now - timedelta(hours=24)

        # Aggregate from start_time to now
        self.aggregate_interval_for_period(
            stock_id=stock_id,
            interval=interval,
            interval_seconds=interval_seconds,
            start_time=start_time,
            end_time=now,
            is_backfill=False
        )

    def aggregate_interval_for_period(self, stock_id: int, interval: str, interval_seconds: int,
                                    start_time: datetime, end_time: datetime, is_backfill: bool = False):
        """Aggregate candles for a specific interval and time period"""

        current_time = self.round_to_interval(start_time, interval_seconds)

        while current_time < end_time:
            period_end = current_time + timedelta(seconds=interval_seconds)

            # Check if candle already exists (avoid duplicates)
            existing_candle = CandleData.query.filter_by(
                stock_id=stock_id,
                interval=interval,
                timestamp_start=current_time
            ).first()

            if not existing_candle:
                # Get price ticks for this period
                ticks = self.get_ticks_for_period(stock_id, current_time, period_end)

                if ticks:
                    # Create candle from ticks
                    candle = CandleData.create_candle_from_ticks(
                        stock_id=stock_id,
                        interval=interval,
                        start_time=current_time,
                        end_time=period_end,
                        price_ticks=ticks
                    )

                    if candle:
                        db.session.add(candle)

                        if not is_backfill:
                            self.logger.info(f"Created {interval} candle for stock {stock_id}: "
                                           f"OHLC({candle.open_price}, {candle.high_price}, "
                                           f"{candle.low_price}, {candle.close_price}) "
                                           f"Volume: {candle.volume}")

            current_time = period_end

        # Commit all candles for this period
        try:
            db.session.commit()
        except Exception as e:
            self.logger.error(f"Error committing candles for stock {stock_id}, interval {interval}: {e}")
            db.session.rollback()

    def get_ticks_for_period(self, stock_id: int, start_time: datetime, end_time: datetime) -> List[PriceTick]:
        """Get all price ticks for a stock within a time period"""
        return PriceTick.query.filter(
            PriceTick.stock_id == stock_id,
            PriceTick.timestamp >= start_time,
            PriceTick.timestamp < end_time
        ).order_by(PriceTick.timestamp.asc()).all()

    def round_to_interval(self, dt: datetime, interval_seconds: int) -> datetime:
        """Round datetime to the nearest interval boundary"""
        # Convert to timestamp, round down to interval, convert back
        timestamp = dt.timestamp()
        rounded_timestamp = (timestamp // interval_seconds) * interval_seconds
        return datetime.fromtimestamp(rounded_timestamp, tz=timezone.utc)

    def get_candles(self, stock_id: int, interval: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent candles for a stock (useful for API endpoints)"""
        candles = CandleData.query.filter_by(
            stock_id=stock_id,
            interval=interval
        ).order_by(CandleData.timestamp_start.desc()).limit(limit).all()

        return [{
            'timestamp': candle.timestamp_start.isoformat(),
            'open': float(candle.open_price),
            'high': float(candle.high_price),
            'low': float(candle.low_price),
            'close': float(candle.close_price),
            'volume': candle.volume
        } for candle in reversed(candles)]  # Reverse to get chronological order


def main():
    """Main entry point for the candle aggregator service"""
    aggregator = CandleAggregator()

    try:
        aggregator.start()
    except KeyboardInterrupt:
        aggregator.stop()
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()