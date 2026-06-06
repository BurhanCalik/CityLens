"use client";

import { MapContainer, TileLayer, Marker, Tooltip } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import type { Detection } from "@/lib/types";

// Başakşehir / İstanbul — the demo audit area.
const CENTER: [number, number] = [41.0931, 28.802];

const iconCache: Record<string, L.DivIcon> = {};
function pinIcon(severity: string): L.DivIcon {
  const sev = severity || "info";
  if (!iconCache[sev]) {
    iconCache[sev] = L.divIcon({
      className: "pin-wrap",
      html: `<span class="pin pin--${sev}"></span>`,
      iconSize: [22, 22],
      iconAnchor: [11, 11],
      tooltipAnchor: [0, -14],
    });
  }
  return iconCache[sev];
}

interface MapViewProps {
  detections: Detection[];
  selectedId: string | null;
  onSelect: (d: Detection) => void;
}

export default function MapView({ detections, selectedId, onSelect }: MapViewProps) {
  return (
    <MapContainer center={CENTER} zoom={13} className="map" scrollWheelZoom>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> katkıda bulunanlar'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {detections.map((d) => (
        <Marker
          key={d.id}
          position={[d.lat, d.lng]}
          icon={pinIcon(d.severity ?? "info")}
          zIndexOffset={selectedId === d.id ? 1000 : 0}
          eventHandlers={{ click: () => onSelect(d) }}
        >
          <Tooltip direction="top" opacity={1}>
            <strong>{d.label}</strong> · {(d.score * 100).toFixed(0)}%
          </Tooltip>
        </Marker>
      ))}
    </MapContainer>
  );
}
