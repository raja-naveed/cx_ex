#!/bin/bash

# Trading Simulation Workers Stop Script
# This script stops all background workers

echo "Stopping ZEBRAT TRADING background workers..."

# Function to stop a worker
stop_worker() {
    local worker_name=$1
    local pid_file="pids/${worker_name}.pid"

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        echo "Stopping $worker_name (PID: $pid)..."

        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            sleep 2

            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                echo "Force killing $worker_name..."
                kill -9 "$pid"
            fi

            echo "$worker_name stopped"
        else
            echo "$worker_name was not running"
        fi

        rm -f "$pid_file"
    else
        echo "No PID file found for $worker_name"
    fi
}

echo "----------------------------------------"
echo "Stopping all workers..."
echo "----------------------------------------"

# Stop all workers
stop_worker "price_worker"
stop_worker "market_scheduler"
stop_worker "candle_aggregator"

# Clean up any remaining processes
echo "Cleaning up any remaining processes..."
pkill -f "price_worker.py" 2>/dev/null || true
pkill -f "market_scheduler.py" 2>/dev/null || true
pkill -f "candle_aggregator.py" 2>/dev/null || true

echo "----------------------------------------"
echo "All workers stopped!"
echo "----------------------------------------"