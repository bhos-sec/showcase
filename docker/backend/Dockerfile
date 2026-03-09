# Development Dockerfile for the Django backend.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.local

WORKDIR /app

# Install system dependencies (including Playwright/Chromium requirements).
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libatspi2.0-0 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libfreetype6 \
    libgbm1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    libxkbcommon0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies.
COPY backend/requirements/ /app/requirements/
RUN pip install --no-cache-dir -r requirements/local.txt

# Install Playwright browser binaries.
RUN playwright install chromium

# Copy application code.
COPY backend/ /app/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
