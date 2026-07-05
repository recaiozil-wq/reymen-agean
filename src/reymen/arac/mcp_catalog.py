# -*- coding: utf-8 -*-
"""mcp_catalog.py â€” MCP Sunucu KataloÄŸu.

ReYMeN'teki MCP Catalog'un ReYMeN uyarlamasÄ±.
Ã–nceden tanÄ±mlÄ± MCP sunucularÄ±nÄ± listeler ve
tek komutla kurulum saÄŸlar.

ToolRegistry'e kayÄ±t için:
    TOOL_META = {...}
    def run(...)
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Optional

TOOL_META = {
    "ad": "mcp_catalog",
    "versiyon": "1.0.0",
    "aciklama": "Ã–nceden tanÄ±mlÄ± MCP sunucularÄ±nÄ± listeler ve kurar.",
    "kategori": "mcp",
    "parametreler": {
        "islem": {
            "tip": "str",
            "aciklama": "Ä°ÅŸlem: 'listele', 'kur', 'bilgi'",
            "zorunlu": True,
        },
        "sunucu_adi": {
            "tip": "str",
            "aciklama": "Kurulacak/bilgisi alÄ±nacak sunucu adÄ± (kur/bilgi için)",
            "zorunlu": False,
        },
    },
    "ornek": (
        'MCP_CATALOG(islem="listele")\n'
        'MCP_CATALOG(islem="kur", sunucu_adi="github")\n'
        'MCP_CATALOG(islem="bilgi", sunucu_adi="filesystem")'
    ),
}

# Katalog: ad -> kurulum bilgisi
KATALOG = {
    "github": {
        "adi": "GitHub MCP",
        "aciklama": "GitHub API: issue, PR, repo, dosya yönetimi",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/github",
    },
    "filesystem": {
        "adi": "Dosya Sistemi MCP",
        "aciklama": "Dosya okuma, yazma, listeleme, arama",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
        "env": {},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem",
    },
    "puppeteer": {
        "adi": "Puppeteer MCP",
        "aciklama": "TarayÄ±cÄ± otomasyonu: sayfa yükleme, ekran görüntüsü, JS çalÄ±ÅŸtÄ±rma",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
        "env": {},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/puppeteer",
    },
    "sqlite": {
        "adi": "SQLite MCP",
        "aciklama": "SQLite veritabanÄ±: sorgu, ÅŸema, tablo yönetimi",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-sqlite", "."],
        "env": {},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/sqlite",
    },
    "brave-search": {
        "adi": "Brave Search MCP",
        "aciklama": "Brave Search API ile web aramasÄ±",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-brave-search"],
        "env": {"BRAVE_API_KEY": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search",
    },
    "fetch": {
        "adi": "Web Fetch MCP",
        "aciklama": "Web sayfalarÄ±nÄ± indirme ve içerik çÄ±karma",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-fetch"],
        "env": {},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/fetch",
    },
    "sequential-thinking": {
        "adi": "SÄ±ralÄ± DüÅŸünme MCP",
        "aciklama": "KarmaÅŸÄ±k problemler için adÄ±m adÄ±m düÅŸünme zinciri",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
        "env": {},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/sequential-thinking",
    },
    "playwright": {
        "adi": "Playwright MCP",
        "aciklama": "TarayÄ±cÄ± otomasyonu: sayfa, tÄ±klama, form, ekran görüntüsü",
        "komut": "npx",
        "args": ["-y", "@playwright/mcp"],
        "env": {},
        "dokuman": "https://github.com/microsoft/playwright-mcp",
    },
    "browser-use": {
        "adi": "Browser Use",
        "aciklama": "AI destekli tarayÄ±cÄ± otomasyonu: görsel + DOM tabanlÄ±",
        "komut": "python",
        "args": ["-m", "browser_use"],
        "env": {},
        "dokuman": "https://github.com/browser-use/browser-use",
    },
    "memory": {
        "adi": "Memory MCP",
        "aciklama": "Bilgi grafiÄŸi tabanlÄ± kalÄ±cÄ± bellek yönetimi",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-memory"],
        "env": {},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/memory",
    },
    "postgres": {
        "adi": "PostgreSQL MCP",
        "aciklama": "PostgreSQL veritabanÄ±: sorgu, ÅŸema, tablo yönetimi",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-postgres"],
        "env": {"DATABASE_URL": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/postgres",
    },
    "redis": {
        "adi": "Redis MCP",
        "aciklama": "Redis önbellek: anahtar-deÄŸer iÅŸlemleri, pub/sub",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-redis"],
        "env": {"REDIS_URL": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/redis",
    },
    "docker": {
        "adi": "Docker MCP",
        "aciklama": "Docker konteyner yönetimi: container, image, compose",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-docker"],
        "env": {},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/docker",
    },
    "kubernetes": {
        "adi": "Kubernetes MCP",
        "aciklama": "Kubernetes küme yönetimi: pod, service, deployment",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-kubernetes"],
        "env": {"KUBECONFIG": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/kubernetes",
    },
    "aws": {
        "adi": "AWS MCP",
        "aciklama": "AWS kaynak yönetimi: S3, EC2, Lambda, DynamoDB",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-aws"],
        "env": {"AWS_ACCESS_KEY_ID": "", "AWS_SECRET_ACCESS_KEY": "", "AWS_REGION": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/aws",
    },
    "gcp": {
        "adi": "Google Cloud MCP",
        "aciklama": "GCP kaynak yönetimi: Storage, Compute, BigQuery",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-gcp"],
        "env": {"GOOGLE_APPLICATION_CREDENTIALS": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/gcp",
    },
    "azure": {
        "adi": "Azure MCP",
        "aciklama": "Azure kaynak yönetimi: Blob, VM, Functions",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-azure"],
        "env": {"AZURE_SUBSCRIPTION_ID": "", "AZURE_TENANT_ID": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/azure",
    },
    "jira": {
        "adi": "Jira MCP",
        "aciklama": "Jira issue, proje, sprint yönetimi",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-jira"],
        "env": {"JIRA_API_TOKEN": "", "JIRA_EMAIL": "", "JIRA_URL": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/jira",
    },
    "linear": {
        "adi": "Linear MCP",
        "aciklama": "Linear issue, proje, takvim yönetimi",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-linear"],
        "env": {"LINEAR_API_KEY": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/linear",
    },
    "notion": {
        "adi": "Notion MCP",
        "aciklama": "Notion sayfa, veritabanÄ±, arama yönetimi",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-notion"],
        "env": {"NOTION_API_KEY": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/notion",
    },
    "google-maps": {
        "adi": "Google Haritalar MCP",
        "aciklama": "Google Haritalar: yer arama, yön tarifi, mesafe",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-google-maps"],
        "env": {"GOOGLE_MAPS_API_KEY": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/google-maps",
    },
    "google-drive": {
        "adi": "Google Drive MCP",
        "aciklama": "Google Drive: dosya listeleme, okuma, yükleme",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-google-drive"],
        "env": {"GOOGLE_DRIVE_API_KEY": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/google-drive",
    },
    "gmail": {
        "adi": "Gmail MCP",
        "aciklama": "Gmail: okuma, gönderme, etiket yönetimi",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-gmail"],
        "env": {"GMAIL_API_KEY": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/gmail",
    },
    "slack": {
        "adi": "Slack MCP",
        "aciklama": "Slack: mesaj, kanal, dosya, arama yönetimi",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-slack"],
        "env": {"SLACK_BOT_TOKEN": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/slack",
    },
    "youtube": {
        "adi": "YouTube MCP",
        "aciklama": "YouTube: video arama, kanal bilgisi, transkript",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-youtube"],
        "env": {"YOUTUBE_API_KEY": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/youtube",
    },
    "spotify": {
        "adi": "Spotify MCP",
        "aciklama": "Spotify: çalma listesi, ÅŸarkÄ±, arama",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-spotify"],
        "env": {"SPOTIFY_CLIENT_ID": "", "SPOTIFY_CLIENT_SECRET": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/spotify",
    },
    "weather": {
        "adi": "Hava Durumu MCP",
        "aciklama": "Hava durumu: anlÄ±k, tahmin, konum tabanlÄ±",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-weather"],
        "env": {"WEATHER_API_KEY": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/weather",
    },
    "time": {
        "adi": "Zaman MCP",
        "aciklama": "Zaman: saat dilimi, tarih dönüÅŸümü, dünya saati",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-time"],
        "env": {},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/time",
    },
    "math": {
        "adi": "Matematik MCP",
        "aciklama": "Matematik: hesaplama, dönüÅŸüm, istatistik",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-math"],
        "env": {},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/math",
    },
    "arxiv": {
        "adi": "ArXiv MCP",
        "aciklama": "ArXiv: makale arama, özet, PDF indirme",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-arxiv"],
        "env": {},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/arxiv",
    },
    "wikipedia": {
        "adi": "Wikipedia MCP",
        "aciklama": "Wikipedia: madde arama, özet, kategori",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-wikipedia"],
        "env": {},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/wikipedia",
    },
    "exa-search": {
        "adi": "Exa Search MCP",
        "aciklama": "Exa (eski adÄ±yla Metaphor) ile semantik web aramasÄ±",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-exa-search"],
        "env": {"EXA_API_KEY": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/exa-search",
    },
    "firecrawl": {
        "adi": "Firecrawl MCP",
        "aciklama": "Web scraping: sayfa içeriÄŸi çÄ±karma, tarama, dönüÅŸtürme",
        "komut": "npx",
        "args": ["-y", "firecrawl-mcp"],
        "env": {"FIRECRAWL_API_KEY": ""},
        "dokuman": "https://github.com/firecrawl/firecrawl-mcp",
    },
    "stripe": {
        "adi": "Stripe MCP",
        "aciklama": "Stripe: ödeme, abonelik, fatura, müÅŸteri yönetimi",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-stripe"],
        "env": {"STRIPE_SECRET_KEY": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/stripe",
    },
    "sentry": {
        "adi": "Sentry MCP",
        "aciklama": "Sentry: hata izleme, performans, issue yönetimi",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-sentry"],
        "env": {"SENTRY_AUTH_TOKEN": "", "SENTRY_ORG": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/sentry",
    },
    "cloudflare": {
        "adi": "Cloudflare MCP",
        "aciklama": "Cloudflare: DNS, Worker, KV, R2, Cache yönetimi",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-cloudflare"],
        "env": {"CLOUDFLARE_API_TOKEN": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/cloudflare",
    },
    "vercel": {
        "adi": "Vercel MCP",
        "aciklama": "Vercel: deployment, domain, environment, log",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-vercel"],
        "env": {"VERCEL_TOKEN": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/vercel",
    },
    "netlify": {
        "adi": "Netlify MCP",
        "aciklama": "Netlify: site, deploy, fonksiyon, form yönetimi",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-netlify"],
        "env": {"NETLIFY_AUTH_TOKEN": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/netlify",
    },
    "figma": {
        "adi": "Figma MCP",
        "aciklama": "Figma: dosya, component, frame, varlÄ±k yönetimi",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-figma"],
        "env": {"FIGMA_ACCESS_TOKEN": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/figma",
    },
    "openai": {
        "adi": "OpenAI MCP",
        "aciklama": "OpenAI: model çaÄŸrÄ±sÄ±, embedding, dosya, asistan",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-openai"],
        "env": {"OPENAI_API_KEY": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/openai",
    },
    "anthropic": {
        "adi": "Anthropic MCP",
        "aciklama": "Anthropic: Claude modeli, mesajlaÅŸma, dosya yükleme",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-anthropic"],
        "env": {"ANTHROPIC_API_KEY": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/anthropic",
    },
    "perplexity": {
        "adi": "Perplexity MCP",
        "aciklama": "Perplexity AI: web tabanlÄ± araÅŸtÄ±rma, kaynaklÄ± cevap",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-perplexity"],
        "env": {"PERPLEXITY_API_KEY": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/perplexity",
    },
    "wolfram-alpha": {
        "adi": "Wolfram Alpha MCP",
        "aciklama": "Wolfram Alpha: hesaplama, veri, grafik, bilgi",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-wolfram-alpha"],
        "env": {"WOLFRAM_ALPHA_API_KEY": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/wolfram-alpha",
    },
    "elevenlabs": {
        "adi": "ElevenLabs MCP",
        "aciklama": "ElevenLabs: metin-konuÅŸma, ses klonlama, efekt",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-elevenlabs"],
        "env": {"ELEVENLABS_API_KEY": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/elevenlabs",
    },
    "apify": {
        "adi": "Apify MCP",
        "aciklama": "Apify: web kazÄ±ma, actor çalÄ±ÅŸtÄ±rma, veri depolama",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-apify"],
        "env": {"APIFY_API_KEY": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/apify",
    },
    "tavily": {
        "adi": "Tavily MCP",
        "aciklama": "Tavily: AI odaklÄ± web arama, haber, analiz",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-tavily"],
        "env": {"TAVILY_API_KEY": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/tavily",
    },
    "datadog": {
        "adi": "Datadog MCP",
        "aciklama": "Datadog: metrik, log, trace, monitor, dashboard",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-datadog"],
        "env": {"DATADOG_API_KEY": "", "DATADOG_APP_KEY": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/datadog",
    },
    "s3": {
        "adi": "S3 MCP",
        "aciklama": "Amazon S3: bucket, dosya yükleme/indirme/silme",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-s3"],
        "env": {"AWS_ACCESS_KEY_ID": "", "AWS_SECRET_ACCESS_KEY": "", "AWS_REGION": "", "S3_BUCKET": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/s3",
    },
    "elasticsearch": {
        "adi": "Elasticsearch MCP",
        "aciklama": "Elasticsearch: indeks, arama, belge yönetimi",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-elasticsearch"],
        "env": {"ELASTICSEARCH_URL": "", "ELASTICSEARCH_API_KEY": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/elasticsearch",
    },
    "grafana": {
        "adi": "Grafana MCP",
        "aciklama": "Grafana: dashboard, panel, veri kaynaÄŸÄ±, alert",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-grafana"],
        "env": {"GRAFANA_API_KEY": "", "GRAFANA_URL": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/grafana",
    },
    "prometheus": {
        "adi": "Prometheus MCP",
        "aciklama": "Prometheus: metrik sorgu, alert, hedef yönetimi",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-prometheus"],
        "env": {"PROMETHEUS_URL": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/prometheus",
    },
    "kafka": {
        "adi": "Kafka MCP",
        "aciklama": "Kafka: topic, mesaj gönderme/alma, consumer grup",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-kafka"],
        "env": {"KAFKA_BROKERS": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/kafka",
    },
    "rabbitmq": {
        "adi": "RabbitMQ MCP",
        "aciklama": "RabbitMQ: kuyruk, exchange, binding yönetimi",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-rabbitmq"],
        "env": {"RABBITMQ_URL": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/rabbitmq",
    },
    "nginx": {
        "adi": "Nginx MCP",
        "aciklama": "Nginx: config, server block, SSL, log analizi",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-nginx"],
        "env": {},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/nginx",
    },
    "pm2": {
        "adi": "PM2 MCP",
        "aciklama": "PM2: process yönetimi, log, monitör, restart",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-pm2"],
        "env": {},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/pm2",
    },
    "git": {
        "adi": "Git MCP",
        "aciklama": "Git: commit, branch, diff, log, merge, push",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-git"],
        "env": {},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/git",
    },
    "svn": {
        "adi": "SVN MCP",
        "aciklama": "Subversion: checkout, commit, diff, log yönetimi",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-svn"],
        "env": {},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/svn",
    },
    "cron": {
        "adi": "Cron MCP",
        "aciklama": "Cron: iÅŸ zamanlama, tetikleme, log görüntüleme",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-cron"],
        "env": {},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/cron",
    },
    "websocket": {
        "adi": "WebSocket MCP",
        "aciklama": "WebSocket: baÄŸlantÄ± yönetimi, mesaj alÄ±ÅŸveriÅŸi",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-websocket"],
        "env": {},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/websocket",
    },
    "mqtt": {
        "adi": "MQTT MCP",
        "aciklama": "MQTT: topic, publish, subscribe, broker yönetimi",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-mqtt"],
        "env": {"MQTT_BROKER_URL": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/mqtt",
    },
    "pdf": {
        "adi": "PDF MCP",
        "aciklama": "PDF: oluÅŸturma, birleÅŸtirme, dönüÅŸtürme, metin çÄ±karma",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-pdf"],
        "env": {},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/pdf",
    },
    "csv": {
        "adi": "CSV MCP",
        "aciklama": "CSV: okuma, dönüÅŸtürme, sorgulama, analiz",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-csv"],
        "env": {},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/csv",
    },
    "excel": {
        "adi": "Excel MCP",
        "aciklama": "Excel: .xlsx okuma, yazma, formül, grafik",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-excel"],
        "env": {},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/excel",
    },
    "wordpress": {
        "adi": "WordPress MCP",
        "aciklama": "WordPress: yazÄ±, sayfa, medya, kullanÄ±cÄ± yönetimi",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-wordpress"],
        "env": {"WORDPRESS_URL": "", "WORDPRESS_APP_PASSWORD": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/wordpress",
    },
    "shopify": {
        "adi": "Shopify MCP",
        "aciklama": "Shopify: ürün, sipariÅŸ, müÅŸteri, envanter yönetimi",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-shopify"],
        "env": {"SHOPIFY_ACCESS_TOKEN": "", "SHOPIFY_STORE_URL": ""},
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/shopify",
    },
}


def _katalog_yolu() -> Path:
    """Katalog dosyasÄ±nÄ±n yolu."""
    return Path.cwd() / ".ReYMeN" / "mcp_catalog.json"


def _katalog_kaydet():
    """Katalog durumunu JSON'a kaydet (hangi sunucular kuruldu vs)."""
    dosya = _katalog_yolu()
    durum = {
        s["adi"]: {"kurulu": False, "env_var": list(s.get("env", {}).keys())}
        for s in KATALOG.values()
    }
    dosya.parent.mkdir(parents=True, exist_ok=True)
    dosya.write_text(json.dumps(durum, ensure_ascii=False, indent=2), encoding="utf-8")


