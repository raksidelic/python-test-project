from arango import ArangoClient
from config import Config
import logging

class DBClient:
    def __init__(self):
        self.client = None
        self.db = None
        self.logger = logging.getLogger("DBClient")
        
        # --- DEBUG LOGS ---
        print(f"\n[DEBUG] Initializing DBClient... Target: {Config.ARANGO_URL}")

    def _connect(self):
        """
        SMART CONNECTION MANAGER (State-Based Logic):
        1. Is there an existing connection? If yes, 'Ping' it (Zombie Check).
        2. If ping fails or no connection exists, establish a 'Fresh Connection'.
        """
        # --- STEP 1: ZOMBIE CHECK (Check existing connection) ---
        if self.db is not None:
            try:
                self.db.properties() # Ping
                return # Connection is healthy, exit.
            except Exception:
                print("[DEBUG] ⚠️ Existing connection is dead (Zombie), reconnecting...")
                self.db = None
                self.client = None # Reset

        # --- STEP 2: FRESH CONNECT (Connect from scratch) ---
        try:
            self.logger.info(f"Attempting DB connection: {Config.ARANGO_URL}")
            # Create Client object from scratch
            self.client = ArangoClient(hosts=Config.ARANGO_URL)
            
            temp_db = self.client.db(
                Config.ARANGO_DB, 
                username=Config.ARANGO_USER, 
                password=Config.ARANGO_PASS
            )
            
            # HANDSHAKE (Liveness and Auth Check)
            temp_db.properties()
            
            self.db = temp_db
            print("[DEBUG] CONNECTION SUCCESSFUL (Fresh Connect)! 🎉")
            self.logger.info("DB connection successful.")
            
        except Exception as e:
            print(f"[DEBUG] ❌ Connection failed: {e}")
            self.logger.error(f"DB connection error: {e}")
            self.db = None
            self.client = None

    def is_connected(self):
        """
        Check method for fixture usage.
        """
        self._connect()
        return self.db is not None

    def get_error_message(self, error_code, lang="message_en"):
        # Connection guarantee (Refreshes if Zombie)
        self._connect()

        if self.db is None:
            return "DB Error: Connection Failed"

        aql = f"FOR doc IN error_codes FILTER doc.code == @code RETURN doc.{lang}"
        bind_vars = {'code': error_code}
        
        try:
            cursor = self.db.aql.execute(aql, bind_vars=bind_vars)
            result = [doc for doc in cursor]
            return result[0] if result else "Unknown Error Code"
        except Exception as e:
            self.logger.error(f"AQL query error: {e}")
            # If error occurred, reset connection for next time
            self.db = None 
            return "DB Query Error"

    def close(self):
        if self.client:
            self.client.close()