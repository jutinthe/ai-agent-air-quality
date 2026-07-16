import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Literature Agent for Air Quality and Health",
  description: "AI-powered literature analysis for air quality and health research"
};

export default function RootLayout({
  children
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
