'use client';

import { motion } from 'framer-motion';
import { ArrowRight, Bot, ExternalLink } from 'lucide-react';
import Link from 'next/link';
import { SignInButton, useAuth } from '@clerk/nextjs';
import CodeBlock from './CodeBlock';

const fadeUp = {
  initial: { opacity: 0, y: 24 },
  animate: { opacity: 1, y: 0 },
};

const stagger = {
  animate: { transition: { staggerChildren: 0.1, delayChildren: 0.1 } },
};

export default function Hero() {
  const { isSignedIn } = useAuth();

  return (
    <section className="relative min-h-screen flex items-center justify-center px-6 pt-28 pb-20 overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 bg-grid opacity-60" />
      <div className="hero-gradient-orb w-[600px] h-[600px] bg-brand-500/8 top-[-10%] left-[-10%]" />
      <div className="hero-gradient-orb w-[500px] h-[500px] bg-accent-500/6 bottom-[-10%] right-[-10%]" />
      <div className="hero-gradient-orb w-[300px] h-[300px] bg-brand-400/5 top-[40%] right-[20%]" />

      <motion.div
        variants={stagger}
        initial="initial"
        animate="animate"
        className="relative z-10 max-w-6xl mx-auto w-full"
      >
        {/* Top: Text content */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          {/* Status badge */}
          <motion.div
            variants={fadeUp}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-[var(--glass-border)] bg-[var(--glass-bg)] text-xs font-medium text-[var(--text-secondary)] mb-8"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            Bot Online — Managing Your Server 24/7
          </motion.div>

          {/* Main heading */}
          <motion.h1
            variants={fadeUp}
            transition={{ duration: 0.6 }}
            className="hero-heading text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold leading-[1.05] tracking-tight mb-6"
          >
            <span className="text-[var(--text-primary)]">Discord management</span>
            <br />
            <span className="text-[var(--text-primary)]">for </span>
            <span className="gradient-text-animated">modern servers</span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            variants={fadeUp}
            transition={{ duration: 0.6 }}
            className="text-base md:text-lg text-[var(--text-secondary)] max-w-xl mx-auto mb-10 leading-relaxed"
          >
            Automate events, moderate your community, manage tickets, and control everything — all from one powerful system built for Grand RP.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            variants={fadeUp}
            transition={{ duration: 0.6 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-3"
          >
            {!isSignedIn ? (
              <SignInButton mode="modal">
                <motion.button
                  whileHover={{ scale: 1.03 }}
                  whileTap={{ scale: 0.97 }}
                  className="glow-btn px-6 py-3 rounded-xl bg-gradient-to-r from-brand-500 to-brand-600 text-white font-semibold text-sm shadow-lg shadow-brand-500/20 flex items-center gap-2"
                >
                  <span>Get Started</span>
                  <ArrowRight size={16} />
                </motion.button>
              </SignInButton>
            ) : (
              <Link href="/dashboard">
                <motion.button
                  whileHover={{ scale: 1.03 }}
                  whileTap={{ scale: 0.97 }}
                  className="glow-btn px-6 py-3 rounded-xl bg-gradient-to-r from-brand-500 to-brand-600 text-white font-semibold text-sm shadow-lg shadow-brand-500/20 flex items-center gap-2"
                >
                  <span>Open Dashboard</span>
                  <ArrowRight size={16} />
                </motion.button>
              </Link>
            )}
            <motion.a
              href="https://discord.gg/KY7MkscD"
              target="_blank"
              rel="noopener noreferrer"
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              className="btn-secondary text-sm"
            >
              <Bot size={16} />
              Join Discord
            </motion.a>
          </motion.div>
        </div>

        {/* Code preview */}
        <motion.div
          variants={fadeUp}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="max-w-2xl mx-auto"
        >
          <CodeBlock />
        </motion.div>

        {/* Stats row */}
        <motion.div
          variants={fadeUp}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="mt-16 flex items-center justify-center gap-8 md:gap-16"
        >
          {[
            { label: 'Commands', value: '14+' },
            { label: 'Events', value: '5+' },
            { label: 'Uptime', value: '99.9%' },
          ].map((stat) => (
            <div key={stat.label} className="text-center">
              <div className="text-2xl md:text-3xl font-bold text-[var(--text-primary)]">{stat.value}</div>
              <div className="text-xs text-[var(--text-secondary)] mt-1">{stat.label}</div>
            </div>
          ))}
        </motion.div>
      </motion.div>
    </section>
  );
}
