from arango import ArangoClient
from config import Config
import logging
import sys

class DBClient:
    def __init__(self):
        # Başlangıçta bağlanma! Sadece değişkenleri hazırla.
        self.client = None
        self.db = None
        self.logger = logging.getLogger("DBClient")
        
        # --- DEBUG: Konfigürasyonları Yazdır ---
        print(f"\n[DEBUG] DBClient Başlatılıyor...")
        print(f"[DEBUG] Hedef URL: '{Config.ARANGO_URL}'")
        # Hangi DB ismini görüyor?
        print(f"[DEBUG] Hedef DB: '{Config.ARANGO_DB}'") 
        print(f"[DEBUG] User: '{Config.ARANGO_USER}'")
        # Şifreyi açık yazma ama dolu mu boş mu kontrol et
        pass_status = "DOLU" if Config.ARANGO_PASS else "BOŞ/NONE"
        print(f"[DEBUG] Pass: {pass_status}")
        # ---------------------------------------

    def _connect(self):
        """Gerçek bağlantıyı ihtiyaç anında kurar (Lazy Loading)"""
        if self.db is not None:
            return # Zaten bağlıysa tekrar uğraşma

        try:
            self.logger.info(f"DB Bağlantısı kuruluyor: {Config.ARANGO_URL} -> {Config.ARANGO_DB}")
            self.client = ArangoClient(hosts=Config.ARANGO_URL)
            
            # Bağlantıyı oluştur
            self.db = self.client.db(
                Config.ARANGO_DB, 
                username=Config.ARANGO_USER, 
                password=Config.ARANGO_PASS
            )
            
            # Bağlantıyı test et (Hata varsa burada patlasın ve yakalayalım)
            self.db.properties()
            print("[DEBUG] BAĞLANTI BAŞARILI! 🎉") # Konsola bas
            self.logger.info("DB Bağlantısı Başarılı.")
            
        except Exception as e:
            # --- DEBUG: Hatayı Konsola Kus ---
            print(f"\n[DEBUG] ❌ BAĞLANTI HATASI OLUŞTU!")
            print(f"[DEBUG] Hata Türü: {type(e).__name__}")
            print(f"[DEBUG] Hata Mesajı: {str(e)}")
            print(f"[DEBUG] --------------------------\n")
            # ---------------------------------
            self.logger.error(f"DB Bağlantı Hatası: {e}")
            # Burada raise etmiyoruz, testin devam etmesine izin verip
            # veriyi çekemezse default değer dönmesini sağlayacağız (Robustness)
            self.db = None 

    def get_error_message(self, error_code, lang="message_en"):
        print(f"[DEBUG] '{error_code}' için DB'ye gidiliyor...") # İzleme
        # Önce bağlanmayı dene
        self._connect()
        
        # Eğer bağlantı başarısız olduysa kod patlamasın, güvenli çıkış yap
        if self.db is None:
            print(f"[DEBUG] DB Nesnesi None olduğu için varsayılan hata dönülüyor.")
            self.logger.warning(f"DB bağlı değil, '{error_code}' için varsayılan mesaj dönülüyor.")
            return "DB Error: Connection Failed"

        aql = f"FOR doc IN error_codes FILTER doc.code == @code RETURN doc.{lang}"
        bind_vars = {'code': error_code}
        
        try:
            cursor = self.db.aql.execute(aql, bind_vars=bind_vars)
            result = [doc for doc in cursor]
            
            if result:
                return result[0]
            else:
                self.logger.warning(f"Uyarı: {error_code} kodlu mesaj DB'de bulunamadı.")
                return "Unknown Error Code"
                
        except Exception as e:
            self.logger.error(f"AQL Sorgu Hatası: {e}")
            return "DB Query Error"

    def close(self):
        if self.client:
            self.client.close()