# CityLens × Cursor CLI & SDK (AI Adaptasyonu — Bonus)

Bu klasör, CityLens'in **Cursor CLI ve SDK** ile nasıl otomatikleştirildiğini gösterir. Amaç hackathon'un "AI Adaptasyonu" bonus puanı: agentic akışı yalnızca IDE içinde değil, **kod/otomasyon** seviyesinde de kullanmak.

## 1. Cursor SDK — `summarize_detections.mjs`
`detections.json`'u okur ve Cursor SDK (`@cursor/sdk`) ile belediyeye yönelik Türkçe bir önceliklendirme raporu üretip `docs/REPORT.md`'ye yazar.

```bash
cd tools/cursor
pnpm install                # @cursor/sdk
export CURSOR_API_KEY=cursor_...    # https://cursor.com/dashboard/integrations
pnpm summarize              # -> docs/REPORT.md
```

Kullanılan desen (skill'e uygun): tek-atış `Agent.prompt(...)` (otomatik dispose), `CursorAgentError` (başlamadı) ile `result.status === "error"` (çalıştı ama hata) ayrımı ve anlamlı çıkış kodları (1/2/0).

## 2. Cursor CLI — `cursor-agent`
Tekrarlanabilir görevleri terminalden çalıştırmak için:

```bash
# Kurulum (bir kez):
#   curl https://cursor.com/install -fsS | bash      (mac/Linux)
#   irm https://cursor.com/install.ps1 | iex          (Windows PowerShell)

# Non-interactive (print) modunda örnek:
cursor-agent -p "data/processed/detections.json'u oku; en düşük güvenli 3 tespiti \
listele ve neden acil incelenmeli açıkla."

# Belirli bir modelle:
cursor-agent -p --model composer-2.5 "README'deki kurulum adımlarını doğrula"
```

## 3. Agentic ruleset (IDE içi)
- `.cursor/rules/citylens-hackathon.mdc` — bağlayıcı hackathon kuralları (her promptta).
- `backend/.cursor/rules/*.mdc` — masterfabric-go konvansiyonları; backend dikey dilimi bunlara birebir uyularak üretildi.

> Not: SDK/CLI komutları `CURSOR_API_KEY` ve internet gerektirir; demo bunlara bağımlı değildir (sadece bonus dökümantasyon/otomasyon).
