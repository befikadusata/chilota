import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { AuthProvider } from "@/lib/auth/auth-context";
import "./globals.css";
import PublicHeader from "@/components/layout/PublicHeader";
import PublicFooter from "@/components/layout/PublicFooter";

// Remove Noto_Sans_Ethiopic for now to fix the build issue
const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: {
    default: 'SurveAddis',
    template: '%s | SurveAddis',
  },
  description: "The platform connecting domestic workers with employers in Ethiopia.",
  manifest: '/manifest.json',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <meta name="theme-color" content="hsl(var(--primary))" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Ethiopic:wght@100..900&display=swap" rel="stylesheet" />
        <script
          dangerouslySetInnerHTML={{
            __html: `
              if ('serviceWorker' in navigator) {
                window.addEventListener('load', function() {
                  navigator.serviceWorker.register('/service-worker.js').then(function(registration) {
                    console.log('ServiceWorker registration successful with scope: ', registration.scope);
                  }, function(err) {
                    console.log('ServiceWorker registration failed: ', err);
                  });
                });
              }
            `,
          }}
        />
      </head>
      <body
        className={`${inter.variable} antialiased`}
        style={{ fontFamily: "'Inter', 'Noto Sans Ethiopic', Arial, sans-serif" }}
      >
        <AuthProvider>
          <div className="min-h-screen flex flex-col">
            <PublicHeader />
            <main className="flex-grow">
              {children}
            </main>
            <PublicFooter />
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}