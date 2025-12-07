import pytest
import allure
import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from config import Config

# --- GÜRÜLTÜ ENGELLEME (WDM LOGLARINI SUSTURMA) ---
# WebDriver Manager'ın gereksiz loglarını kapatır
os.environ['WDM_LOG'] = "0"
logging.getLogger("WDM").setLevel(logging.WARNING)

# 1. DRIVER AYARLARI
@pytest.fixture(scope="function")
def driver(request):
    # Remote URL kontrolü (Docker/Selenoid için)
    remote_url = os.getenv("SELENIUM_REMOTE_URL")
    
    # --- SENARYO A: REMOTE (DOCKER) ---
    if remote_url:
        print(f"\n[SETUP] Remote WebDriver'a bağlanılıyor: {remote_url}")
        options = webdriver.ChromeOptions()
        # Docker içinde pencere boyutu önemlidir, aksi halde elementler görünmeyebilir
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        # Shared Memory sorununu aşmak için
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        
        driver = webdriver.Remote(
            command_executor=remote_url,
            options=options
        )

    # --- SENARYO B: LOCAL (SENİN BİLGİSAYARIN) ---
    else:
        print(f"\n[SETUP] Local WebDriver başlatılıyor ({'HEADLESS' if os.getenv('HEADLESS') == 'true' else 'GUI'})...")
        service = ChromeService(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        
        # Headless Ayarı (Sadece Local için geçerli, Docker zaten headless gibidir)
        if os.getenv("HEADLESS") == "true":
            options.add_argument("--headless")
            options.add_argument("--window-size=1920,1080")
            
        driver = webdriver.Chrome(service=service, options=options)
    
    # Ortak Bekleme Süresi
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

# 2. KRİTİK KANCA (HOOK)
# Bu fonksiyon, testin sonucunu (Passed/Failed) yakalar ve yukarıdaki fixture'a haber verir.
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    
    # Testin sonucunu 'rep_call', 'rep_setup' gibi değişkenlere atar
    setattr(item, "rep_" + rep.when, rep)