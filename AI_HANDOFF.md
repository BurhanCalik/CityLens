# CityLens — AI Geliştirme El Kitabı (Cursor Ajanı İçin Brifing)

> **Bu dosya, CityLens projesinde Cursor içinde çalışacak geliştirici ajan (sen) içindir.** Aynı modeli (Opus 4.8) kullanıyoruz. Kullanıcı CV/AI tarafında yeni. Her şey **küçük/orta adımlarla** ilerleyecek. Önce çalışan en basit uçtan uca sürüm ("yürüyen iskelet"), sonra derinleştirme. 

---

## 0) Proje özeti
CityLens: Google Street View sokak görüntülerinden **bir kentsel nesneyi** Hugging Face görü modeliyle otomatik tespit edip sonuçları bir **harita** üzerinde gösteren web uygulaması. Kamusal fayda: belediye/vatandaş için otomatik şehir denetimi.

> ⚠️ **Hedef nesne (TBD):** Etkinlik verisi/çizelgesi gelince kullanıcı "şunu tespit edeceğiz" diyecek veya ona sen sor (ör. çukur, tabela, çöp). Pipeline **nesneden bağımsızdır** — sadece bu tek değişkeni doldur, gerisi aynı kalır.

## 1) Kullanıcı & çalışma tarzı
- CV/AI'da yeni → adımları açıkla, basit tut.
- Tüm geliştirme Cursor'da yapılacak (kural).
- Küçük kapsam, önce uçtan uca iskelet, sonra iyileştir.
- **Her anlamlı adımdan sonra commit** (süreç puanlanıyor).(Kullanıcı commitleyecek)

## 2) BAĞLAYICI KURALLAR (ihlali = puan kaybı / diskalifiye)

### Stack (sapma kabul edilmez)
- **Web:** Next.js → **Vercel**
- **Mobil:** Expo — **ŞİMDİLİK YAPILMAYACAK (sadece web)**
- **Backend:** Go, **masterfabric-go mimarisi ZORUNLU** (`C:\Users\scadenza\Downloads\masterfabric-go-main\masterfabric-go-main`). Kendi mimarini kurmak **YASAK**. Onun `.cursor/rules` ve konvansiyonlarına birebir uy. → **Render**
- **AI model & veri seti:** **Hugging Face** platformu (zorunlu)
- **Harici veri:** Google Street View API (ilk 10.000 istek ücretsiz)
- **Hosting:** Web=Vercel, Backend=Render.com

### Süreç & AI
- Cursor IDE zorunlu; **Cursor Ruleset** zorunlu (`.cursor/rules/citylens-hackathon.mdc` mevcut).
- README'de: hangi **AI araçları / prompt teknikleri / Cursor özellikleri** nasıl kullanıldı — detaylı.
- 💡 **BONUS PUAN:** Cursor **CLI & SDK** kullan + README'de belgele → AI Adaptasyonu ekstra puan.

### KVKK (kırmızı çizgi — diskalifiye)
- Modeller yalnızca **cansız kentsel objeler** (tabela, çöp kutusu, hasarlı yol vb.).
- Kimlik tespiti / yüz tanıma / plaka **okuma** / kişi-araç takibi / profilleme **YASAK**.
- İnsan yüzleri ve araç plakaları, **model çalışmadan ÖNCE geri döndürülemez** biçimde bulanıklaştırılacak.
- Ham görüntüler: public repo'ya / şifresiz cloud'a **ASLA**. `.env` + `.gitignore`.
- Etkinlik sonunda tüm ham görüntüler **silinecek + belgelenecek** (`docs/KVKK-IMHA.md`).

### Ödül şartı (4'ü de zorunlu)
Canlı demo · Tekrarlanabilir sonuç · Çalışan kaynak kod (commit geçmişiyle) · KVKK silme/anonimleştirme belgesi.

### Puanlama (100)
Teknik Çalışırlık **30** (eşitlikte belirleyici) · Doğruluk **25** · Kamu Faydası **20** · AI Adaptasyon **10** · KVKK **10** · Sunum/README **5**.

