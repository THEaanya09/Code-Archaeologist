import type { Metadata } from "next";
import Script from "next/script";
import ThemeProvider from "@/components/ui/ThemeProvider";
import PullStringSwitch from "@/components/ui/PullStringSwitch";
import SmoothScroll from "@/components/ui/SmoothScroll";
import Sidebar from "@/components/layout/Sidebar";
import "./globals.css";

export const metadata: Metadata = {
  title: "CodeArchaeologist — Why is it like this?",
  description:
    "Reconstruct historical software decisions from GitHub discussions using evidence-backed GraphRAG retrieval.",
  keywords: ["code archaeology", "software history", "decision graph", "Flask", "GraphRAG"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <Script
          id="theme-initializer"
          strategy="beforeInteractive"
        >{`
          try {
            var t = localStorage.getItem('ca-theme');
            if (t === 'dark') {
              document.documentElement.setAttribute('data-theme', 'dark');
            } else if (t === 'light') {
              document.documentElement.removeAttribute('data-theme');
            } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
              document.documentElement.setAttribute('data-theme', 'dark');
            }
          } catch(e) {}
        `}</Script>
      </head>
      <body className="font-sans antialiased">
        <ThemeProvider>
          <SmoothScroll>
            {/* Pull-string switch — fixed in top-right corner */}
            <div className="fixed top-0 right-6 z-50 flex items-start">
              <PullStringSwitch />
            </div>

            <div className="flex min-h-screen">
              <Sidebar />
              <main className="flex-1 ml-[230px]">{children}</main>
            </div>
          </SmoothScroll>
        </ThemeProvider>
      </body>
    </html>
  );
}
