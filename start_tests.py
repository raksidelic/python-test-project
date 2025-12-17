import platform
import os
import subprocess
import sys

def main():
    arch = platform.machine().lower()
    system = platform.system()
    
    print(f"🖥️  Sistem Taranıyor... İşletim Sistemi: {system} | İşlemci: {arch}")

    browsers_json = None
    
    # --- 1. OTOMATİK HESAPLAMA (Varsayılan) ---
    if any(x in arch for x in ["arm", "aarch64"]):
        print("✅ Tespit: ARM Mimarisi")
        browsers_json = "browsers_arm.json"
        auto_worker_count = "8" # M3 varsayılanı
        
        # İmaj hazırlığı...
        subprocess.run(["docker", "pull", "seleniarm/standalone-chromium:latest"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["docker", "pull", "seleniarm/standalone-firefox:latest"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    elif any(x in arch for x in ["x86_64", "amd64", "i386", "i686"]):
        print("✅ Tespit: Intel/AMD Mimarisi")
        browsers_json = "browsers_intel.json"
        auto_worker_count = "2" # Intel varsayılanı
        
        # İmaj hazırlığı...
        subprocess.run(["docker", "pull", "selenoid/vnc:chrome_120.0"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["docker", "pull", "selenoid/vnc:firefox_120.0"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        print(f"❌ HATA: Mimarisi tanınamadı.")
        sys.exit(1)

    # --- 2. MANUEL OVERRIDE (GitLab'dan gelen emir) ---
    # os.getenv("WORKER_COUNT") varsa onu alır, yoksa auto_worker_count'u kullanır.
    final_worker_count = os.getenv("WORKER_COUNT", auto_worker_count)

    if browsers_json:
        print(f"\n🚀 Test Ortamı Başlatılıyor...")
        print(f"   📄 Konfigürasyon: {browsers_json}")
        
        # Kullanıcıya bilgi ver: Manuel mi, Otomatik mi?
        if final_worker_count != auto_worker_count:
            print(f"   ⚠️ MANUEL AYAR AKTİF: Worker sayısı {final_worker_count} olarak zorlandı.")
        else:
            print(f"   ⚡ Otomatik Worker Sayısı: {final_worker_count}")
        
        env = os.environ.copy()
        env["BROWSERS_JSON"] = browsers_json
        env["WORKER_COUNT"] = final_worker_count # Docker'a gidecek nihai sayı
        
        try:
            # Temizlik
            subprocess.run(["docker-compose", "down", "--remove-orphans"], env=env, stderr=subprocess.DEVNULL)
            
            # Başlat
            print("🎬 Testler Koşuluyor...")
            result = subprocess.run(
                ["docker-compose", "up", "--build", "--exit-code-from", "pytest-tests"], 
                env=env
            )
            exit_code = result.returncode

        except KeyboardInterrupt:
            exit_code = 0
        except Exception as e:
            print(f"Hata: {e}")
            exit_code = 1
        finally:
            print("\n🧹 Ortam temizleniyor...")
            subprocess.run(["docker-compose", "down", "--remove-orphans"], env=env, stderr=subprocess.DEVNULL)
            sys.exit(exit_code)

if __name__ == "__main__":
    main()