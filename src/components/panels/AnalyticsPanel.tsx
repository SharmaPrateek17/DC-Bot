'use client';

import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import { Activity, Users, MessageSquare, Hash, Wifi, TrendingUp } from 'lucide-react';

const channels = [
  { name: '#general', messages: 47, active: true },
  { name: '#events', messages: 12, active: true },
  { name: '#rp-chat', messages: 89, active: true },
  { name: '#admin-logs', messages: 5, active: false },
  { name: '#announcements', messages: 2, active: false },
];

const liveFeed = [
  { user: 'Bittu', action: 'sent a message in #general', time: 'Just now' },
  { user: 'Ghost', action: 'registered for RP Factory', time: '2 min ago' },
  { user: 'SARKAR Bot', action: 'sent event reminder', time: '5 min ago' },
  { user: 'Phoenix', action: 'used !status command', time: '8 min ago' },
  { user: 'Vikram', action: 'created a new announcement', time: '12 min ago' },
  { user: 'Shadow', action: 'joined #events voice channel', time: '15 min ago' },
];

export function AnalyticsPanel() {
  const [pulse, setPulse] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => setPulse(p => p + 1), 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-4">
      <p className="text-sm text-[var(--text-secondary)]">Real-time server activity and monitoring.</p>

      {/* Live Stats */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: 'Online Now', value: '23', icon: Users, color: 'text-emerald-400' },
          { label: 'Messages/hr', value: '156', icon: MessageSquare, color: 'text-brand-400' },
          { label: 'Active Channels', value: '3', icon: Hash, color: 'text-accent-400' },
        ].map((stat) => (
          <div key={stat.label} className="glass rounded-xl p-3 text-center">
            <stat.icon size={16} className={`${stat.color} mx-auto mb-1`} />
            <div className="text-lg font-bold">{stat.value}</div>
            <div className="text-xs text-[var(--text-secondary)]">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Channel Activity */}
      <div className="glass rounded-xl p-4">
        <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
          <Activity size={14} className="text-brand-400" /> Channel Activity
        </h4>
        <div className="space-y-2">
          {channels.map((ch) => (
            <div key={ch.name} className="flex items-center justify-between p-2 rounded-lg hover:bg-white/3 transition-all">
              <div className="flex items-center gap-2">
                <span className={`w-1.5 h-1.5 rounded-full ${ch.active ? 'bg-emerald-400' : 'bg-gray-500'}`} />
                <span className="text-sm font-mono">{ch.name}</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-20 h-1.5 rounded-full bg-white/5 overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.min((ch.messages / 100) * 100, 100)}%` }}
                    transition={{ duration: 0.8 }}
                    className="h-full bg-gradient-to-r from-brand-500 to-accent-500 rounded-full"
                  />
                </div>
                <span className="text-xs text-[var(--text-secondary)] w-8 text-right">{ch.messages}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Live Feed */}
      <div className="glass rounded-xl p-4">
        <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
          <Wifi size={14} className="text-emerald-400 animate-pulse" /> Live Feed
        </h4>
        <div className="space-y-1.5 max-h-48 overflow-y-auto">
          {liveFeed.map((item, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.06 }}
              className="flex items-center justify-between p-2 rounded-lg text-xs"
            >
              <span>
                <span className="text-brand-400 font-medium">{item.user}</span>
                <span className="text-[var(--text-secondary)]"> {item.action}</span>
              </span>
              <span className="text-[var(--text-secondary)] opacity-60 shrink-0 ml-2">{item.time}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
