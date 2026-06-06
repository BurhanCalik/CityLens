import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CityLens — Yapay Zekâ ile Kentsel Denetim",
  description:
    "Belediye için otomatik trafik levhası envanteri ve eksik/devrilmiş/görünürlüğü kapalı levha aday haritası. KVKK uyumlu, yapay zekâ destekli kentsel denetim.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="tr">
      <body>{children}</body>
    </html>
  );
}
