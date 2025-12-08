import pytest
import allure
import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from config import Config

# --- GÜRÜLTÜ ENGELLEME ---
# WDM artık kullanılmadığı için onun loglarını kapatmaya gerek yok ama 
# Selenium'un kendi loglarını temiz tutmak iyidir.
logging.getLogger("selenium").setLevel(logging.WARNING)

@pytest.fixture(scope="function")
def driver(request):
    # Ayarları Çek
    remote_url = os.getenv("SELENIUM_REMOTE_URL")
    browser_name = os.getenv("BROWSER", "chrome").lower()
    headless = os.getenv("HEADLESS") == "true"

    driver = None
    options = None

    print(f"\n[SETUP] Test Başlatılıyor -> Tarayıcı: {browser_name.upper()} | Mod: {'HEADLESS' if headless else 'GUI'}")

    # ------------------------------------------------------------------
    # 1. REMOTE (DOCKER / SELENOID)
    # ------------------------------------------------------------------
    if remote_url:
        print(f"[SETUP] Remote WebDriver'a bağlanılıyor: {remote_url}")
        
        if browser_name == "chrome":
            options = webdriver.ChromeOptions()
        elif browser_name == "firefox":
            options = webdriver.FirefoxOptions()
        elif browser_name == "edge":
            options = webdriver.EdgeOptions()
        else:
            print(f"UYARI: Remote ortamda '{browser_name}' desteklenmiyor, Chrome kullanılıyor.")
            options = webdriver.ChromeOptions()
        
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        
        if headless:
            if browser_name == "firefox":
                options.add_argument("-headless")
            else:
                options.add_argument("--headless")

        driver = webdriver.Remote(command_executor=remote_url, options=options)

    # ------------------------------------------------------------------
    # 2. LOCAL (SENİN BİLGİSAYARIN) - NATIVE SELENIUM MANAGER
    # ------------------------------------------------------------------
    else:
        # --- A. CHROME ---
        if browser_name == "chrome":
            # Manager yok, Selenium 4.10+ kendi halleder
            service = ChromeService() 
            options = webdriver.ChromeOptions()
            options.add_argument("--start-maximized")
            if "incognito" in browser_name:
                options.add_argument("--incognito")
            if headless:
                options.add_argument("--headless")
                options.add_argument("--window-size=1920,1080")
            driver = webdriver.Chrome(service=service, options=options)

        # --- B. FIREFOX ---
        elif browser_name == "firefox":
            service = FirefoxService()
            options = webdriver.FirefoxOptions()
            if "incognito" in browser_name:
                options.add_argument("-private")
            if headless:
                options.add_argument("-headless")
                options.add_argument("--width=1920")
                options.add_argument("--height=1080")
            else:
                options.add_argument("--start-maximized")
            driver = webdriver.Firefox(service=service, options=options)

        # --- C. EDGE ---
        elif browser_name == "edge":
            service = EdgeService()
            options = webdriver.EdgeOptions()
            options.add_argument("--start-maximized")
            if "incognito" in browser_name:
                options.add_argument("-inprivate")
            if headless:
                options.add_argument("--headless")
                options.add_argument("--window-size=1920,1080")
            driver = webdriver.Edge(service=service, options=options)

        # --- D. SAFARI ---
        elif browser_name == "safari":
            if headless:
                print("UYARI: Safari 'Headless' modunu desteklemez!")
            driver = webdriver.Safari()
            driver.maximize_window()

        else:
            raise ValueError(f"Desteklenmeyen Tarayıcı: {browser_name}")

    driver.implicitly_wait(Config.TIMEOUT)
    yield driver
    
    # TEARDOWN
    if request.node.rep_call.failed:
        try:
            allure.attach(driver.get_screenshot_as_png(), name="Hata_Goruntusu", attachment_type=allure.attachment_type.PNG)
        except:
            pass
    driver.quit()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)