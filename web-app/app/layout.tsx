import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import NavigationBar from "./_components/navigation-bar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Providers } from "./providers";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Attention Agent",
  description: "Focus Monitoring Results Display",
};
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <Providers>
        <ScrollArea>
          <div className="mx-auto max-w-7xl px-16 py-5 space-y-6">
            <header>
              <NavigationBar />
            </header>

            <main>{children}</main>
          </div>
        </ScrollArea>
        </Providers>
      </body>
    </html>
  )
}
