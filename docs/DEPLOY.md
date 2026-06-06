# CityLens — Canlıya Alma Rehberi (adım adım)

Demo mimarisi: **Web (Vercel)** → **Backend (Render)** → `/detections`. Web, backend'e kısa timeout'la bağlanır; ulaşamazsa paketlenmiş yerel veriye düşer, böylece harita **asla boş kalmaz**.

> Aşağıdaki adımlar **senin** elinle (hesaplar/anahtarlar) yapılması gerekenlerdir. Kod tarafı hazırdır (`render.yaml`, `backend/Dockerfile`, web Next.js).

## 0. Ön koşul — GitHub'a push
```bash
git add -A
git commit -m "feat: CityLens MVP (backend + web + ml)"
git push origin main
```
Repo: `https://github.com/BurhanCalik/CityLens` (mevcut).

## 1. Backend → Render (Docker)
**Yol A — Blueprint (önerilen, `render.yaml` hazır):**
1. https://dashboard.render.com → **New +** → **Blueprint**.
2. CityLens reposunu seç. Render `render.yaml`'i okur → `citylens-backend` servisini oluşturur (Docker, `rootDir: backend`).
3. **Apply** → build başlar (~3–6 dk). Dockerfile `golang:1.25-alpine` kullanır (go.mod 1.25.x ile uyumlu).
4. Bitince URL'i not al: `https://citylens-backend.onrender.com`.

**Yol B — Manuel:**
1. **New +** → **Web Service** → repo seç.
2. **Root Directory:** `backend` · **Runtime:** `Docker` · **Health Check Path:** `/health/live` · **Plan:** Free → **Create**.

**Doğrula:**
```
https://citylens-backend.onrender.com/health/live      -> {"status":"alive"}
https://citylens-backend.onrender.com/detections        -> [ ... 5 temiz demo kaydı ... ]
https://citylens-backend.onrender.com/detections/stats  -> {"total":5, ...}
```
> Not: PORT'u Render otomatik enjekte eder; config `PORT`'u önce okur. DB gerekmez (detections embed'li).

## 2. Web → Vercel (Next.js)
1. https://vercel.com → **Add New** → **Project** → CityLens repo'sunu import et.
2. **Root Directory:** `web` (önemli! monorepo).
3. **Environment Variables** → ekle:
   - `NEXT_PUBLIC_API_URL` = `https://citylens-backend.onrender.com`
   - (Production + Preview + Development hepsine uygula.)
4. **Deploy** → URL: `https://citylens.vercel.app` (veya verilen ad).

> ⚠️ `NEXT_PUBLIC_*` değişkenleri **build anında** gömülür. URL'i sonradan değiştirirsen **redeploy** gerekir.

## 3. (Opsiyonel) Gerçek CV verisi
Demo `detections.json` ile hazır çalışır. Gerçek Street View taraması için:
1. Google Cloud Console → **Street View Static API**'yi etkinleştir → API key oluştur.
2. Kök `.env` dosyasına: `GOOGLE_MAPS_API_KEY=...`
3. `cd ml && python run_pipeline.py` (fetch → anonymize → detect → export).
4. `detections.json` güncellenir; backend'i yeniden deploy et (embed) **veya** `DETECTIONS_PATH` ayarla.

## 4. Demo öncesi kontrol listesi (kritik)
- [ ] **Render'ı önceden uyandır:** Free tier 15 dk boşta uyur, ilk istek ~50 sn. Sunumdan ~2 dk önce `/health/live`'ı aç (uyandır).
- [ ] Web açılışta backend'e bağlanırsa **"Canlı backend bağlı"** rozeti yeşil yanar. Uyumadıysa bile harita yerel veriyle dolu gelir (demo bozulmaz).
- [ ] `detections.json` commit'li mi? (tekrarlanabilirlik şartı)
- [ ] KVKK: `data/raw/` boş + `docs/KVKK-IMHA.md` dolduruldu mu?
- [ ] `web/public/anon/` altında yalnızca final demo kanıtları var mı? (şu an 5 dosya)

## 5. Sık sorunlar
| Sorun | Çözüm |
|---|---|
| Render build "go.mod requires go >= 1.25" | Dockerfile `golang:1.25-alpine` olmalı (zaten ayarlı). |
| Web'de pin yok | `NEXT_PUBLIC_API_URL` yanlış/eksik → düzelt + redeploy. Yine de yerel fallback çalışır. |
| Harita boş gri | İnternet yok (OSM tile) — tile'lar internet ister; pinler yine de localde gelebilir. |
| CORS hatası | Backend CORS `*` açık; URL'de `https` ve doğru host kullandığından emin ol. |