## 3) masterfabric-go — nasıl çalışıyor (incelendi)
- **Clean/Hexagonal + DDD.** Katmanlar: `domain` (saf Go, bağımlılık yok) → `application` (usecase+dto) → `infrastructure` (http/postgres/redis/kafka). Router: **Chi**.
- **Postgres OPSİYONEL:** DB yoksa server yine kalkar (`db=nil`); IAM/tenant endpoint'leri çalışmaz ama `/health/live` çalışır. Kafka default **in-process** (`KAFKA_ENABLED=false`). Redis opsiyonel.
- **CORS zaten `*` açık** → Vercel'den doğrudan çağrılabilir.
- **Yeni özellik = dikey dilim:** `domain/<ctx>/{model,repository}` + `application/<ctx>/{usecase,dto}` + `infrastructure/http/handler/<ctx>` + `router.go`'ya route. Konvansiyonlar (`backend/.cursor/rules`): context ilk parametre, error son + `fmt.Errorf("...: %w", err)` ile wrap, UUID, UTC, DI + `NewXxx`, interface domain'de.
- **Render PORT GOTCHA:** config `SERVER_PORT` okur (default 8080), `SERVER_HOST=0.0.0.0`. Render `PORT` inject eder. Çözüm: Render env'e `SERVER_PORT` = Render'ın verdiği port (ör. 10000) koy; **veya** `config.go`'da tek satır `PORT` fallback ekle.
- **Dockerfile var** (`./cmd/server` build, 8080 expose) → Render'da "Docker" runtime ile deploy.

## 4) CityLens mimari kararı (DEMO-GÜVENLİ + kurallara uygun)
"detections" özelliğini masterfabric katmanlarıyla ekle, AMA demo'yu DB'ye bağımlı yapma:
- `domain/detection/model.go` → `Detection{ ID, Lat, Lng, Label, Score, ImageURL, CreatedAt }`
- `domain/detection/repository.go` → `DetectionRepository` interface (`List(ctx)` ...)
- `infrastructure/detection/json_repo.go` → JSON dosyasından okuyan impl (demo için bulletproof). **Ham veri değil, ANONİM sonuç JSON'u**: `data/processed/detections.json`
- `application/detection/usecase/list_detections.go` (+ dto)
- `infrastructure/http/handler/detection/handler.go` → `GET /detections`
- `router.go` → `r.Get("/detections", detectionHandler.List)` — **`/api/v1` grubunun DIŞINDA** (JWT/tenant gerektirmesin, `/health` gibi)
- (Opsiyonel, zaman varsa) `infrastructure/postgres/detection/...` → Postgres impl.

**Neden:** Server hiçbir altyapı olmadan kalkar, Render'da DB'siz deploy olur, canlı demo çökmez. Repository pattern korunduğu için sonradan Postgres'e geçmek tek satır.

## 5) CV pipeline (Hugging Face) — `ml/` klasörü
Akış (nesne agnostik). **KVKK: detect.py SADECE anonimleştirilmiş görselle çalışır.**
1. `fetch.py` — Street View Static API'den görsel indir (önce `/metadata` ile var mı kontrol et = kota tasarrufu). → `data/raw/` **(.gitignore)**
2. `anonymize.py` — **deface** ile yüzleri bulanıklaştır + plakaları tespit edip blur'la (HF plaka modeli **veya** OWLv2 "license plate" prompt). → `data/anon/`
3. `detect.py` — Hugging Face `transformers` object detection:
   - **En hızlı/uyumlu (eğitim YOK):** pretrained DETR `facebook/detr-resnet-50` **veya** zero-shot **OWLv2** `google/owlv2-base-patch16-ensemble` → `candidate_labels=["<hedef nesne>"]`.
   - **Doğruluk artışı (zaman varsa):** HF dataset ile fine-tune.
