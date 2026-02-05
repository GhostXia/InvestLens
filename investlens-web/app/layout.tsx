import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider";

// Font configurations optimizing for performance (subsets: latin)
const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

/**
 * Global Metadata Configuration
 * Defines the default SEO tags for the application.
 */
export const metadata: Metadata = {
  title: "InvestLens | AI-Native Investment Analysis",
  description: "Advanced financial analysis powered by multi-model consensus.",
};

/**
 * RootLayout Component
 * 
 * The top-level layout wrapper for the entire Next.js application.
 * Responsibilities:
 * 1. Applies global font variables (Geist Sans/Mono).
 * 2. Injects the `ThemeProvider` to manage dark/light mode context application-wide.
 * 3. Suppresses hydration warnings related to theme attributes.
 * 
 * @param {Readonly<{ children: React.ReactNode }>} props - The page content
 * @returns {JSX.Element} The HTML shell
 */
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
