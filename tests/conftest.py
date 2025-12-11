import pytest
import allure
import os
import time
import requests
import logging
from selenium import webdriver
from config import Config

logging.getLogger("selenium").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

@pytest.fixture(scope="function")
def driver(request):
    remote_url = os.getenv("SELENIUM_REMOTE_URL")
    browser_name = os.getenv("BROWSER", "chrome").lower()
    headless = os.getenv("HEADLESS") == "true"
    
    # Video dosya adı
    video_name = f"{request.node.name}.mp4".replace(" ", "_")

    driver = None
    options = None

    if remote_url:
        print(f"\n[SETUP] Selenoid Remote: {browser_name.upper()}")
        
        if browser_name == "chrome":
            options = webdriver.ChromeOptions()
        elif browser_name == "firefox":
            options = webdriver.FirefoxOptions()
        else:
            options = webdriver.ChromeOptions()

        # --- SELENOID AYARLARI ---
        selenoid_options = {
            "enableVNC": True,
            "enableVideo": True,       # Video AÇIK
            "videoName": video_name,   # Dosya adı sabitlendi
            "name": request.node.name
        }
        options.set_capability("selenoid:options", selenoid_options)
        
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Remote(command_executor=remote_url, options=options)

    else:
        # Local
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=options)

    driver.implicitly_wait(Config.TIMEOUT)
    yield driver
    
    # --- TEARDOWN ---
    
    # 1. Hata varsa Screenshot al (Screenshot sadece hatada kalsın)
    if request.node.rep_call.failed:
        try:
            allure.attach(driver.get_screenshot_as_png(), name="Hata_Screenshot", attachment_type=allure.attachment_type.PNG)
        except:
            pass

    # 2. Önce Tarayıcıyı Kapat (Video kaydının bitmesi için şart!)
    driver.quit()

    # 3. Video Rapora Ekleme (HER DURUMDA: PASS veya FAIL)
    if remote_url:
        # Video dosyasının diske yazılması için kısa bekleme
        time.sleep(3) 
        
        video_url = f"http://selenoid:4444/video/{video_name}"
        
        try:
            print(f"[REPORT] Video indiriliyor: {video_url}")
            response = requests.get(video_url, timeout=5)
            
            if response.status_code == 200:
                # Başarılı veya Hatalı fark etmeksizin ekle
                allure.attach(response.content, name="Test Kaydı (Video)", attachment_type=allure.attachment_type.MP4)
            else:
                print(f"[UYARI] Video bulunamadı (Status: {response.status_code})")
        except Exception as e:
            print(f"[HATA] Video eklenirken sorun oluştu: {e}")

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)