def listele() -> str:
    """Katalogdaki tüm MCP sunucularÄ±nÄ± listele."""
    satirlar = ["ğŸ“¦ MCP Sunucu KataloÄŸu", "=" * 40, ""]

    for ad, bilgi in KATALOG.items():
        env_str = ""
        if bilgi.get("env"):
            gerekli = [f"${k}" for k in bilgi["env"].keys()]
            env_str = f" ğŸ”‘ {', '.join(gerekli)}"

        satirlar.append(f"  {ad}")
        satirlar.append(f"    {bilgi['adi']}: {bilgi['aciklama']}{env_str}")
        satirlar.append("")

    satirlar.append(f"Toplam: {len(KATALOG)} sunucu")
    satirlar.append("KullanÄ±m: MCP_CATALOG(islem='kur', sunucu_adi='github')")
    return "\n".join(satirlar)


def bilgi(sunucu_adi: str) -> str:
    """Belirli bir MCP sunucusu hakkÄ±nda detaylÄ± bilgi."""
    if sunucu_adi not in KATALOG:
        mevcut = ", ".join(KATALOG.keys())
        return f"[MCP_CATALOG] '{sunucu_adi}' bulunamadÄ±. Mevcut: {mevcut}"

    bilgi = KATALOG[sunucu_adi]
    satirlar = [
        f"ğŸ“– {bilgi['adi']}",
        f"  AçÄ±klama: {bilgi['aciklama']}",
        f"  Komut: {bilgi['komut']} {' '.join(bilgi['args'])}",
    ]

    if bilgi.get("env"):
        satirlar.append(f"  Gerekli env: {', '.join(bilgi['env'].keys())}")
    if bilgi.get("dokuman"):
        satirlar.append(f"  Doküman: {bilgi['dokuman']}")

    # Config'de var mÄ± kontrol et
    config_yolu = Path.cwd() / "config.yaml"
    if config_yolu.exists():
        cfg = config_yolu.read_text(encoding="utf-8")
        if f"mcp_servers:" in cfg and sunucu_adi in cfg:
            satirlar.append(f"  Durum: âš™ï¸ config.yaml'da tanÄ±mlÄ±")

    return "\n".join(satirlar)


