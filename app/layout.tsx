import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Script from "next/script";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "AgentSuite",
  description: "AI-powered business automation",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${inter.variable} font-sans antialiased text-white`}
      >
        {/* 🔐 GOOGLE AUTH */}
        <Script
          src="https://accounts.google.com/gsi/client"
          strategy="afterInteractive"
        />

        {/* 🌌 BACKGROUND ROOT */}
        <div className="relative min-h-screen overflow-hidden bg-[#050816]">

          {/* 🔥 BASE GRADIENT (clean + controlled) */}
          <div className="absolute inset-0 bg-[linear-gradient(180deg,#050816_0%,#070b18_100%)]" />

          {/* 🔥 RADIAL LIGHTS (lepsza kompozycja) */}
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_25%_15%,rgba(59,130,246,0.18),transparent_35%),radial-gradient(circle_at_75%_20%,rgba(168,85,247,0.18),transparent_35%)]" />

          {/* 🔥 GRID */}
          <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.025)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.025)_1px,transparent_1px)] bg-[size:28px_28px] [mask-image:radial-gradient(ellipse_at_center,black_55%,transparent_90%)]" />

          {/* 🔥 FLOATING LIGHTS (bardziej naturalne) */}
          <div className="pointer-events-none absolute top-[10%] left-[15%] h-[320px] w-[320px] rounded-full bg-blue-500/20 blur-[120px] animate-[pulse_6s_ease-in-out_infinite]" />

          <div className="pointer-events-none absolute top-[20%] right-[10%] h-[320px] w-[320px] rounded-full bg-purple-500/20 blur-[120px] animate-[pulse_7s_ease-in-out_infinite]" />

          {/* 🔥 CENTER AMBIENT LIGHT */}
          <div className="pointer-events-none absolute left-1/2 top-1/3 h-[600px] w-[900px] -translate-x-1/2 rounded-full bg-blue-500/10 blur-[160px]" />

          {/* 🔥 COLORED NOISE (KEY UPGRADE) */}
          <div className="pointer-events-none absolute inset-0 opacity-[0.045] mix-blend-soft-light">
            <div className="absolute inset-0 bg-[('/noise.png')]" />
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-transparent to-purple-500/10" />
          </div>

          {/* 🔥 VIGNETTE (dodaje depth) */}
          <div className="pointer-events-none absolute inset-0 [mask-image:radial-gradient(circle_at_center,transparent_55%,black)] bg-black/40" />

          {/* 🔥 CONTENT */}
          <div className="relative z-10 min-h-screen">
            {children}
          </div>

        </div>
      </body>
    </html>
  );
}