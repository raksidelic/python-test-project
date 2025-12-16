import logging
from typing import Any
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

# Logger Tanımlaması
logger = logging.getLogger("DriverFactory")

class DriverFactory:
    @staticmethod
    def get_driver(config: Any, execution_id: str) -> WebDriver:
        """
        Verilen konfigürasyona göre (Local veya Remote) WebDriver örneği oluşturur.
        execution_id: Her test koşumu için üretilen benzersiz UUID (Conftest'ten gelir).
        """
        browser = config.BROWSER.lower()
        remote_url = config.SELENIUM_REMOTE_URL
        
        logger.info(f"Driver başlatılıyor: {browser.upper()} | Headless: {config.HEADLESS} | Remote: {bool(remote_url)} | ExecID: {execution_id}")

        # 1. Tarayıcı Opsiyonlarını Hazırla
        options = DriverFactory._get_browser_options(browser, config)

        # 2. Remote (Selenoid) veya Local Driver Başlat
        if remote_url:
            return DriverFactory._create_remote_driver(remote_url, options, execution_id, config)
        else:
            return DriverFactory._create_local_driver(browser, options)

    @staticmethod
    def _get_browser_options(browser: str, config: Any):
        """Tarayıcıya özel standart opsiyonları ayarlar."""
        options = None
        
        if browser == "chrome":
            options = ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            # [GERİ EKLENDİ] Eski dosyanızdaki önemli opsiyonlar
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-popup-blocking")
            
        elif browser == "firefox":
            options = FirefoxOptions()
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
        
        else:
            raise ValueError(f"❌ Desteklenmeyen tarayıcı türü: {browser}")

        if config.HEADLESS:
            options.add_argument("--headless")

        return options

    @staticmethod
    def _create_remote_driver(remote_url: str, options: Any, execution_id: str, config: Any) -> WebDriver:
        """Remote WebDriver (Selenoid/Grid) bağlantısını kurar."""
        
        # 1. Config'den modu oku ('true', 'false', 'on_failure')
        mode = getattr(config, "RECORD_VIDEO", "on_failure").lower()
        should_record = mode in ["true", "always", "on_failure", "on_success"]

        selenoid_options = {
            "enableVNC": True,
            "enableVideo": should_record,
            "videoScreenSize": "1920x1080",
            # UI'da görünecek isim (UUID kullanıyoruz ki karışmasın)
            "name": execution_id,
            
            # --- KRİTİK: DOCKER ETİKETLEME ---
            # VideoManager'ın bu konteyneri API kullanmadan bulabilmesi için
            # 'execution_id' etiketini konteynerin alnına yapıştırıyoruz.
            "labels": {
                "env": "test", 
                "team": "qa",
                "execution_id": execution_id  # <--- VideoManager bunu arayacak
            }
        }
        
        options.set_capability("selenoid:options", selenoid_options)
        
        try:
            logger.info(f"Remote bağlantı kuruluyor... (Label: {execution_id})")
            driver = webdriver.Remote(command_executor=remote_url, options=options)
            
            if should_record:
                final_video_name = f"{driver.session_id}.mp4"
                driver.video_name = final_video_name
            else:
                driver.video_name = None

            logger.info(f"✅ Driver başlatıldı. Video: {driver.video_name}")
            return driver
        
        except Exception as e:
            logger.error(f"❌ Remote Driver başlatılamadı! Hata: {e}")
            raise e

    @staticmethod
    def _create_local_driver(browser: str, options: Any) -> WebDriver:
        """Local WebDriver başlatır."""
        try:
            if browser == "chrome":
                driver = webdriver.Chrome(options=options)
            elif browser == "firefox":
                driver = webdriver.Firefox(options=options)
            else:
                 raise ValueError(f"Local driver için desteklenmeyen tarayıcı: {browser}")
            
            logger.info("✅ Local Driver başarıyla başlatıldı.")
            driver.maximize_window()
            return driver
        except Exception as e:
            logger.error(f"❌ Local Driver başlatılamadı! Hata: {e}")
            raise e