import platform
import os
import subprocess
import sys
import tempfile
from pathlib import Path
import shutil

# --- DOCKERFILE ŞABLONU ---
DOCKERFILE_TEMPLATE = """
FROM alpine:latest
RUN apk add --no-cache ffmpeg bash xset pulseaudio-utils
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
"""

def is_docker_running():
    """Docker Daemon'ın çalışıp çalışmadığını kontrol eder."""
    try:
        subprocess.run(["docker", "info"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_image_exists(image_name):
    """Docker'da belirtilen imajın olup olmadığını kontrol eder."""
    try:
        result = subprocess.run(
            ["docker", "images", "-q", image_name],
            capture_output=True,
            text=True
        )
        return bool(result.stdout.strip())
    except subprocess.CalledProcessError:
        return False

def build_arm_native_recorder(target_image_name):
    original_image = "selenoid/video-recorder:latest-release"
    
    print(f"   🛠️  DİKKAT: '{target_image_name}' bulunamadı. Otomatik inşa süreci başlıyor...")
    
    # 1. Orijinal İmaj Kontrolü (Offline Support)
    if check_image_exists(original_image):
        print(f"   ✅ Orijinal kaynak imaj ({original_image}) yerel diskte bulundu. İnternetten çekilmeyecek.")
    else:
        print(f"   📥 Orijinal imaj yerelde yok, internetten çekiliyor: {original_image}")
        try:
            subprocess.run(["docker", "pull", original_image], check=True, stdout=subprocess.DEVNULL) # stderr açık kalsın
        except subprocess.CalledProcessError:
            print(f"   ❌ HATA: '{original_image}' çekilemedi. İnternet bağlantınızı veya Docker'ı kontrol edin.")
            sys.exit(1)
    
    # Geçici klasör işlemi
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        script_path = temp_path / "entrypoint.sh"
        dockerfile_path = temp_path / "Dockerfile"
        
        # 2. entrypoint.sh dosyasını orijinal imajdan çıkart
        print("   📄 entrypoint.sh dosyası orijinal imajdan kopyalanıyor...")
        try:
            with open(script_path, "w") as f:
                # Platform uyarısını (WARNING: amd64/arm64 mismatch) gizlemek için stderr=DEVNULL eklendi
                subprocess.run(
                    ["docker", "run", "--rm", "--entrypoint", "cat", original_image, "/entrypoint.sh"],
                    stdout=f,
                    stderr=subprocess.DEVNULL, 
                    check=True
                )
        except subprocess.CalledProcessError:
             print("   ❌ HATA: entrypoint.sh dosyası kopyalanamadı!")
             sys.exit(1)
        
        if script_path.stat().st_size == 0:
            print("   ❌ HATA: entrypoint.sh dosyası boş çıkarıldı!")
            sys.exit(1)
            
        # 3. Dockerfile dosyasını oluştur
        print("   📝 Dockerfile oluşturuluyor...")
        with open(dockerfile_path, "w") as f:
            f.write(DOCKERFILE_TEMPLATE.strip())
            
        # 4. Yeni İmajı Derle
        print(f"   🔨 Native ARM imajı derleniyor: {target_image_name}")
        try:
            subprocess.run(
                ["docker", "build", "-t", target_image_name, "."],
                cwd=temp_dir,
                check=True
            )
            print("   ✅ İmaj başarıyla oluşturuldu!")
        except subprocess.CalledProcessError:
            print("   ❌ HATA: İmaj derlenirken bir sorun oluştu.")
            sys.exit(1)
            
    print("   🧹 Geçici dosyalar temizlendi.")

def main():
    # 0. Docker Sağlık Kontrolü
    if not is_docker_running():
        print("❌ KRİTİK HATA: Docker çalışmıyor! Lütfen Docker Desktop'ı başlatın.")
        sys.exit(1)

    arch = platform.machine().lower()
    system = platform.system()
    
    print(f"🖥️  Sistem Taranıyor... İşletim Sistemi: {system} | İşlemci: {arch}")

    browsers_json = None
    video_image = None
    
    # --- 1. MİMARİ KONTROLÜ ---
    if any(x in arch for x in ["arm", "aarch64"]):
        print("✅ Tespit: ARM Mimarisi (Apple Silicon)")
        browsers_json = "browsers_arm.json"
        video_image = "selenoid/video-recorder:arm-native"
        auto_worker_count = "6"
        
        if not check_image_exists(video_image):
            build_arm_native_recorder(video_image)
        
        print("   📦 ARM Browser İmajları Kontrol Ediliyor...")
        # Check=False yaptık, internet yoksa bile hata verip durmasın, belki imaj lokalde vardır.
        subprocess.run(["docker", "pull", "seleniarm/standalone-chromium:latest"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["docker", "pull", "seleniarm/standalone-firefox:latest"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    elif any(x in arch for x in ["x86_64", "amd64", "i386", "i686"]):
        print("✅ Tespit: Intel/AMD Mimarisi")
        browsers_json = "browsers_intel.json"
        video_image = "selenoid/video-recorder:latest-release"
        auto_worker_count = "2"
        
        print("   📦 Intel Browser İmajları Kontrol Ediliyor...")
        subprocess.run(["docker", "pull", "selenoid/vnc:chrome_120.0"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["docker", "pull", "selenoid/vnc:firefox_120.0"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["docker", "pull", video_image], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        print(f"❌ HATA: Mimari tanınamadı ({arch}).")
        sys.exit(1)

    # --- 2. ÇALIŞTIRMA ---
    final_worker_count = os.getenv("WORKER_COUNT", auto_worker_count)

    if browsers_json and video_image:
        print(f"\n🚀 Test Ortamı Başlatılıyor...")
        print(f"   📄 Browser Config : {browsers_json}")
        print(f"   🎥 Video Image    : {video_image}")
        
        if final_worker_count != auto_worker_count:
            print(f"   ⚠️ MANUEL AYAR: Worker sayısı {final_worker_count} olarak ayarlandı.")
        else:
            print(f"   ⚡ Otomatik Worker: {final_worker_count}")
        
        env = os.environ.copy()
        env["BROWSERS_JSON"] = browsers_json
        env["VIDEO_RECORDER_IMAGE"] = video_image
        env["WORKER_COUNT"] = final_worker_count
        
        try:
            print("🧹 Temizlik yapılıyor...")
            subprocess.run(["docker-compose", "down", "--remove-orphans"], env=env, stderr=subprocess.DEVNULL)
            
            print("🎬 Konteynerler Ayağa Kaldırılıyor...")
            result = subprocess.run(
                ["docker-compose", "up", "--build", "--exit-code-from", "pytest-tests"], 
                env=env
            )
            exit_code = result.returncode

        except KeyboardInterrupt:
            print("\n🛑 Kullanıcı tarafından durduruldu.")
            exit_code = 0
        except Exception as e:
            print(f"❌ Hata: {e}")
            exit_code = 1
        finally:
            print("\n🧹 Sistem kapatılıyor...")
            subprocess.run(["docker-compose", "down", "--remove-orphans"], env=env, stderr=subprocess.DEVNULL)
            sys.exit(exit_code)

if __name__ == "__main__":
    main()