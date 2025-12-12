# seed.py:

from arango import ArangoClient
from config import Config

def seed_database():
    # 1. Bağlantı
    client = ArangoClient(hosts=Config.ARANGO_URL)
    sys_db = client.db('_system', username=Config.ARANGO_USER, password=Config.ARANGO_PASS)

    # Veritabanı yoksa oluştur (Opsiyonel, zaten var dedin ama garanti olsun)
    if not sys_db.has_database(Config.ARANGO_DB):
        sys_db.create_database(Config.ARANGO_DB)
    
    # Hedef DB'ye bağlan
    db = client.db(Config.ARANGO_DB, username=Config.ARANGO_USER, password=Config.ARANGO_PASS)

    # Collection oluştur (Tablo karşılığı)
    col_name = "error_codes"
    if db.has_collection(col_name):
        db.delete_collection(col_name) # Temiz başlangıç
    
    error_col = db.create_collection(col_name)

    # Verileri Ekle
    data = [
        {
            "code": "LOCKED",
            "message_en": "Epic sadface: Sorry, this user has been locked out.",
            "message_tr": "Üzgünüz, bu kullanıcı kilitlendi."
        },
        {
            "code": "INVALID",
            "message_en": "Epic sadface: Username and password do not match any user in this service",
            "message_tr": "Kullanıcı adı veya şifre hatalı."
        }
    ]
    
    error_col.insert_many(data)
    print(f"✅ Başarılı: {len(data)} adet hata kodu ArangoDB '{Config.ARANGO_DB}' veritabanına eklendi.")

if __name__ == "__main__":
    seed_database()