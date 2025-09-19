#!/bin/bash

# Trading Simulation Workers Startup Script
# This script starts all background workers for the trading simulation

echo "Starting ZEBRAT TRADING background workers..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Function to start a worker in the background
start_worker() {
    local worker_name=$1
    local script_name=$2

    echo "Starting $worker_name..."
    nohup python $script_name > logs/${worker_name}.log 2>&1 &
    local pid=$!
    echo "$pid" > pids/${worker_name}.pid
    echo "$worker_name started with PID: $pid"
}

# Create directories for logs and PIDs
mkdir -p logs pids

echo "----------------------------------------"
echo "Starting all workers..."
echo "----------------------------------------"

# Start price worker (generates live price data)
start_worker "price_worker" "price_worker.py"

# Start market scheduler (manages market open/close)
start_worker "market_scheduler" "market_scheduler.py"

# Start candle aggregator (generates OHLC data)
start_worker "candle_aggregator" "candle_aggregator.py"

echo "----------------------------------------"
echo "All workers started successfully!"
echo ""
echo "To monitor workers:"
echo "  tail -f logs/price_worker.log"
echo "  tail -f logs/market_scheduler.log"
echo "  tail -f logs/candle_aggregator.log"
echo ""
echo "To stop all workers:"
echo "  ./stop_workers.sh"
echo "----------------------------------------"