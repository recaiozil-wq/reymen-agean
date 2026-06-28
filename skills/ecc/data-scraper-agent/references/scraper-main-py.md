---
skill_id: 047f1cb594cd
usage_count: 1
last_used: 2026-06-16
---
# scraper/main.py
import os, sys, yaml
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from scraper.sources import my_source          # add your sources