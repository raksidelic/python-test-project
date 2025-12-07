import pytest
import allure
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from utilities.test_data import TestData

@allure.feature("Login Senaryoları")
class TestLogin:

    # 1. POZİTİF TESTLER (Birden fazla geçerli kullanıcı ile döngü)
    @allure.story("Başarılı Giriş Testleri")
    @allure.title("Geçerli Kullanıcı Girişi: {username}")
    @pytest.mark.parametrize("username, password", TestData.VALID_USERS)
    def test_valid_login_scenarios(self, driver, username, password):
        login_page = LoginPage(driver)
        login_page.load()
        login_page.login(username, password)
        
        dashboard = DashboardPage(driver)
        
        # Giriş başarılı mı kontrol et
        assert "inventory" in dashboard.get_url(), f"{username} ile giriş yapılamadı!"
        
    # 2. NEGATİF TESTLER (Yasaklı kullanıcı, Yanlış şifre vb.)
    @allure.story("Başarısız Giriş Denemeleri")
    @allure.title("Hatalı Giriş: {username}")
    @pytest.mark.parametrize("username, password, expected_error", TestData.INVALID_LOGIN_DATA)
    def test_invalid_login_scenarios(self, driver, username, password, expected_error):
        login_page = LoginPage(driver)
        login_page.load()
        login_page.login(username, password)
        
        # Hata mesajı beklediğimiz gibi mi kontrolü.
        actual_error = login_page.get_error_message()
        assert expected_error in actual_error, f"Beklenen hata: '{expected_error}', Alınan: '{actual_error}'"