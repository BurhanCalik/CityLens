export type Severity = "info" | "warning" | "urgent";

/** A single anonymized urban-object detection, matching the backend contract. */
export interface Detection {
  id: string;
  lat: number;
  lng: number;
  label: string;
  score: number;
  image_url: string;
  address?: string;
  severity?: Severity;
  captured_at?: string;
}

export interface Stats {
  total: number;
  urgent: number;
  warning: number;
  info: number;
  avgScore: number;
}

export type DataSource = "live" | "offline";
