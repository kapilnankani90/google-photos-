import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Memory Search — Google Photos",
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
