from utilities.constants import ErrorMessages

class TestData:
    # --- POZİTİF SENARYOLAR ---
    VALID_USERS = [
        ("standard_user", "secret_sauce"),
        ("problem_user", "secret_sauce"),
        ("performance_glitch_user", "secret_sauce")
    ]

    # --- NEGATİF SENARYOLAR ---
    # Artık string yok, değişken referansı var!
    INVALID_LOGIN_DATA = [
        ("locked_out_user", "secret_sauce", ErrorMessages.LOCKED_OUT_ERROR),
        ("standard_user", "yanlis_sifre", ErrorMessages.INVALID_CRED_ERROR),
        ("olmayan_kullanici", "secret_sauce", ErrorMessages.INVALID_CRED_ERROR)
    ]