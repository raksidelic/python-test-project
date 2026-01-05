import pytest
import allure
import threading
import http.server
import socketserver
import time
import os
from utilities.figma_client import FigmaClient
from utilities.ai_auditor import AIAuditor
from utilities.report_helper import ReportHelper

# Config
PORT = 8000
SITE_DIR = "site-v1"
FILE_KEY = os.getenv("FIGMA_PROJECT_KEY")
NODE_ID = os.getenv("FIGMA_NODE_ID")
MODEL_NAME = os.getenv("GEMINI_MODEL", "Gemini-1.5-Flash")

def get_base_url():
    if os.getenv("DOCKER_ENV") == "true":
        return f"http://pytest-test-runner:{PORT}"
    return f"http://localhost:{PORT}"

def take_full_page_screenshot(driver):
    """
    Sayfayı tam ekran çeker ve SONRA PENCEREYİ ESKİ HALİNE GETİRİR.
    (Bu sayede test bitiminde InvalidSession hatası oluşmaz)
    """
    # 1. Mevcut boyutu sakla (Yedekle)
    original_size = driver.get_window_size()
    
    # 2. Toplam Yüksekliği Hesapla
    total_width = driver.execute_script("return document.body.offsetWidth")
    total_height = driver.execute_script("""
        return Math.max(
            document.body.scrollHeight, 
            document.body.offsetHeight, 
            document.documentElement.clientHeight, 
            document.documentElement.scrollHeight, 
            document.documentElement.offsetHeight
        );
    """)

    # 3. Footer için Güvenlik Payı (+150px)
    safe_height = total_height + 150

    # 4. Pencereyi Büyüt
    driver.set_window_size(total_width, safe_height)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1.5)  # Render bekle
    
    # 5. Screenshot Al
    png_data = driver.get_screenshot_as_png()
    
    # 6. PENCEREYİ ESKİ HALİNE GETİR (Kritik Düzeltme) 🚑
    driver.set_window_size(original_size['width'], original_size['height'])
    
    return png_data

@pytest.fixture(scope="module")
def local_server():
    os.chdir(SITE_DIR)
    handler = http.server.SimpleHTTPRequestHandler
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("", PORT), handler)
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()
    yield
    httpd.shutdown()
    httpd.server_close()
    os.chdir("..")

@allure.title("AI-Powered Design Validation")
def test_figma_vs_live_site(driver, local_server):
    
    target_url = get_base_url()
    
    # --- CACHE BUSTING: URL'in sonuna rastgele sayı ekle ---
    # Tarayıcı bunu "yeni bir sayfa" sanıp en güncel HTML/CSS'i çekmek zorunda kalır.
    import time
    unique_url = f"{target_url}?t={int(time.time())}"
    
    with allure.step(f"Navigating to: {unique_url}"):
        driver.get(unique_url)
        time.sleep(2)
    
    # 1. Full Page Live Screenshot
    live_png_bytes = take_full_page_screenshot(driver)
    allure.attach(live_png_bytes, name="Live Site (Full Page)", attachment_type=allure.attachment_type.PNG)
    
    # 2. Figma Screenshot
    figma = FigmaClient()
    try:
        # Cache=True kullanıyoruz ki manuel dosyan varsa API'ye gitmesin
        figma_png_bytes = figma.get_node_image(FILE_KEY, NODE_ID, use_cache=True)
        allure.attach(figma_png_bytes, name="Figma Baseline (Original Design)", attachment_type=allure.attachment_type.PNG)
    except Exception as e:
        pytest.fail(f"Figma hatası: {e}")

    # --- KRİTİK EKLEME: TARAYICIYI ERKEN KAPAT ---
    # Görüntüleri aldık, artık tarayıcıya ihtiyacımız yok.
    # AI analizi uzun sürerse Selenoid timeout yemesin diye driver'ı şimdi kapatıyoruz.
    driver.quit()
    print("\n✅ Tarayıcı kapatıldı. AI Analizi başlatılıyor (Bu işlem zaman alabilir)...")
    # ---------------------------------------------

    # 3. AI Analizi (YENİ: Koordinatlı JSON Analizi)
    auditor = AIAuditor()
    errors_json = auditor.analyze_with_coordinates(figma_png_bytes, live_png_bytes)
    
    # 4. HTML Raporu Oluştur (Görsel Kırpma Dahil)
    html_report = ReportHelper.create_visual_html_report(
        errors_json, 
        figma_png_bytes, 
        live_png_bytes, 
        MODEL_NAME
    )
    
    # Raporu Ekle
    allure.attach(
        html_report, 
        name="🤖 AI UX/UI Visual Report", 
        attachment_type=allure.attachment_type.HTML
    )
    
    print(f"\n📢 Görsel Rapor oluşturuldu.")

    # 5. Hata Varsa Testi Fail Yap
    if len(errors_json) > 0:
        pytest.fail(f"{len(errors_json)} Visual Differences Detected! See the report.")