# tests/conftest.py

import pytest
import allure
import logging
import os
import json
import docker
import fcntl  # Linux'ta dosya kilitleme için (xdist uyumlu)
from config import Config
from utilities.db_client import DBClient
from utilities.driver_factory import DriverFactory

# --- LOGGING ---
logger = logging.getLogger("Conftest")
logging.getLogger("selenium").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# Silinecek videoların tutulacağı Manifest Dosyası
CLEANUP_MANIFEST = "/app/videos/cleanup_manifest.jsonl"

@pytest.fixture(scope="session")
def db_client():
    client = DBClient()
    yield client
    client.close()

def _register_video_for_deletion(video_name):
    """
    Worker'lar (paralel çalışanlar) silinecek dosyayı buraya yazar.
    fcntl ile dosya kilitlenir, böylece veriler birbirine karışmaz.
    """
    entry = {"video": video_name, "action": "delete"}
    try:
        # 'a' modu ile append (ekleme) yapıyoruz
        with open(CLEANUP_MANIFEST, "a") as f:
            fcntl.flock(f, fcntl.LOCK_EX) # 🔒 KİLİTLE (Diğer workerlar bekler)
            f.write(json.dumps(entry) + "\n")
            fcntl.flock(f, fcntl.LOCK_UN) # 🔓 KİLİDİ AÇ
    except Exception as e:
        logger.error(f"Manifest dosyasına yazılamadı: {e}")

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

@pytest.fixture(scope="function")
def driver(request):
    test_name = request.node.name
    driver_instance = None
    
    # 1. SETUP
    try:
        driver_instance = DriverFactory.get_driver(Config, test_name)
        driver_instance.implicitly_wait(Config.TIMEOUT)
        yield driver_instance
    except Exception as e:
        logger.error(f"[SETUP HATA] Driver başlatılamadı: {e}")
        yield None

    # 2. TEARDOWN
    if driver_instance:
        # Test durumunu kontrol et
        is_failed = False
        node = request.node
        if getattr(node, 'rep_call', None) and node.rep_call.failed:
            is_failed = True
            try:
                allure.attach(
                    driver_instance.get_screenshot_as_png(), 
                    name="Hata_Goruntusu", 
                    attachment_type=allure.attachment_type.PNG
                )
            except:
                pass

        # Driver'ı kapat (Selenoid videoyu diske yazar)
        driver_instance.quit()

        # 3. AKILLI KAYIT (JSON'a Yazma)
        video_name = getattr(driver_instance, 'video_name', None)
        
        # Eğer 'on_failure' modundaysak ve test BAŞARILI ise -> Listeye ekle
        should_delete = (
            Config.RECORD_VIDEO == "on_failure" 
            and not is_failed 
            and video_name is not None
        )

        if should_delete:
            _register_video_for_deletion(video_name)

def pytest_sessionfinish(session, exitstatus):
    """
    TOPLU KIYIM ZAMANI 💀
    Tüm testler bittiğinde Master Node burayı çalıştırır.
    """
    if hasattr(session.config, 'workerinput'):
        return

    if not os.path.exists(CLEANUP_MANIFEST):
        return

    logger.info("🧹 [BATCH CLEANUP] Temizlik manifestosu okunuyor...")
    
    # Docker Client'ı başlat (requirements.txt içinde var)
    try:
        docker_client = docker.from_env()
    except Exception as e:
        logger.warning(f"Docker bağlantısı sağlanamadı: {e}")
        docker_client = None
    
    deleted_count = 0
    try:
        with open(CLEANUP_MANIFEST, "r") as f:
            lines = f.readlines()
            
        for line in lines:
            try:
                data = json.loads(line.strip())
                video_file = data.get("video") # Örn: fe604...mp4
                
                file_path = os.path.join("/app/videos", video_file)
                
                # --- 2. SİSTEM SEVİYESİ SENKRONİZASYON (NO SLEEP) ---
                # "Bir şekilde anlasın" dediğiniz yer burası:
                # Rastgele uyumak yerine, o dosyayı yazan konteyneri bulup
                # "İşin bitene kadar (kapanana kadar) buradayım" diyoruz.
                if docker_client:
                    try:
                        # Şu an çalışan tüm konteynerleri tara
                        for container in docker_client.containers.list():
                            # Konteynerin özelliklerinde bizim dosya ismimiz geçiyor mu?
                            # (Selenoid, dosya ismini Env veya Cmd olarak konteynere verir)
                            if video_file in str(container.attrs):
                                # Bulduk! Konteyner kapanana kadar blokla (Wait for Exit)
                                # Bu bir sleep değildir, işletim sistemi sinyali bekler.
                                container.wait()
                                break
                    except Exception as e:
                        # Konteyner o sırada zaten gittiyse hata verebilir, sorun yok.
                        pass
                # ----------------------------------------------------

                # Konteyner öldüğüne göre dosya artık diskte olmalı.
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted_count += 1
                else:
                    logger.warning(f"⚠️ Dosya diskte bulunamadı: {video_file}")

            except Exception as inner_e:
                logger.warning(f"Satır işlenemedi: {inner_e}")
                
        if os.path.exists(CLEANUP_MANIFEST):
             os.remove(CLEANUP_MANIFEST)
             
        logger.info(f"✅ [CLEANUP COMPLETE] Toplam {deleted_count} adet gereksiz video disken silindi.")
        
    except Exception as e:
        logger.error(f"❌ Toplu silme işleminde hata: {e}")
    """
    TOPLU KIYIM ZAMANI 💀
    Tüm testler bittiğinde Master Node burayı çalıştırır.
    """
    # Sadece Master Node çalıştırsın (Workerlar çalıştırmasın)
    if hasattr(session.config, 'workerinput'):
        return

    if not os.path.exists(CLEANUP_MANIFEST):
        return

    logger.info("🧹 [BATCH CLEANUP] Temizlik manifestosu okunuyor...")
    
    deleted_count = 0
    try:
        with open(CLEANUP_MANIFEST, "r") as f:
            lines = f.readlines()
            
        for line in lines:
            try:
                data = json.loads(line.strip())
                video_file = data.get("video")
                
                # Dosya yolu: /app/videos/test_x.mp4
                file_path = os.path.join("/app/videos", video_file)
                
                if os.path.exists(file_path):
                    os.remove(file_path) # 🔥 API YOK, DİREKT SİLME VAR
                    deleted_count += 1
            except Exception as inner_e:
                logger.warning(f"Satır işlenemedi: {inner_e}")
                
        # İş bittikten sonra manifestoyu da temizle
        os.remove(CLEANUP_MANIFEST)
        logger.info(f"✅ [CLEANUP COMPLETE] Toplam {deleted_count} adet gereksiz video disken silindi.")
        
    except Exception as e:
        logger.error(f"❌ Toplu silme işleminde hata: {e}")