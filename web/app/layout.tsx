import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CityLens — Yapay Zekâ ile Kentsel Denetim",
  description:
    "Sokak görüntülerinden kentsel objeleri otomatik tespit eden, KVKK uyumlu kamusal denetim haritası.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="tr">
      <body>{children}</body>
    </html>
  );
}
