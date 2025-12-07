import os
from dotenv import load_dotenv

# .env yüklenir
load_dotenv()

class Config:
    BASE_URL = os.getenv("BASE_URL")
    USERNAME = os.getenv("APP_USERNAME")
    PASSWORD = os.getenv("APP_PASSWORD")
    BROWSER = os.getenv("BROWSER", "chrome")
    TIMEOUT = int(os.getenv("TIMEOUT", 10))

    if not BASE_URL or not USERNAME or not PASSWORD:
        raise ValueError("KRITIK HATA: .env dosyasında eksik veri var!")