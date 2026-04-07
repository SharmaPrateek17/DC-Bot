'use client';

import { motion } from 'framer-motion';
import { ArrowRight, Bot } from 'lucide-react';
import Link from 'next/link';
import { SignInButton, useAuth } from '@clerk/nextjs';

export default function CTA() {
  const { isSignedIn } = useAuth();

  return (
    <section className="py-24 md:py-32 px-6 relative">
      <div className="absolute inset-0 bg-mesh opacity-30" />
      
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="max-w-3xl mx-auto text-center relative z-10"
      >
        <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
          Ready to <span className="gradient-text">level up</span> your server?
        </h2>
        <p className="text-[var(--text-secondary)] text-base mb-8 max-w-md mx-auto leading-relaxed">
          Join the Sarkar community and experience next-level Discord management with automated events, moderation, and more.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          {!isSignedIn ? (
            <SignInButton mode="modal">
              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                className="glow-btn px-6 py-3 rounded-xl bg-gradient-to-r from-brand-500 to-brand-600 text-white font-semibold text-sm shadow-lg shadow-brand-500/20 flex items-center gap-2 mx-auto sm:mx-0"
              >
                <span>Get Started for Free</span>
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
        </div>
      </motion.div>
    </section>
  );
}
