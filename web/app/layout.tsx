import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "築地・明石町 歴史アトラス | tsukiji-atlas",
  description:
    "築地・明石町エリアの名所旧跡・文化財・記念碑を時代別・分野別に可視化する地図。",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
