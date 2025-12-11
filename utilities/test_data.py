from utilities.db_client import DBClient

# DB Bağlantısını başlat
# Not: Testler çok hızlı koşarsa her seferinde bağlanmak yerine
# bu client bir Singleton veya Fixture olarak da tasarlanabilir.
db = DBClient()

class TestData:
    VALID_USERS = [
        ("standard_user", "secret_sauce"),
        ("probl2em_user", "sec2ret_sauce"),
        ("performance_glitch_user", "secret_sauce")
    ]

    # Dinamik Veri: ArangoDB'den geliyor
    INVALID_LOGIN_DATA = [
        ("locked_out_user", "secret_sauce", db.get_error_message('LOCKED')),
        ("standard_user", "yanlis_sifre", db.get_error_message('INVALID')),
        ("olmayan_kullanici", "secret_sauce", db.get_error_message('INVALID'))
    ]