4. `export.py` — tespitleri → `data/processed/detections.json` (backend bunu servis eder).
- **Kurulum:** `pip install transformers timm pillow` (torch + deface zaten kurulu). Modeli **erken indir** (OWLv2 büyük; wifi yavaşsa DETR daha küçük ~160MB).
- **Çıktı sözleşmesi:** `detections.json = [{ "lat":.., "lng":.., "label":"..", "score":0.xx, "image_url":"/anon/0001.jpg" }]`

## 6) Web (Next.js) — `web/` klasörü → Vercel
- `pnpm create next-app@latest web` (App Router, TS).
- Harita: **react-leaflet** (ücretsiz, OSM), Başakşehir merkezli.
- Backend'den `GET <RENDER_URL>/detections` → pin'le. Pin tıkla → anonim görsel + kutu + etiket + skor + adres. Sayaç/filtre ("toplam", "acil").
- env: `NEXT_PUBLIC_API_URL` (Render backend), gerekirse `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` (kısıtlı).

## 7) Adım adım görev listesi (HER adımda commit)
0. **İskelet:** `backend/` (masterfabric kopyala — kendi `.cursor/rules`'uyla), `web/`, `ml/`, `data/`, `docs/`. Kök `.gitignore` + `.env.example`.
   - commit: `chore: monorepo skeleton + gitignore` → `chore: add masterfabric-go backend base`
1. **Backend ayağa:** `cd backend && go run ./cmd/server` → `GET /health/live` = `{"status":"alive"}`. commit: `chore: boot backend, health ok`
2. **Web iskeleti:** next-app + boş Başakşehir haritası, `pnpm dev` çalışsın. commit: `feat(web): map homepage`
3. **Detections feature** (Bölüm 4) + 3-5 sahte kayıtlı `detections.json`. `GET /detections` JSON dönsün. commit: `feat(backend): detections endpoint (json repo)`
4. **Web ↔ backend bağla:** harita `/detections`'ı çizsin (sahte veriyle bile). commit: `feat(web): render detections on map` ← 🎉 **YÜRÜYEN İSKELET**
5. **CV:** fetch → anonymize → detect → export = gerçek `detections.json`. commit'ler: `feat(ml): streetview fetch`, `feat(ml): deface+plate anonymize`, `feat(ml): HF detection`, `feat(ml): export detections`
6. **Gerçek veriyle uçtan uca.** Doğruluğu artır (model/threshold/fine-tune). commit'ler.
7. **Deploy:** backend→Render (Dockerfile, env, PORT gotcha), web→Vercel (`NEXT_PUBLIC_API_URL`). commit: `chore: deploy configs`
8. **Cila + README** (AI kullanımı + Cursor CLI/SDK) + **KVKK imha belgesi** + demo provası. **Ham veriyi sil + belgele.** commit'ler.

## 8) README zorunlu içerik
Problem/fayda · mimari diyagram · stack · kurulum/çalıştırma · **AI kullanımı** (hangi Cursor özellikleri, prompt teknikleri, ruleset, **Cursor CLI/SDK** — örneklerle) · KVKK notu + imha belgesi linki · demo linki/gif · takım.

## 9) Ne zaman kullanıcıya sor
- **Hedef nesne** kesinleşmeden CV'de model `candidate_labels`'ı doldurma — kullanıcı söyleyince gir. **Kullanıcıya sen de sorabilirsin ne yapılack nasıl yapılacak ama ona açıklamalarıyla bilrikte yaz neyin ne olduğunu söyleyerek ve senin tavsiyelerinle**
- Etkinlikte **bonus modül** önerilirse entegre et.

## ✅ Tanım: Bitti (ödül uygunluğu)
☐ Canlı demo (Vercel web + Render backend çalışıyor) ☐ Tekrarlanabilir (`detections.json` + commit geçmişi) ☐ Çalışan kaynak kod ☐ KVKK imha belgesi ☐ README (AI dökümantasyonu) ☐ `.cursor` ruleset ☐
