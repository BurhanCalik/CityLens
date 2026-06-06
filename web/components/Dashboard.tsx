"use client";

import dynamic from "next/dynamic";
import { useEffect, useMemo, useState } from "react";
import { loadDetections } from "@/lib/api";
import type { DataSource, Detection, Severity } from "@/lib/types";

// Leaflet touches `window`, so the map must only render on the client.
const MapView = dynamic(() => import("@/components/MapView"), {
  ssr: false,
  loading: () => <div className="map map--loading">Harita yükleniyor…</div>,
});

const CATEGORY_COLOR: Record<string, string> = {
  traffic_sign: "#2dd4bf",
  billboard: "#a78bfa",
  garbage: "#f97316",
};
const FALLBACK_COLOR = "#64748b";

// Severity is used here as a NON-ALARMIST model-confidence / verification-priority
// scale (not an emergency scale). The legend explains the colors.
const CONFIDENCE: { key: Severity; label: string; color: string }[] = [
  { key: "info", label: "Yüksek güven", color: "#22c55e" },
  { key: "warning", label: "Orta güven", color: "#f59e0b" },
  { key: "urgent", label: "Düşük güven", color: "#ef4444" },
];

function confidenceLabel(sev?: Severity): string {
  return CONFIDENCE.find((c) => c.key === (sev ?? "info"))?.label ?? "Yüksek güven";
}

function neighborhood(address?: string): string {
  if (!address) return "Diğer";
  const m = address.match(/^(.*?)\s*Mah\./);
  return (m ? m[1] : address.split(",")[0]).trim();
}

