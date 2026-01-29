# --- YARDIMCI KOMUTLAR (Internal) ---
clean:
	@echo "🧹 Allure sonuçları temizleniyor..."
	@rm -rf allure-results/*
	@echo "✅ Temizlik tamamlandı."

# Sadece Testi Koşan (Temizlik Yapmayan) İç Komutlar
_run_cy:
	@echo "🚀 Cypress Testleri Başlatılıyor..."
	docker-compose up --build cypress-tests

_run_py:
	@echo "🐍 Python Testleri (start_tests.py) Başlatılıyor..."
	python3 start_tests.py

# --- KULLANICI KOMUTLARI (External) ---

# 1. Sadece CYPRESS (Temizle -> Çalıştır)
cy: clean _run_cy

# 2. Sadece PYTHON (Temizle -> Çalıştır)
py: clean _run_py

# 3. HEPSİ (Temizle -> Sırayla Çalıştır)
# Buradaki sihir: 'clean' sadece EN BAŞTA bir kere çalışır.
# Sonra _run_cy ve _run_py temizlik yapmadan peş peşe çalışır.
all: clean _run_cy _run_py

# 4. RAPOR
report:
	allure serve allure-results