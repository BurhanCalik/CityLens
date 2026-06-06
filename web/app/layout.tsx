import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CityLens — AI Kentsel Kusur/Denetim Haritası",
  description:
    "Sokak görüntülerinden trafik levhası, reklam panosu ve atık gibi kentsel objeleri otomatik tespit eden, KVKK uyumlu, proaktif çok kategorili belediye denetim haritası.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="tr">
      <body>{children}</body>
    </html>
  );
}
