'use client';

import { motion } from 'framer-motion';
import { Users } from 'lucide-react';
import PageTransition from '@/components/PageTransition';

export default function MembersPage() {
  return (
    <PageTransition>
      <div className="min-h-screen pt-28 pb-20 px-6">
        <div className="absolute inset-0 bg-mesh opacity-30 pointer-events-none" />
        <div className="max-w-4xl mx-auto relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h1 className="text-4xl md:text-6xl font-display font-bold mb-4">
              Server <span className="gradient-text">Members</span>
            </h1>
            <p className="text-[var(--text-secondary)] text-lg max-w-xl mx-auto">
              Member information is kept private for security.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="glass rounded-3xl p-16 text-center max-w-lg mx-auto"
          >
            <div className="w-20 h-20 rounded-2xl bg-brand-500/10 flex items-center justify-center mx-auto mb-6">
              <Users size={32} className="text-brand-400" />
            </div>
            <h2 className="text-xl font-bold mb-3">No Public Members Displayed</h2>
            <p className="text-[var(--text-secondary)] text-sm leading-relaxed mb-6">
              Member data is only accessible to authorized staff through the dashboard. Join our server to connect with the community.
            </p>
            <motion.a
              href="https://discord.gg/KY7MkscD"
              target="_blank"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="glow-btn inline-block px-6 py-3 rounded-xl bg-gradient-to-r from-brand-500 to-accent-500 text-white font-semibold shadow-lg shadow-brand-500/25 text-sm"
            >
              Join Server
            </motion.a>
          </motion.div>
        </div>
      </div>
    </PageTransition>
  );
}
