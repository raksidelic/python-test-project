class TestData:
    VALID_USERS = [
        ("standard_user", "secret_sauce"),
        ("problem2_user", "secret2_sauce"),
        ("performance_glitch_user", "secret_sauce")
    ]

    # Dinamik yapı için değişiklik:
    # Artık burada DB çağrısı yapılmıyor. Sadece Hata Kodları (Key) tutuluyor.
    # Yapı: (username, password, error_key)
    INVALID_LOGIN_DATA = [
        ("locked_out_user", "secret_sauce", "LOCKED"),
        ("standard_user", "yanlis_sifre", "INVALID"),
        ("olmayan_kullanici", "secret_sauce", "INVALID")
    ]