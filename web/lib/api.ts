import type { Detection, DataSource, Stats } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export interface LoadResult {
  detections: Detection[];
  source: DataSource;
}

/**
 * Loads detections with a demo-safe strategy:
 *   1. Try the live backend (GET {API_URL}/detections) with a short timeout, so
 *      a cold Render instance can't stall the UI.
 *   2. On any failure/timeout/empty result, fall back to the JSON bundled with
 *      the web app. The map is therefore NEVER empty during a live demo.
 */
export async function loadDetections(): Promise<LoadResult> {
  if (API_URL) {
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 4000);
      const res = await fetch(`${API_URL}/detections`, {
        cache: "no-store",
        signal: controller.signal,
      });
      clearTimeout(timeout);

      if (res.ok) {
        const data = (await res.json()) as Detection[];
        if (Array.isArray(data) && data.length > 0) {
          return { detections: data, source: "live" };
        }
      }
    } catch {
      // Ignore and fall back to the bundled document.
    }
  }

  const res = await fetch("/detections.json", { cache: "no-store" });
  const data = (await res.json()) as Detection[];
  return { detections: data, source: "offline" };
}

/** Computes dashboard counters on the client so it works in offline mode too. */
export function computeStats(detections: Detection[]): Stats {
  const stats: Stats = { total: detections.length, urgent: 0, warning: 0, info: 0, avgScore: 0 };
  let scoreSum = 0;
  for (const d of detections) {
    scoreSum += d.score;
    const severity = d.severity ?? "info";
    if (severity === "urgent") stats.urgent += 1;
    else if (severity === "warning") stats.warning += 1;
    else stats.info += 1;
  }
  stats.avgScore = detections.length ? scoreSum / detections.length : 0;
  return stats;
}
