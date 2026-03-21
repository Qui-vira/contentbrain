FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the polymarket scripts
COPY scripts/polymarket_bot.py scripts/
COPY scripts/polymarket_cron.py scripts/
COPY scripts/polymarket_scanner.py scripts/
COPY scripts/polymarket_tracker.py scripts/

# Create data directories the scripts expect
RUN mkdir -p 07-Analytics/signal-performance \
             07-Analytics/polymarket \
             06-Drafts/polymarket

CMD ["python", "scripts/polymarket_bot.py", "--run"]
