'use client';

import { motion } from 'framer-motion';
import { Search, Copy, Check } from 'lucide-react';
import { useState } from 'react';
import PageTransition from '@/components/PageTransition';

const commands = [
  { name: '!help', alias: '—', desc: 'Opens the Command Center help menu with all available commands.', usage: '!help', category: 'General' },
  { name: '!status', alias: '—', desc: 'Shows bot uptime, server stats, and RP Ticket reminder countdown.', usage: '!status', category: 'General' },
  { name: '!quote', alias: '!q', desc: 'Sends a random motivational or funny quote.', usage: '!quote', category: 'Fun' },
  { name: '!leaderboard', alias: '!lb', desc: 'Displays the server activity leaderboard.', usage: '!leaderboard', category: 'Fun' },
  { name: '!events', alias: '—', desc: 'Shows all upcoming scheduled events with countdowns.', usage: '!events', category: 'Events' },
  { name: '!registrations', alias: '!reg', desc: 'View active event registrations and participant lists.', usage: '!registrations', category: 'Events' },
  { name: '!raid', alias: '—', desc: 'Start a new raid event with registration buttons.', usage: '!raid [event_name]', category: 'Events' },
  { name: '!robbery', alias: '—', desc: 'Start a bank robbery event with team management.', usage: '!robbery', category: 'Events' },
  { name: '!start', alias: '—', desc: 'Start an event and lock registrations.', usage: '!start [event_id]', category: 'Admin' },
  { name: '!close', alias: '—', desc: 'Close an event and archive results.', usage: '!close [event_id]', category: 'Admin' },
  { name: '!clean', alias: '—', desc: 'Bulk delete messages in a channel.', usage: '!clean [count]', category: 'Admin' },
  { name: '!ban', alias: '—', desc: 'Opens the interactive ban modal with reason and duration.', usage: '!ban @user', category: 'Moderation' },
  { name: '!pager', alias: '—', desc: 'Send a notification ping to a specific role or member.', usage: '!pager @role [message]', category: 'Admin' },
  { name: '!announcement', alias: '!ann', desc: 'Create a formatted announcement embed.', usage: '!announcement [message]', category: 'Admin' },
];

const categories = ['All', 'General', 'Fun', 'Events', 'Admin', 'Moderation'];
const categoryColors: Record<string, string> = {
  General: 'text-emerald-400 bg-emerald-500/10',
  Fun: 'text-pink-400 bg-pink-500/10',
  Events: 'text-accent-400 bg-accent-500/10',
  Admin: 'text-orange-400 bg-orange-500/10',
  Moderation: 'text-red-400 bg-red-500/10',
};

export default function CommandsPage() {
  const [search, setSearch] = useState('');
  const [activeCategory, setActiveCategory] = useState('All');
  const [copiedCmd, setCopiedCmd] = useState<string | null>(null);

  const filtered = commands.filter((cmd) => {
    const matchesSearch = cmd.name.toLowerCase().includes(search.toLowerCase()) ||
      cmd.desc.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = activeCategory === 'All' || cmd.category === activeCategory;
    return matchesSearch && matchesCategory;
  });

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCmd(text);
    setTimeout(() => setCopiedCmd(null), 2000);
  };

  return (
    <PageTransition>
      <div className="min-h-screen pt-28 pb-20 px-6">
        <div className="absolute inset-0 bg-mesh opacity-30 pointer-events-none" />
        <div className="max-w-5xl mx-auto relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-12"
          >
            <h1 className="text-4xl md:text-6xl font-display font-bold mb-4">
              Bot <span className="gradient-text">Commands</span>
            </h1>
            <p className="text-[var(--text-secondary)] text-lg max-w-xl mx-auto">
              Complete reference for all {commands.length} bot commands. Click to copy usage.
            </p>
          </motion.div>

          {/* Search + Filters */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="mb-8 space-y-4"
          >
            <div className="relative">
              <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--text-secondary)]" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search commands..."
                className="w-full pl-12 pr-4 py-3 rounded-2xl glass text-[var(--text-primary)] placeholder:text-[var(--text-secondary)] outline-none focus:ring-2 focus:ring-brand-500/30 transition-all bg-transparent"
              />
            </div>
            <div className="flex flex-wrap gap-2">
              {categories.map((cat) => (
                <motion.button
                  key={cat}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setActiveCategory(cat)}
                  className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                    activeCategory === cat
                      ? 'bg-brand-500/20 text-brand-400 shadow-lg shadow-brand-500/10'
                      : 'glass text-[var(--text-secondary)] hover:text-[var(--text-primary)] glow-hover'
                  }`}
                >
                  {cat}
                </motion.button>
              ))}
            </div>
          </motion.div>

          {/* Commands List */}
          <div className="space-y-3">
            {filtered.map((cmd, i) => (
              <motion.div
                key={cmd.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: i * 0.04 }}
                whileHover={{ x: 4, boxShadow: '0 0 20px rgba(124, 58, 237, 0.1)' }}
                className="glass rounded-2xl p-5 group cursor-pointer transition-all"
                onClick={() => copyToClipboard(cmd.usage)}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1.5">
                      <code className="text-brand-400 font-mono font-bold text-lg">{cmd.name}</code>
                      {cmd.alias !== '—' && (
                        <span className="text-xs text-[var(--text-secondary)] font-mono px-2 py-0.5 rounded-lg bg-white/5">
                          alias: {cmd.alias}
                        </span>
                      )}
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-lg ${categoryColors[cmd.category]}`}>
                        {cmd.category}
                      </span>
                    </div>
                    <p className="text-sm text-[var(--text-secondary)] mb-2">{cmd.desc}</p>
                    <code className="text-xs font-mono text-[var(--text-secondary)] bg-white/5 px-3 py-1 rounded-lg">
                      {cmd.usage}
                    </code>
                  </div>
                  <motion.div
                    whileHover={{ scale: 1.2 }}
                    className="p-2 rounded-xl text-[var(--text-secondary)] hover:text-brand-400 hover:bg-brand-500/10 transition-colors shrink-0"
                  >
                    {copiedCmd === cmd.usage ? <Check size={16} className="text-emerald-400" /> : <Copy size={16} />}
                  </motion.div>
                </div>
              </motion.div>
            ))}
          </div>

          {filtered.length === 0 && (
            <div className="text-center py-16 text-[var(--text-secondary)]">No commands match your search.</div>
          )}
        </div>
      </div>
    </PageTransition>
  );
}
