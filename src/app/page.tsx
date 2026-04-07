'use client';

import Hero from '@/components/Hero';
import Features from '@/components/Features';
import About from '@/components/About';
import CTA from '@/components/CTA';
import Footer from '@/components/Footer';
import PageTransition from '@/components/PageTransition';

export default function HomePage() {
  return (
    <PageTransition>
      <div className="min-h-screen">
        <Hero />
        <div className="section-divider mx-6" />
        <Features />
        <div className="section-divider mx-6" />
        <About />
        <div className="section-divider mx-6" />
        <CTA />
        <Footer />
      </div>
    </PageTransition>
  );
}
