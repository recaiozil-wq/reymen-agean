FROM python:3.11-slim

WORKDIR /app

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıkları
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyaları
COPY . .

# Hatchling ile kurulum
RUN pip install --no-cache-dir -e .

# Port
EXPOSE 8080

# Varsayılan: web UI
CMD ["python", "-m", "src.reymen.web_ui"]
