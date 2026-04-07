'use client';

import { motion } from 'framer-motion';
import { Mail, PlayCircle, Camera, MessagesSquare, Code2, Sparkles, Cpu } from 'lucide-react';

export default function About() {
  return (
    <section id="about" className="py-24 md:py-32 px-6 relative">
      <div className="section-divider absolute top-0 left-6 right-6" />
      <div className="max-w-6xl mx-auto">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.6 }}
          className="mb-16"
        >
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
            About <span className="gradient-text">Sarkar System</span>
          </h2>
          <p className="text-[var(--text-secondary)] text-base max-w-xl">
            A powerful Discord bot system designed for Grand RP servers — built for automation, moderation, and event management.
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left — Description + highlights */}
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="space-y-6"
          >
            <p className="text-[var(--text-secondary)] text-sm leading-relaxed">
              Built to handle roleplay servers, events, ticket systems, and community control efficiently. 
              Every feature is crafted to make server management seamless.
            </p>

            {/* Highlight cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {[
                { icon: <Code2 size={18} />, label: 'Custom Built', desc: 'Tailored for GRP' },
                { icon: <Sparkles size={18} />, label: 'Auto Events', desc: 'Scheduled reminders' },
                { icon: <Cpu size={18} />, label: '24/7 Uptime', desc: 'Always online' },
              ].map((item) => (
                <div key={item.label} className="rounded-xl border border-[var(--glass-border)] bg-[var(--glass-bg)] p-4">
                  <div className="text-brand-400 mb-2">{item.icon}</div>
                  <div className="text-sm font-medium text-[var(--text-primary)]">{item.label}</div>
                  <div className="text-xs text-[var(--text-secondary)]">{item.desc}</div>
                </div>
              ))}
            </div>

            <div className="rounded-xl border border-brand-500/20 bg-brand-500/5 p-4">
              <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                🚧 Website is under active development — new features are being added regularly.
              </p>
            </div>
          </motion.div>

          {/* Right — Developer card + socials */}
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="space-y-4"
          >
            {/* Developer card */}
            <div className="rounded-xl border border-[var(--glass-border)] bg-[var(--glass-bg)] p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-brand-400 to-accent-500 flex items-center justify-center shadow-lg shadow-brand-500/15">
                  <span className="text-xl">👑</span>
                </div>
                <div>
                  <h3 className="text-base font-semibold text-[var(--text-primary)]">Bittu</h3>
                  <p className="text-xs text-[var(--text-secondary)]">Developer & Owner</p>
                </div>
              </div>
              <p className="text-sm text-[var(--text-secondary)] leading-relaxed mb-4">
                Creator of the Sarkar System — a bot designed for Grand RP communities with advanced event management, moderation, and automation features.
              </p>
              <div className="flex items-center gap-1.5 text-xs text-[var(--text-secondary)]">
                <Mail size={12} className="text-brand-400" />
                <a href="mailto:Bittu180712@gmail.com" className="hover:text-brand-400 transition-colors">
                  Bittu180712@gmail.com
                </a>
              </div>
            </div>

            {/* Social links */}
            <div className="rounded-xl border border-[var(--glass-border)] bg-[var(--glass-bg)] p-4">
              <h4 className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wider mb-3">
                Connect
              </h4>
              <div className="grid grid-cols-2 gap-2">
                <motion.a
                  href="https://www.youtube.com/@BittuSharmaRP"
                  target="_blank"
                  rel="noopener noreferrer"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="flex items-center gap-2 px-3 py-2.5 rounded-lg bg-red-500/8 text-red-400 hover:bg-red-500/15 transition-all text-sm font-medium"
                >
                  <PlayCircle size={16} />
                  YouTube
                </motion.a>
                <motion.div
                  className="flex items-center gap-2 px-3 py-2.5 rounded-lg bg-pink-500/8 text-pink-400 text-sm font-medium cursor-default"
                >
                  <Camera size={16} />
                  Instagram
                </motion.div>
                <motion.a
                  href="https://discord.gg/KY7MkscD"
                  target="_blank"
                  rel="noopener noreferrer"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="flex items-center gap-2 px-3 py-2.5 rounded-lg bg-accent-500/8 text-accent-400 hover:bg-accent-500/15 transition-all text-sm font-medium"
                >
                  <MessagesSquare size={16} />
                  Sarkar DC
                </motion.a>
                <motion.a
                  href="https://discord.gg/DNg6fPhY"
                  target="_blank"
                  rel="noopener noreferrer"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="flex items-center gap-2 px-3 py-2.5 rounded-lg bg-brand-500/8 text-brand-400 hover:bg-brand-500/15 transition-all text-sm font-medium"
                >
                  <MessagesSquare size={16} />
                  Owner DC
                </motion.a>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