def _config_ekle(sunucu_adi: str) -> bool:
    """Sunucuyu config.yaml'a MCP sunucusu olarak ekle."""
    bilgi = KATALOG.get(sunucu_adi)
    if not bilgi:
        return False

    config_yolu = Path.cwd() / "config.yaml"
    yaml_ek = (
        f"\n  {sunucu_adi}:\n"
        f"    command: {bilgi['komut']}\n"
        f"    args: {json.dumps(bilgi['args'])}\n"
    )
    if bilgi.get("env"):
        env_yaml = "\n".join(f'      {k}: "${{{k}}}"' for k in bilgi["env"])
        yaml_ek += f"    env:\n{env_yaml}\n"

    try:
        if config_yolu.exists():
            icerik = config_yolu.read_text(encoding="utf-8")
            if "mcp_servers:" not in icerik:
                icerik += "\n\n# MCP Sunuculari\nmcp_servers:\n"
            icerik += yaml_ek
            config_yolu.write_text(icerik, encoding="utf-8")
            return True
        else:
            config_yolu.write_text(
                "# ReYMeN YapÄ±landÄ±rma\n\nmcp_servers:\n" + yaml_ek,
                encoding="utf-8",
            )
            return True
    except Exception:
        return False


def kur(sunucu_adi: str) -> str:
    """MCP sunucusunu kur (config'e ekle)."""
    if sunucu_adi not in KATALOG:
        mevcut = ", ".join(KATALOG.keys())
        return f"[MCP_CATALOG] '{sunucu_adi}' bulunamadÄ±. Mevcut: {mevcut}"

    bilgi = KATALOG[sunucu_adi]

    # Env kontrol
    env_eksik = []
    for env_key in bilgi.get("env", {}):
        if not os.environ.get(env_key):
            env_eksik.append(env_key)

    # Config'e ekle
    if _config_ekle(sunucu_adi):
        satirlar = [f"âœ… {bilgi['adi']} config.yaml'a eklendi."]
        if env_eksik:
            satirlar.append(f"âš ï¸  Eksik env: {', '.join(env_eksik)}")
            satirlar.append(f"   .env dosyasÄ±na ekleyin.")
        satirlar.append(f"   Kullanmak için motor'u yeniden baÅŸlatÄ±n.")
        return "\n".join(satirlar)
    else:
        return f"[MCP_CATALOG] {bilgi['adi']} eklenemedi."


