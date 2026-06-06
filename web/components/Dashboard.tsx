"use client";

import dynamic from "next/dynamic";
import { useEffect, useMemo, useState } from "react";
import { computeStats, loadDetections } from "@/lib/api";
import type { DataSource, Detection, Severity } from "@/lib/types";

// Leaflet touches `window`, so the map must only render on the client.
const MapView = dynamic(() => import("@/components/MapView"), {
  ssr: false,
  loading: () => <div className="map map--loading">Harita yükleniyor…</div>,
});

type Filter = "all" | Severity;

const SEVERITY_LABEL: Record<Severity, string> = {
  info: "Bilgi",
  warning: "Uyarı",
  urgent: "Acil",
};

export default function Dashboard() {
  const [detections, setDetections] = useState<Detection[]>([]);
  const [source, setSource] = useState<DataSource>("offline");
  const [filter, setFilter] = useState<Filter>("all");
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

  const stats = useMemo(() => computeStats(detections), [detections]);
  const visible = useMemo(
    () => (filter === "all" ? detections : detections.filter((d) => (d.severity ?? "info") === filter)),
    [detections, filter],
  );

  return (
    <div className="app">
      <MapView detections={visible} selectedId={selected?.id ?? null} onSelect={setSelected} />

      <header className="brand">
        <div className="brand__logo">CL</div>
        <div>
          <div className="brand__title">CityLens</div>
          <div className="brand__subtitle">Trafik levhası envanteri &amp; güvenlik denetimi · Başakşehir</div>
        </div>
      </header>

      <aside className="panel">
        <span className={`panel__source panel__source--${source}`}>
          <span className="dot" />
          {source === "live" ? "Canlı backend bağlı" : "Çevrimdışı (yerel veri)"}
        </span>

        <div className="stats">
          <div className="stat stat--total">
            <div className="stat__value">{stats.total}</div>
            <div className="stat__label">Toplam tespit</div>
          </div>
          <div className="stat stat--urgent">
            <div className="stat__value">{stats.urgent}</div>
            <div className="stat__label">Acil</div>
          </div>
          <div className="stat">
            <div className="stat__value">{stats.warning}</div>
            <div className="stat__label">Uyarı</div>
          </div>
          <div className="stat">
            <div className="stat__value">{(stats.avgScore * 100).toFixed(0)}%</div>
            <div className="stat__label">Ort. güven</div>
          </div>
        </div>

        <div className="filters">
          {(["all", "urgent", "warning", "info"] as Filter[]).map((f) => (
            <button
              key={f}
              className={`filter ${filter === f ? "filter--active" : ""}`}
              onClick={() => setFilter(f)}
            >
              {f === "all" ? "Tümü" : SEVERITY_LABEL[f]}
            </button>
          ))}
        </div>

        <div className="legend">
          <div className="legend__row">
            <span className="legend__swatch" style={{ background: "#ef4444" }} /> Acil müdahale
          </div>
          <div className="legend__row">
            <span className="legend__swatch" style={{ background: "#f59e0b" }} /> Uyarı / takip
          </div>
          <div className="legend__row">
            <span className="legend__swatch" style={{ background: "#3b82f6" }} /> Bilgi
          </div>
        </div>
      </aside>

      {selected && (
        <aside className="evidence">
          <button className="evidence__close" onClick={() => setSelected(null)} aria-label="Kapat">
            ×
          </button>
          <div className="evidence__imgwrap">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={selected.image_url} alt="Anonimleştirilmiş kanıt görseli" />
            <span className="evidence__badge">KVKK · yüz &amp; plaka bulanık</span>
          </div>
          <div className="evidence__body">
            <span className={`tag tag--${selected.severity ?? "info"}`}>
              {SEVERITY_LABEL[(selected.severity ?? "info") as Severity]}
            </span>
            <h2>{selected.label}</h2>
            <div className="evidence__score">
              Tespit güveni: <strong>{(selected.score * 100).toFixed(1)}%</strong>
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
                  <span className="meta__key">Çekim</span>
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
