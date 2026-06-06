# CityLens Jüri Sunum Notları

## 30 Saniyelik Açılış

CityLens, belediyelerin sokak seviyesinde kentsel obje envanterini daha hızlı çıkarması için geliştirdiğimiz AI destekli denetim haritasıdır. Google Street View görüntülerini kullanıyoruz; model çalışmadan önce yüz ve plakaları anonimleştiriyoruz; ardından kent levhası, reklam panosu ve atık gibi cansız objeleri tespit edip haritada kanıt görseliyle gösteriyoruz.

## Demo Sırası

1. Haritayı aç.
2. Sağ üstte veri kaynağı rozetini göster: canlı backend bağlıysa canlı, değilse offline fallback.
3. Toplam tespit sayısını ve kategori sayaçlarını göster.
4. Önce `Çöp / atık` filtresini aç, `0006` veya `0098` kanıtını göster.
5. Sonra `Reklam panosu` filtresini aç, `0019` veya `0064` kanıtını göster.
6. Son olarak `Kent levhası` filtresini aç, `0007` kanıtını göster.
7. Kanıt panelinde şu sırayı söyle: kategori, skor, adres, koordinat, anonimleştirme notu.

## Jüriye Anlatılacak Ana Cümleler

- "Bu bir şikayet uygulaması değil; belediye için proaktif saha denetim haritası."
- "Canlı demo model inference'a bağlı değil. Önceden üretilmiş ve doğrulanmış `detections.json` backend'e embed edildiği için demo tekrarlanabilir."
- "Model adaylarını olduğu gibi göstermiyoruz. Yanlış ve düşük güvenli görselleri public demo setinden çıkarıyoruz; bu yüzden gösterdiğimiz fotoğraflar insan-onaylı kanıt seti."
- "Amaç kimlik tespiti değil. Sadece cansız kentsel objeleri hedefliyoruz."
- "Ham Street View görüntüleri git'e girmiyor ve etkinlik sonunda siliniyor. Kalıcı çıktı yalnızca anonim kanıt ve JSON sonuçları."

## Fotoğraflar Nereden Geliyor?

Kısa cevap:

> "Fotoğraflar Google Street View Static API'den geliyor. `ml/points.json` içinde Başakşehir koordinatlarımız var. `fetch.py` önce ücretsiz metadata kontrolü yapıyor, sonra görüntüyü indiriyor. `anonymize.py` modelden önce yüz/plaka anonimleştirme yapıyor. `detect.py` Hugging Face Grounding DINO ile cansız kentsel objeleri buluyor. `export.py` de kutulu kanıt görsellerini ve `detections.json` dosyasını üretiyor."

## Sistem Mimarisi Nasıl?

Kısa cevap:

> "Üç katman var: CV pipeline, Go backend ve Next.js web. CV pipeline sonucu `detections.json` üretiyor. Go backend bunu embed ederek `/detections` ve `/detections/stats` endpoint'lerinden servis ediyor. Next.js harita önce canlı backend'e bağlanıyor; bağlantı yoksa paketlenmiş JSON fallback ile yine dolu açılıyor."

## KVKK Sorusu Gelirse

> "Yüz tanıma, plaka okuma, kişi/araç takibi veya profilleme yok. Google Street View zaten kaynakta yüz/plaka bulanıklaştırıyor; biz ayrıca deface ve Grounding DINO backstop ile model öncesi anonimleştirme kurguladık. Ham görüntüler `data/raw/` altında geçici tutuluyor, git'e girmiyor ve finalde imha ediliyor. İmha kaydı `docs/KVKK-IMHA.md` içinde."

## AI Adaptasyonu Sorusu Gelirse

> "Cursor'u sadece kod yazdırmak için değil, süreç mimarisi için kullandık. `.cursor/rules/citylens-hackathon.mdc` ile hackathon stack, KVKK ve output sözleşmesini agent'a bağladık. Backend tarafında masterfabric-go ruleset'lerine uyduk. Ayrıca `tools/cursor/summarize_detections.mjs` ile Cursor SDK kullanan bir belediye raporu otomasyonu ekledik; `cursor-agent` CLI akışını da dokümante ettik."

## Doğruluk Sorusu Gelirse

> "Bu hackathon sürümünde zero-shot Grounding DINO kullandık. Dolayısıyla amaç fine-tuned üretim modeli değil, uçtan uca çalışan sorumlu AI prototipi. Yanlış adayları public demo setinden çıkardık; finalde gösterilen 5 kayıt insan-onaylı temiz kanıt setidir. Üretim yol haritasında belediye etiketli veriyle fine-tune ve daha büyük tarama alanı var."

## Kapanış

CityLens'in değeri tek bir fotoğraftan ibaret değil: veri kaynağından anonimleştirmeye, AI tespitinden backend API'ye, harita demosundan KVKK imha belgesine kadar uçtan uca çalışan bir kamu faydası prototipi olması.
