import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # --- ENVIRONMENT SETTINGS ---
    ENV = os.getenv("ENV", "STAGE").upper()
    BASE_URL = os.getenv("BASE_URL", "https://www.saucedemo.com")
    TIMEOUT = int(os.getenv("TIMEOUT", 10))

    # --- PLATFORM SELECTION ---
    # Options: 'web' (default), 'android', 'ios'
    PLATFORM_NAME = os.getenv("PLATFORM_NAME", "web").lower()
    
    # --- WEB TEST RUN SETTINGS ---
    BROWSER = os.getenv("BROWSER", "chrome").lower()
    HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"

    # --- MOBILE SETTINGS ---
    MOBILE_APP_PATH = os.getenv("MOBILE_APP_PATH")
    MOBILE_DEVICE_NAME = os.getenv("MOBILE_DEVICE_NAME", "Android Emulator")
    MOBILE_REMOTE_URL = os.getenv("MOBILE_REMOTE_URL") # Appium/Selenoid URL

    # --- SELENOID SETTINGS ---
    RECORD_VIDEO = os.getenv("RECORD_VIDEO", "on_failure").lower()
    SELENIUM_REMOTE_URL = os.getenv("SELENIUM_REMOTE_URL")
    
    # --- DATABASE: NoSQL (ARANGO) ---
    ARANGO_URL = os.getenv("ARANGO_URL", "http://localhost:8529")
    ARANGO_DB = os.getenv("ARANGO_DB_NAME", "_system")
    ARANGO_USER = os.getenv("ARANGO_USER", "root")
    ARANGO_PASS = os.getenv("ARANGO_PASSWORD", "")
    
    # --- DATABASE: SQL (POSTGRESQL) ---
    _PG_HOST = os.getenv("POSTGRESQL_HOST")
    _PG_PORT = os.getenv("POSTGRESQL_PORT")
    _PG_DB = os.getenv("POSTGRESQL_DB")
    _PG_USER = os.getenv("POSTGRESQL_USER")
    _PG_PASS = os.getenv("POSTGRESQL_PASSWORD")

    @property
    def POSTGRES_DSN(self):
        """
        Constructs the connection string (DSN). Returns None if info is missing.
        Format: postgresql://user:pass@host:port/dbname
        """
        if not all([self._PG_HOST, self._PG_USER, self._PG_PASS, self._PG_DB]):
            return None
        
        return f"postgresql://{self._PG_USER}:{self._PG_PASS}@{self._PG_HOST}:{self._PG_PORT}/{self._PG_DB}"

    @staticmethod
    def is_remote():
        """Determines if tests are running on Selenoid (Remote) or Local."""
        return Config.SELENIUM_REMOTE_URL is not None