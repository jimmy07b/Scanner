import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://scanner-ywmt.vercel.app";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "RootLayer | Precision Security Analysis for Websites, URLs & Files",
    template: "%s | RootLayer Security",
  },
  description:
    "Enterprise-grade automated cybersecurity intelligence: live website posture audits, real-time URL threat detection, and static file malware scanning.",
  keywords: [
    "cybersecurity scanner",
    "website vulnerability audit",
    "URL threat check",
    "phishing detector",
    "file malware scanner",
    "SSL certificate check",
    "security headers analysis",
    "DevSecOps",
    "RootLayer",
  ],
  authors: [{ name: "RootLayer Security Team" }],
  creator: "RootLayer",
  publisher: "RootLayer",
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: siteUrl,
    title: "RootLayer | Precision Security Analysis for Websites, URLs & Files",
    description:
      "Enterprise-grade automated cybersecurity intelligence: live website posture audits, real-time URL threat detection, and static file malware scanning.",
    siteName: "RootLayer",
    images: [
      {
        url: `${siteUrl}/hero-cyber-bg.jpg`,
        width: 1200,
        height: 630,
        alt: "RootLayer Cybersecurity Analysis Engine",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "RootLayer | Precision Security Analysis",
    description:
      "Enterprise-grade automated cybersecurity intelligence: live website posture audits, real-time URL threat detection, and static file malware scanning.",
    images: [`${siteUrl}/hero-cyber-bg.jpg`],
  },
};

const jsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": `${siteUrl}/#organization`,
      name: "RootLayer",
      url: siteUrl,
      logo: `${siteUrl}/hero-cyber-bg.jpg`,
      description:
        "Precision automated cybersecurity intelligence, website audits, URL threat detection, and file security scanning.",
    },
    {
      "@type": "WebApplication",
      "@id": `${siteUrl}/#application`,
      name: "RootLayer Security Engine",
      url: siteUrl,
      applicationCategory: "SecurityApplication",
      operatingSystem: "All",
      offers: {
        "@type": "Offer",
        price: "0",
        priceCurrency: "USD",
      },
      featureList: [
        "Live Website SSL & Security Header Auditing",
        "Real-Time Phishing & Malicious URL Threat Detection",
        "Static Archive, Executable, & Document Malware Scanner",
        "Automated Vulnerability Scoring and Evidence Logs",
      ],
    },
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body className="min-h-screen flex flex-col bg-[#090d16] text-slate-100 antialiased">
        <Navbar />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
