# CityLens - KVKK Uyum, Anonimleştirme ve Veri İmha Belgesi

Bu belge, hackathon ödül hakediş şartlarından biri olan **KVKK veri silme / anonimleştirme belgesi** gereksinimini karşılar.

## 1. Amaç ve Kapsam

CityLens, Google Street View kamusal sokak görüntülerinden yalnızca cansız kentsel objeleri tespit eder:

- Kent / trafik levhası
- Reklam panosu
- Çöp / atık noktası

Proje; kimlik tespiti, yüz tanıma, plaka okuma, kişi/araç takibi veya profilleme yapmaz.

## 2. Amaç Sınırlaması

Kesin yasaklar:

- Yüz tanıma veya kimlik tespiti
- Plaka okuma, OCR veya araç sahibi çıkarımı
- Kişi ya da araç takibi
- Davranış analizi veya profilleme

Model çıktısı yalnızca `id`, `lat`, `lng`, `label`, `category`, `score`, `image_url`, `address`, `severity` ve `captured_at` alanlarını içerir. Bu alanlar kişisel veri üretmek için kullanılmaz.

## 3. Anonimleştirme Sırası

Pipeline sırası bağlayıcıdır:

```text
fetch -> anonymize -> detect -> export
```

- `fetch.py`: Google Street View Static API'den görüntü indirir.
- `anonymize.py`: model çalışmadan önce yüz/plaka anonimleştirme uygular.
- `detect.py`: yalnızca `data/anon/` içindeki anonim görüntüleri okur.
- `export.py`: sadece seçilmiş, anonim ve kutulu kanıt görsellerini `web/public/anon/` altına yayınlar.

Ek güvence: Google Street View görüntüleri kaynakta Google tarafından yüz/plaka bulanıklaştırılmış olarak servis edilir. CityLens bunun üzerine `deface` ve Grounding DINO backstop yaklaşımını kurgular.

## 4. Veri Minimizasyonu

Kalıcı teslim çıktıları:

- `data/processed/detections.json`
- `backend/internal/infrastructure/detection/detections.json`
- `web/public/detections.json`
- `web/public/anon/*.jpg` içindeki anonim kanıt görselleri

Ham Street View görüntüleri `data/raw/` altında geçici tutulur, git'e girmez ve final teslim öncesi silinir.

## 5. Güvenlik

- `.env` ve API anahtarları git dışıdır.
- `data/raw/` `.gitignore` ile dışarıda tutulur.
- Ham görseller public repo'ya veya açık bulut depolamaya yüklenmez.
- Demo, canlı model çıkarımına veya ham görsele ihtiyaç duymadan anonim JSON ve kanıt görselleriyle çalışır.

## 6. İmha Kaydı

| Alan | Değer |
|---|---|
| Toplam indirilen ham görüntü sayısı | 52 |
| Anonimleştirilen görüntü sayısı | 49 |
| Public demo kanıt görseli sayısı | 5 |
| Silme komutu çalıştırıldı mı? | Evet |
| Silme tarihi/saati (UTC) | 2026-06-06T12:21:56Z |
| `data/raw/` boş doğrulandı mı? | Evet, 0 dosya |
| Uygulayan kişi | CityLens ekibi |
| İmza | Dijital teslim kaydı |

## 7. Kullanılan Silme Komutu

Windows PowerShell:

```powershell
Get-ChildItem -LiteralPath C:\dev\CityLens\data\raw -File -Recurse |
  ForEach-Object { Remove-Item -LiteralPath $_.FullName -Force }
```

Doğrulama:

```powershell
Get-ChildItem -LiteralPath C:\dev\CityLens\data\raw -File -Recurse
# Sonuç: 0 dosya
```

## 8. Sorumluluk Beyanı

CityLens ekibi olarak; modelin yalnızca cansız kentsel objeler için kullanıldığını, kişisel veri üretme veya takip amacı taşımadığını, ham görüntülerin final teslim öncesi silindiğini ve kalıcı demo çıktılarının anonim kanıt görselleriyle sınırlı olduğunu beyan ederiz.
