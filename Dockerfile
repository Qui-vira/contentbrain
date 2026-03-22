FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot + scanner scripts
COPY scripts/polymarket_bot.py scripts/
COPY scripts/polymarket_cron.py scripts/
COPY scripts/polymarket_scanner.py scripts/
COPY scripts/polymarket_tracker.py scripts/
COPY scripts/claude_estimator.py scripts/
COPY scripts/binance_ta_runner.py scripts/
COPY scripts/forex_ta_runner.py scripts/
COPY scripts/market_data.py scripts/
COPY scripts/unified_auto_scanner.py scripts/

# Create data directories the scripts expect
RUN mkdir -p 07-Analytics/signal-performance \
             07-Analytics/polymarket \
             06-Drafts/polymarket

# Copy .env if present (for API keys)
COPY .env* ./

CMD ["python", "scripts/polymarket_bot.py", "--run"]
