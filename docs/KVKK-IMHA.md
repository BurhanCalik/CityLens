# CityLens — KVKK Uyum, Anonimleştirme ve Veri İmha Belgesi

> Bu belge, ödül hak ediş şartlarından biri olan **"KVKK veri silme/anonimleştirme belgesi"** gereksinimini karşılar. Etkinlik sonunda **Silme Kayıt Tablosu** doldurulup imzalanır.

## 1. Amaç ve Kapsam
CityLens, Google Street View kamusal sokak görüntülerinden **yalnızca cansız kentsel objeleri** (ör. trafik levhası) otomatik tespit eder. Amaç; belediye/vatandaş için otomatik, tekrarlanabilir kentsel denetimdir.

## 2. Amaç Sınırlaması (kesin yasaklar)
Aşağıdakiler proje kapsamında **YASAKTIR** ve hiçbir kod yolunda uygulanmaz:
- Yüz tanıma / kimlik tespiti
- Plaka **okuma** / OCR / araç sahibi tespiti
- Kişi veya araç **takibi**, profilleme, davranış analizi

Model girdisi yalnızca anonimleştirilmiş görüntüdür; çıktı yalnızca `{lat, lng, label, score, image_url}` alanlarını içerir — kişisel veri içermez.

## 3. Zorunlu Anonimleştirme (model çalışmadan ÖNCE, geri döndürülemez)
Sıralama **bağlayıcıdır**: `fetch → anonymize → detect → export`. `detect.py` yalnızca `data/anon/` klasörünü okur; `data/anon/` boşsa **çalışmayı reddeder** (KVKK STOP).

İki katmanlı (defense-in-depth) anonimleştirme — `ml/anonymize.py`:
1. **deface**: amaca özel yüz bulanıklaştırma (yüksek geri çağırım), alt süreç olarak.
2. **Grounding DINO backstop**: `"human face. license plate."` istemiyle tespit edilen bölgelere PIL ile güçlü Gaussian blur.

Blur, piksel düzeyinde ve **geri döndürülemez** biçimde uygulanır; orijinal pikseller anonim çıktıda yer almaz.

**Ek güvence (kaynakta anonimleştirme):** Google Street View görüntüleri zaten kaynakta (Google tarafından) yüz ve plaka bulanıklaştırılmış olarak servis edilir. CityLens bunun üzerine kendi deface + Grounding DINO pasını ekler — yani anonimleştirme **iki bağımsız katmanda** garanti altına alınır.

## 4. Veri Minimizasyonu
- Kalıcı çıktı: yalnızca `data/processed/detections.json` (anonim sonuç) + anonim kanıt görselleri (`web/public/anon/`).
- Ham görüntüler (`data/raw/`) yalnızca işleme anında diskte tutulur, sonunda silinir.

## 5. Güvenlik
- Ham görüntüler **asla** public repo'ya / şifresiz cloud'a yüklenmez. `data/raw/` ve tüm `**/raw/` yolları `.gitignore` ile hariç tutulur.
- API anahtarları yalnızca `.env` içinde tutulur (`.env` gitignored). Koda secret yazılmaz. `NEXT_PUBLIC_` yalnızca kısıtlı tarayıcı anahtarı için kullanılır.
- Street View kotası korunur: indirmeden önce ücretsiz `/metadata` ile görüntü varlığı kontrol edilir.

## 6. Veri İmha Prosedürü (etkinlik sonunda uygulanır)
Ham görüntüleri kalıcı sil (Windows PowerShell):

```powershell
Remove-Item -Recurse -Force C:\dev\CityLens\data\raw\*
```

Doğrula (boş dönmeli):

```powershell
Get-ChildItem -Recurse C:\dev\CityLens\data\raw
```

> İsteğe bağlı ek güvence: geri kurtarmayı zorlaştırmak için diskte güvenli silme aracı kullanılabilir. Ham görüntüler git geçmişine hiç girmediği için repo tarafında ek işlem gerekmez.

## 7. Silme Kayıt Tablosu (etkinlik sonunda doldurulur)

| Alan | Değer |
|---|---|
| Toplam indirilen ham görüntü sayısı | __________ |
| Anonimleştirilen görüntü sayısı | __________ |
| Silme komutu çalıştırıldı mı? (E/H) | __________ |
| Silme tarihi/saati (UTC) | __________ |
| `data/raw/` boş doğrulandı mı? (E/H) | __________ |
| Uygulayan kişi (ad-soyad) | __________ |
| İmza | __________ |

## 8. Sorumluluk Beyanı
CityLens ekibi olarak; geliştirme sürecinin tamamında insan onuru ve mahremiyetinin verimlilik kaygısının önünde tutulduğunu, modelin yalnızca cansız kentsel objeler için kullanıldığını ve yukarıdaki imha prosedürünün uygulandığını beyan ederiz.