def run(islem: str, sunucu_adi: str = "") -> str:
    """MCP kataloÄŸunu yönet.

    Args:
        islem: 'listele', 'kur', 'bilgi'
        sunucu_adi: Ä°ÅŸlem yapÄ±lacak sunucu adÄ±

    Returns:
        str: Ä°ÅŸlem sonucu
    """
    islem = islem.strip().lower()

    if islem == "listele":
        _katalog_kaydet()
        return listele()
    elif islem == "bilgi":
        if not sunucu_adi:
            return "[MCP_CATALOG] 'bilgi' için 'sunucu_adi' gerekli."
        return bilgi(sunucu_adi)
    elif islem == "kur":
        if not sunucu_adi:
            return "[MCP_CATALOG] 'kur' için 'sunucu_adi' gerekli."
        return kur(sunucu_adi)
    else:
        return f"[MCP_CATALOG] Bilinmeyen iÅŸlem: '{islem}'. Åunlar: listele, kur, bilgi"


def check_fn(parametreler: dict) -> tuple:
    """DoÄŸrulama: islem parametresi zorunlu."""
    if not parametreler.get("islem"):
        return False, "MCP_CATALOG: 'islem' parametresi zorunludur"
    return True, ""


# KÄ±sa kullanÄ±m alias
MCP_CATALOG = run
