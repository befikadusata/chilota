import type { Metadata } from "next";
import { Inter, Noto_Sans_Ethiopic } from "next/font/google";
import { AuthProvider } from "@/lib/auth/auth-context";
import "./globals.css";
import PublicHeader from "@/components/layout/PublicHeader";
import PublicFooter from "@/components/layout/PublicFooter";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

const noto_sans_ethiopic = Noto_Sans_Ethiopic({
  subsets: ["latin"],
  variable: "--font-noto-sans-ethiopic",
});

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
        className={`${inter.variable} ${noto_sans_ethiopic.variable} antialiased`}
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
