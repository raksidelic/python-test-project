# config.py:

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # --- ORTAM AYARLARI ---
    ENV = os.getenv("ENV", "STAGE").upper() # STAGE veya PROD
    BASE_URL = os.getenv("BASE_URL", "https://www.saucedemo.com")
    TIMEOUT = int(os.getenv("TIMEOUT", 10))
    
    # --- TEST KOŞUM AYARLARI ---
    # Tarayıcı veya Platform seçimi: chrome, firefox, android_app, ios_app
    BROWSER = os.getenv("BROWSER", "chrome").lower()
    HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
    
    # --- VIDEO KAYIT AYARLARI (YENİ) ---
    # Seçenekler: 'true' (her zaman), 'false' (hiçbir zaman), 'on_failure' (sadece hatalar)
    RECORD_VIDEO = os.getenv("RECORD_VIDEO", "on_failure").lower()

    # --- SELENOID / GRID AYARLARI ---
    SELENIUM_REMOTE_URL = os.getenv("SELENIUM_REMOTE_URL") # Örn: http://localhost:4444/wd/hub
    
    # --- DATABASE: NOSQL (ARANGO) ---
    ARANGO_URL = os.getenv("ARANGO_URL", "http://localhost:8529")
    ARANGO_DB = os.getenv("ARANGO_DB_NAME", "_system")
    ARANGO_USER = os.getenv("ARANGO_USER", "root")
    ARANGO_PASS = os.getenv("ARANGO_PASSWORD", "")
    
    # --- DATABASE: SQL (POSTGRESQL - Gelecek için Hazırlık) ---
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASSWORD")

    @staticmethod
    def is_remote():
        """Testlerin Selenoid üzerinde mi yoksa lokalde mi koştuğunu belirler."""
        return Config.SELENIUM_REMOTE_URL is not None