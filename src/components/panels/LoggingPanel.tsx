'use client';

import { motion } from 'framer-motion';
import { useState } from 'react';
import { ScrollText, Calendar, UserCheck, Terminal, Filter } from 'lucide-react';

const eventLogs = [
  { time: '14:32', event: 'RP Factory started', detail: '12 participants registered', type: 'event' },
  { time: '14:30', event: 'Event reminder sent', detail: '10 min warning for RP Factory', type: 'event' },
  { time: '13:15', event: 'Biz War closed', detail: 'Team Alpha won, 16 participants', type: 'event' },
  { time: '12:00', event: 'Bank Robbery scheduled', detail: 'Set for Mar 28, 9:00 PM', type: 'event' },
];

const regLogs = [
  { time: '14:28', event: 'Ghost registered', detail: 'RP Factory — Slot 12/20', type: 'reg' },
  { time: '14:25', event: 'Phoenix registered', detail: 'RP Factory — Slot 11/20', type: 'reg' },
  { time: '13:10', event: 'Shadow cancelled', detail: 'Biz War — moved to waiting list', type: 'reg' },
  { time: '12:45', event: 'Ninja registered', detail: 'Biz War — Slot 16/16 (FULL)', type: 'reg' },
];

const cmdLogs = [
  { time: '14:35', event: '!help used', detail: 'by Bittu in #general', type: 'cmd' },
  { time: '14:33', event: '!status used', detail: 'by Ghost in #bot-cmds', type: 'cmd' },
  { time: '14:30', event: '!events used', detail: 'by Phoenix in #events', type: 'cmd' },
  { time: '14:22', event: '!ban executed', detail: 'by SARKAR on SpamBot#1234', type: 'cmd' },
  { time: '14:10', event: '!quote used', detail: 'by Vikram in #general', type: 'cmd' },
];

const filterTabs = [
  { id: 'all', label: 'All', icon: ScrollText },
  { id: 'event', label: 'Events', icon: Calendar },
  { id: 'reg', label: 'Registrations', icon: UserCheck },
  { id: 'cmd', label: 'Commands', icon: Terminal },
];

const typeColors: Record<string, string> = {
  event: 'text-brand-400 bg-brand-500/10',
  reg: 'text-accent-400 bg-accent-500/10',
  cmd: 'text-emerald-400 bg-emerald-500/10',
};

export function LoggingPanel() {
  const [filter, setFilter] = useState('all');
  const allLogs = [...eventLogs, ...regLogs, ...cmdLogs].sort((a, b) => b.time.localeCompare(a.time));
  const filtered = filter === 'all' ? allLogs : allLogs.filter(l => l.type === filter);

  return (
    <div className="space-y-4">
      <p className="text-sm text-[var(--text-secondary)]">Real-time Discord activity logs — events, registrations, and command usage.</p>

      <div className="flex gap-1.5">
        {filterTabs.map(tab => (
          <motion.button
            key={tab.id}
            whileTap={{ scale: 0.95 }}
            onClick={() => setFilter(tab.id)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-all ${
              filter === tab.id ? 'bg-brand-500/20 text-brand-400' : 'text-[var(--text-secondary)] hover:bg-white/5'
            }`}
          >
            <tab.icon size={12} /> {tab.label}
          </motion.button>
        ))}
      </div>

      <div className="glass rounded-xl p-4 font-mono text-xs max-h-80 overflow-y-auto space-y-1">
        {filtered.map((log, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.04 }}
            className="flex gap-3 p-2 rounded-lg hover:bg-white/3 transition-all"
          >
            <span className="text-[var(--text-secondary)] opacity-50 shrink-0">{log.time}</span>
            <span className={`px-1.5 py-0.5 rounded text-[10px] uppercase font-bold shrink-0 ${typeColors[log.type]}`}>{log.type}</span>
            <span className="text-[var(--text-primary)]">{log.event}</span>
            <span className="text-[var(--text-secondary)] opacity-60 ml-auto shrink-0">{log.detail}</span>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

/* ═══════════ LOGIN LOGS ═══════════ */
const loginLogs = [
  { user: 'Bittu', email: 'bittu***@gmail.com', time: '2 min ago', status: 'success', ip: '103.xx.xx.45' },
  { user: 'Ghost', email: 'ghost***@gmail.com', time: '1 hour ago', status: 'success', ip: '157.xx.xx.12' },
  { user: 'Unknown', email: 'spam***@mail.com', time: '3 hours ago', status: 'failed', ip: '45.xx.xx.89' },
  { user: 'Phoenix', email: 'phoenix***@gmail.com', time: '5 hours ago', status: 'success', ip: '203.xx.xx.67' },
  { user: 'Unknown', email: 'test***@temp.com', time: '1 day ago', status: 'failed', ip: '91.xx.xx.34' },
];

export function LoginLogsPanel() {
  return (
    <div className="space-y-4">
      <p className="text-sm text-[var(--text-secondary)]">Website login activity — track who accesses the dashboard.</p>

      <div className="grid grid-cols-3 gap-3">
        <div className="glass rounded-xl p-3 text-center">
          <div className="text-lg font-bold text-emerald-400">12</div>
          <div className="text-xs text-[var(--text-secondary)]">Successful</div>
        </div>
        <div className="glass rounded-xl p-3 text-center">
          <div className="text-lg font-bold text-red-400">3</div>
          <div className="text-xs text-[var(--text-secondary)]">Failed</div>
        </div>
        <div className="glass rounded-xl p-3 text-center">
          <div className="text-lg font-bold text-brand-400">15</div>
          <div className="text-xs text-[var(--text-secondary)]">Total</div>
        </div>
      </div>

      <div className="glass rounded-xl overflow-hidden">
        <div className="grid grid-cols-5 gap-2 p-3 border-b border-[var(--glass-border)] text-xs font-semibold text-[var(--text-secondary)]">
          <span>User</span><span>Email</span><span>IP</span><span>Time</span><span>Status</span>
        </div>
        {loginLogs.map((log, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: i * 0.06 }}
            className="grid grid-cols-5 gap-2 p-3 text-xs hover:bg-white/3 transition-all"
          >
            <span className="font-medium">{log.user}</span>
            <span className="text-[var(--text-secondary)] truncate">{log.email}</span>
            <span className="text-[var(--text-secondary)] font-mono">{log.ip}</span>
            <span className="text-[var(--text-secondary)]">{log.time}</span>
            <span className={`font-medium ${log.status === 'success' ? 'text-emerald-400' : 'text-red-400'}`}>
              {log.status}
            </span>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
