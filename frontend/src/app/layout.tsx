import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Google Photos Discovery Engine — Research & Evidence Console",
  description: "Interactive Research Discovery and Qualitative Evidence Console for Google Photos Retrieval",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <div className="ambient-glow" />
        {children}
      </body>
    </html>
  );
}
