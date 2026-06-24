import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FlowSight AI | Operations control tower",
  description: "Know what will go wrong next, what it will cost, and who should act now."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