export default function Dashboard() {
  const [detections, setDetections] = useState<Detection[]>([]);
  const [source, setSource] = useState<DataSource>("offline");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [confidenceFilter, setConfidenceFilter] = useState<string>("all");
  const [selected, setSelected] = useState<Detection | null>(null);

  useEffect(() => {
    let active = true;
    loadDetections().then((res) => {
      if (!active) return;
      setDetections(res.detections);
      setSource(res.source);
    });
    return () => {
      active = false;
    };
  }, []);

  const categories = useMemo(() => {
    const map = new Map<string, { key: string; label: string; count: number }>();
    for (const d of detections) {
      const key = d.category ?? "other";
      const entry = map.get(key) ?? { key, label: d.label || "Diğer", count: 0 };
      entry.count += 1;
      map.set(key, entry);
    }
    return [...map.values()].sort((a, b) => b.count - a.count);
  }, [detections]);

  const neighborhoods = useMemo(() => {
    const map = new Map<string, number>();
    for (const d of detections) {
      const n = neighborhood(d.address);
      map.set(n, (map.get(n) ?? 0) + 1);
    }
    return [...map.entries()].map(([name, count]) => ({ name, count })).sort((a, b) => b.count - a.count);
  }, [detections]);

  const visible = useMemo(
    () =>
      detections.filter(
        (d) =>
          (categoryFilter === "all" || (d.category ?? "other") === categoryFilter) &&
          (confidenceFilter === "all" || (d.severity ?? "info") === confidenceFilter),
      ),
    [detections, categoryFilter, confidenceFilter],
  );

  return (
    <div className="app">
      <MapView detections={visible} selectedId={selected?.id ?? null} onSelect={setSelected} />

      <header className="brand">
        <div className="brand__logo">CL</div>
        <div>
          <div className="brand__title">CityLens</div>
          <div className="brand__subtitle">AI Kentsel Kusur/Denetim Haritası · Başakşehir</div>
        </div>
      </header>

      <aside className="panel">
        <span className={`panel__source panel__source--${source}`}>
          <span className="dot" />
          {source === "live" ? "Canlı backend bağlı" : "Çevrimdışı (yerel veri)"}
        </span>

        <div className="stats">
          <div className="stat stat--total">
            <div className="stat__value">{detections.length}</div>
            <div className="stat__label">Toplam tespit</div>
          </div>
          {categories.map((c) => (
            <div className="stat" key={c.key}>
              <div className="stat__value" style={{ color: CATEGORY_COLOR[c.key] ?? FALLBACK_COLOR }}>
                {c.count}
              </div>
              <div className="stat__label">{c.label}</div>
            </div>
          ))}
        </div>

        <div className="filter-group__title">Kategori</div>
        <div className="filters">
          <button
            className={`filter ${categoryFilter === "all" ? "filter--active" : ""}`}
            onClick={() => setCategoryFilter("all")}
          >
            Tümü
          </button>
          {categories.map((c) => (
            <button
              key={c.key}
              className={`filter ${categoryFilter === c.key ? "filter--active" : ""}`}
              onClick={() => setCategoryFilter(c.key)}
            >
              <span className="filter__dot" style={{ background: CATEGORY_COLOR[c.key] ?? FALLBACK_COLOR }} />
              {c.label}
            </button>
          ))}
        </div>

        <div className="filter-group__title">Doğrulama önceliği (model güveni)</div>
        <div className="filters">
          <button
            className={`filter ${confidenceFilter === "all" ? "filter--active" : ""}`}
            onClick={() => setConfidenceFilter("all")}
          >
            Tümü
          </button>
          {CONFIDENCE.map((c) => (
            <button
              key={c.key}
              className={`filter ${confidenceFilter === c.key ? "filter--active" : ""}`}
              onClick={() => setConfidenceFilter(c.key)}
            >
              <span className="filter__dot" style={{ background: c.color }} />
              {c.label}
            </button>
          ))}
        </div>

        <div className="legend">
          <div className="legend__hint">Pin rengi = saha doğrulama önceliği (model güveni):</div>
          {CONFIDENCE.map((c) => (
            <div className="legend__row" key={c.key}>
              <span className="legend__swatch" style={{ background: c.color }} /> {c.label}
            </div>
          ))}
        </div>

        {neighborhoods.length > 1 && (
          <div className="hood">
            <div className="filter-group__title">Mahalleye göre</div>
            {neighborhoods.slice(0, 4).map((n) => (
              <div className="hood__row" key={n.name}>
                <span className="hood__name">{n.name}</span>
                <span className="hood__count">{n.count}</span>
              </div>
            ))}
          </div>
        )}
      </aside>

      {selected && (
        <aside className="evidence">
          <button className="evidence__close" onClick={() => setSelected(null)} aria-label="Kapat">
            ×
          </button>
          <div className="evidence__imgwrap">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={selected.image_url} alt="Anonimleştirilmiş kanıt görseli (tespit kutulu)" />
            <span className="evidence__badge">KVKK · yüz &amp; plaka bulanık</span>
          </div>
          <div className="evidence__body">
            <span
              className="tag"
              style={{
                background: `${CATEGORY_COLOR[selected.category ?? "other"] ?? FALLBACK_COLOR}22`,
                color: CATEGORY_COLOR[selected.category ?? "other"] ?? FALLBACK_COLOR,
              }}
            >
              {selected.label}
            </span>
            <h2>{selected.label}</h2>
            <div className="evidence__score">
              Tespit güveni: <strong>{(selected.score * 100).toFixed(1)}%</strong> ·{" "}
              {confidenceLabel(selected.severity)}
            </div>
            <div className="meta">
              {selected.address && (
                <div className="meta__row">
                  <span className="meta__key">Adres</span>
                  <span className="meta__val">{selected.address}</span>
                </div>
              )}
              <div className="meta__row">
                <span className="meta__key">Konum</span>
                <span className="meta__val">
                  {selected.lat.toFixed(5)}, {selected.lng.toFixed(5)}
                </span>
              </div>
              {selected.captured_at && (
                <div className="meta__row">
                  <span className="meta__key">İşlenme</span>
                  <span className="meta__val">
                    {new Date(selected.captured_at).toLocaleString("tr-TR")}
                  </span>
                </div>
              )}
            </div>
            <p className="kvkk-note">
              Bu görsel, model çalışmadan <strong>önce</strong> insan yüzleri ve araç plakaları
              geri döndürülemez biçimde bulanıklaştırılarak işlenmiştir. CityLens yalnızca cansız
              kentsel objeleri tespit eder; kimlik tespiti, profilleme veya takip yapmaz.
            </p>
          </div>
        </aside>
      )}

      <footer className="kvkk-bar">
        <strong>KVKK uyumlu:</strong> yüz &amp; plaka bulanıklaştırma · yalnızca cansız kentsel obje ·
        ham görüntü saklanmaz
      </footer>
    </div>
  );
}
