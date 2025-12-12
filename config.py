# config.py:

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_URL = os.getenv("BASE_URL")
    USERNAME = os.getenv("APP_USERNAME")
    PASSWORD = os.getenv("APP_PASSWORD")
    BROWSER = os.getenv("BROWSER", "chrome")
    TIMEOUT = int(os.getenv("TIMEOUT", 10))
    
    # DB Config
    ARANGO_URL = os.getenv("ARANGO_URL")
    ARANGO_DB = os.getenv("ARANGO_DB_NAME")
    ARANGO_USER = os.getenv("ARANGO_USER")
    ARANGO_PASS = os.getenv("ARANGO_PASSWORD")