# Dockerfile:

FROM python:3.14

# Çalışma klasörü
WORKDIR /app

# Gereksinimleri kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proje kodlarını kopyala
COPY . .

# Varsayılan komut (Docker çalıştığında testi başlatır)
# --host parametresi ile raporları dışarıya açabiliriz
CMD ["pytest", "--alluredir=allure-results", "--clean-alluredir"]