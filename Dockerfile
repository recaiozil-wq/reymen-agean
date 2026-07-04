FROM python:3.11-slim

WORKDIR /app

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıkları
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Kaynak kod
COPY . .

# Hassas dosyaları temizle (kullanıcı kendi .env'ini oluştursun)
RUN rm -f .env token.txt 2>/dev/null; true

# Varsayılan ortam değişkenleri
ENV HERMES_HOME=/app
ENV PYTHONPATH=/app/src

# Entry point
CMD ["python", "-m", "reymen"]
