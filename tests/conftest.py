# tests/conftest.py

import pytest
import allure
import logging
import requests
from config import Config
from utilities.db_client import DBClient
from utilities.driver_factory import DriverFactory

# --- LOGGING KURULUMU ---
# Global logger yerine modüle özel logger kullanımı
logger = logging.getLogger("Conftest")

# Selenium ve Urllib3'ün gürültülü loglarını sustur
logging.getLogger("selenium").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

@pytest.fixture(scope="session")
def db_client():
    client = DBClient()
    yield client
    client.close()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Test sonucunu (Pass/Fail) 'item' objesine kaydeder.
    Bu bilgiye teardown aşamasında ihtiyacımız olacak.
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

@pytest.fixture(scope="function")
def driver(request):
    """
    Driver Factory kullanarak tarayıcıyı ayağa kaldırır ve
    test bitiminde akıllı video yönetimi yapar.
    """
    test_name = request.node.name
    driver_instance = None
    
    # --- 1. SETUP (BAŞLANGIÇ) ---
    try:
        driver_instance = DriverFactory.get_driver(Config, test_name)
        driver_instance.implicitly_wait(Config.TIMEOUT)
        yield driver_instance
    
    except Exception as e:
        logger.error(f"[SETUP HATA] Driver başlatılamadı: {e}")
        yield None

    # --- 2. TEARDOWN (BİTİŞ) ---
    if driver_instance:
        # Testin durumunu kontrol et
        # request.node.rep_call.failed -> True ise test patlamıştır
        is_failed = False
        node = request.node
        if getattr(node, 'rep_call', None) and node.rep_call.failed:
            is_failed = True
            
            # Hata anında ekran görüntüsü al
            try:
                allure.attach(
                    driver_instance.get_screenshot_as_png(), 
                    name="Hata_Goruntusu", 
                    attachment_type=allure.attachment_type.PNG
                )
            except Exception as e:
                logger.warning(f"Screenshot alınamadı: {e}")

        # Driver'ı kapat (Bu işlem videoyu Selenoid tarafında diske yazar)
        driver_instance.quit()

        # --- 3. AKILLI VIDEO TEMİZLİĞİ ---
        # Eğer mod 'on_failure' ise ve test BAŞARILI ise videoyu silmeliyiz.
        # DriverFactory'de driver objesine yapıştırdığımız 'video_name'i alıyoruz.
        video_name = getattr(driver_instance, 'video_name', None)
        
        should_delete = (
            Config.RECORD_VIDEO == "on_failure" 
            and not is_failed 
            and video_name is not None
        )

        if should_delete:
            _delete_video_from_selenoid(video_name)

def _delete_video_from_selenoid(video_name):
    """
    Selenoid API kullanarak gereksiz (başarılı test) videosunu siler.
    Endpoint: DELETE http://<selenoid-host>:4444/video/<filename>
    """
    if not Config.SELENIUM_REMOTE_URL:
        return

    try:
        # Remote URL genellikle "http://host:4444/wd/hub" formatındadır.
        # "/wd/hub" kısmını atıp base url'i (http://host:4444) alıyoruz.
        base_url = Config.SELENIUM_REMOTE_URL.split("/wd/hub")[0]
        delete_url = f"{base_url}/video/{video_name}"
        
        response = requests.delete(delete_url, timeout=5)
        
        if response.status_code == 200:
            logger.info(f"🗑️ [CLEANUP] Başarılı test videosu silindi: {video_name}")
        elif response.status_code == 404:
            logger.warning(f"⚠️ Video bulunamadı (Zaten silinmiş olabilir): {video_name}")
        else:
            logger.warning(f"⚠️ Video silinemedi. Kod: {response.status_code} | URL: {delete_url}")
            
    except Exception as e:
        logger.error(f"❌ Video silme işlemi sırasında hata: {e}")