#!/usr/bin/env bash

# Projenin bulunduğu klasöre geç.
cd "$(dirname "$0")" || exit 1

echo "Dash testleri başlatılıyor..."

# Windows Git Bash ve Linux/macOS sanal ortamlarını destekle.
if [ -f ".venv/Scripts/activate" ]; then
    source ".venv/Scripts/activate"
elif [ -f ".venv/bin/activate" ]; then
    source ".venv/bin/activate"
else
    echo "Hata: .venv sanal ortamı bulunamadı."
    exit 1
fi

echo "Sanal ortam etkinleştirildi."
echo "Kullanılan Python: $(python --version)"

# Test paketini çalıştır.
python -m pytest tests/test_app.py -v
TEST_STATUS=$?

# Sonuca göre yalnızca 0 veya 1 döndür.
if [ "$TEST_STATUS" -eq 0 ]; then
    echo "Tüm testler başarıyla tamamlandı."
    exit 0
else
    echo "Bir veya daha fazla test başarısız oldu."
    exit 1
fi