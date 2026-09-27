import type { Metadata } from "next";
import { Source_Serif_4, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";
import Providers from "@/components/Providers";
import Navbar from "@/components/Navbar";

const serif = Source_Serif_4({
  subsets: ["latin"],
  variable: "--font-serif",
  display: "swap",
});

const mono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Nano-R1",
  description: "A GRPO-tuned Qwen2.5 model that shows its work on math word problems.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${serif.variable} ${mono.variable}`}>
      <body className="min-h-screen bg-paper text-ink antialiased">
        <Providers>
          <Navbar />
          <main className="mx-auto max-w-3xl px-6 py-10">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
