## Etsy Ürün Analiz ve Öneri Sistemi

Bu repo, Etsy ürünlerini toplayıp temizleyen, temel metin işleme (NLP) ve analiz adımlarını içeren örnek bir çalışmadır. Amaç: sade, çalışabilir bir akış sunmak.

### Kurulum
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### Hızlı Başlangıç
```bash
# Klasörleri hazırla
python days/day01_setup.py

# Örnek veri çek (kategori/arama URL’si verin)
python days/day02_scrape_sample.py --category_url "https://www.etsy.com/search?q=poster"

# Sayfalı çekim (isteğe bağlı)
python days/day03_scrape_paged.py --category_url "https://www.etsy.com/search?q=poster" --max_pages 5

# Temizleme
python days/day04_clean_data.py --input data/raw/day03_products.csv

# Analiz (özet ve grafik)
python days/day05_analysis.py --input data/processed/day04_clean.csv
```

### Yapı
```
 days/      # Gün bazlı komut dosyaları
 src/       # Yardımcı modüller (scrape, io, text, erank)
 data/      # Ham/işlenmiş veri klasörleri
 outputs/   # Özet rapor ve grafikler
 tests/     # Basit birim testleri
```

### Notlar
- Etsy isteklerini sınırlayabilir; `--delay` ile nazik olun.
- eRank anahtar kelimeleri için `data/erank_keywords.csv` kullanılır (opsiyonel).
- Eğitim/örnek amaçlıdır.

### Test
```bash
pytest -q
```

Lisans: MIT
