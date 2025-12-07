import pytest
import allure
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from config import Config

# 1. DRIVER AYARLARI
@pytest.fixture(scope="function")
def driver(request):
    service = ChromeService(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    
    # --- HEADLESS AYARI (DİNAMİK) ---
    # Eğer .env dosyasında HEADLESS=true ise arkaplanda çalıştır
    if os.getenv("HEADLESS") == "true":
        options.add_argument("--headless")
        # Headless modda ekran boyutu hatası almamak için sabit boyut verilir
        options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(Config.TIMEOUT)
    
    yield driver
    
    # --- TEARDOWN (TEST BİTİŞİ) ---
    
    # Eğer test başarısız olduysa (failed) burası devreye girer
    if request.node.rep_call.failed:
        # Allure Raporuna Ekran Görüntüsü Ekle
        allure.attach(
            driver.get_screenshot_as_png(),
            name="Hata_Goruntusu",
            attachment_type=allure.attachment_type.PNG
        )
        print("\n[ALLURE] Hata görüntüsü rapora eklendi.")
    
    driver.quit()

# Bu fonksiyon, testin sonucunu (Passed/Failed) yakalar ve yukarıdaki fixture'a haber verir.
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    
    # Testin sonucunu 'rep_call', 'rep_setup' gibi değişkenlere atar
    setattr(item, "rep_" + rep.when, rep)