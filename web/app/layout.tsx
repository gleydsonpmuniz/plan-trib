import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Plan Trib — Planejamento Tributário",
  description: "Comparativo Simples Nacional × Lucro Presumido × Lucro Real",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className="bg-slate-50 text-slate-900 antialiased">{children}</body>
    </html>
  );
}
