class TestData:
    # --- POZİTİF SENARYOLAR İÇİN KULLANICILAR ---
    VALID_USERS = [
        ("standard_user", "secret_sauce"),
        ("problem_user", "secret_sauce"),
        ("performance_glitch_user", "secret_sauce")
    ]

    # --- NEGATİF SENARYOLAR (HATA BEKLENEN) ---
    # Format: (Kullanıcı Adı, Şifre, Beklenen Hata Mesajı)
    INVALID_LOGIN_DATA = [
        ("locked_out_user", "secret_sauce", "Epic sadface: Sorry, this user has been locked out."),
        ("standard_user", "yanlis_sifre", "Epic sadface: Username and password do not match any user in this service"),
        ("olmayan_kullanici", "secret_sauce", "Epic sadface: Username and password do not match any user in this service")
    ]