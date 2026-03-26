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
COPY scripts/telegram_learner.py scripts/

# Create data directories the scripts expect
RUN mkdir -p 07-Analytics/signal-performance/signal-details \
             07-Analytics/polymarket \
             06-Drafts/polymarket \
             06-Drafts/trading

# Don't copy .env — use Railway env vars instead
# Set working dir so scripts/ imports work
ENV PYTHONPATH=/app/scripts
WORKDIR /app

CMD ["python", "scripts/polymarket_bot.py", "--run"]
