FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app.py .
COPY scripts/ ./scripts/

# Setup cron for weekly price scraper
RUN echo "0 18 * * 5 cd /app && python scripts/ngx_scraper.py >> /var/log/cron.log 2>&1" > /etc/cron.d/price-scraper
RUN chmod 0644 /etc/cron.d/price-scraper
RUN crontab /etc/cron.d/price-scraper
RUN touch /var/log/cron.log

# Expose Streamlit port
EXPOSE 8501

# Start cron and Streamlit
CMD service cron start && streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true
