'use client';

import { motion } from 'framer-motion';
import { useState } from 'react';
import {
  Shield, ToggleLeft, ToggleRight, AlertTriangle,
  Ban, MessageSquare, Link2, UserX, Volume2
} from 'lucide-react';

const modFeatures = [
  { name: 'Anti-Spam Filter', desc: 'Block rapid message flooding and repeated content.', icon: MessageSquare, enabled: true },
  { name: 'Slur Detection', desc: 'Automatically detect and remove offensive language.', icon: Ban, enabled: true },
  { name: 'Link Filter', desc: 'Block unauthorized links and invites.', icon: Link2, enabled: false },
  { name: 'Anti-Raid', desc: 'Detect mass-join attempts and auto-lockdown.', icon: UserX, enabled: false },
  { name: 'Caps Lock Filter', desc: 'Detect and warn users sending excessive caps.', icon: Volume2, enabled: true },
];

export function AutoModPanel() {
  const [features, setFeatures] = useState(modFeatures);

  const toggle = (i: number) => {
    setFeatures(prev => prev.map((f, idx) => idx === i ? { ...f, enabled: !f.enabled } : f));
  };

  return (
    <div className="space-y-4">
      <p className="text-sm text-[var(--text-secondary)]">Configure website and bot auto-moderation controls.</p>

      <div className="glass rounded-xl p-4">
        <div className="flex items-center gap-2 mb-4">
          <Shield size={16} className="text-brand-400" />
          <h4 className="text-sm font-semibold">Moderation Controls</h4>
        </div>
        <div className="space-y-2">
          {features.map((feat, i) => (
            <motion.div
              key={feat.name}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.06 }}
              className="flex items-center justify-between p-3 rounded-xl hover:bg-white/3 transition-all"
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center text-brand-400">
                  <feat.icon size={14} />
                </div>
                <div>
                  <div className="text-sm font-medium">{feat.name}</div>
                  <div className="text-xs text-[var(--text-secondary)]">{feat.desc}</div>
                </div>
              </div>
              <motion.button whileTap={{ scale: 0.9 }} onClick={() => toggle(i)} className={`transition-colors ${feat.enabled ? 'text-emerald-400' : 'text-[var(--text-secondary)]'}`}>
                {feat.enabled ? <ToggleRight size={24} /> : <ToggleLeft size={24} />}
              </motion.button>
            </motion.div>
          ))}
        </div>
      </div>

      <div className="glass rounded-xl p-4">
        <h4 className="text-sm font-semibold mb-3">Quick Stats</h4>
        <div className="grid grid-cols-3 gap-3">
          {[
            { label: 'Blocked Today', value: '14', color: 'text-red-400' },
            { label: 'Warnings Sent', value: '8', color: 'text-orange-400' },
            { label: 'Auto-Bans', value: '2', color: 'text-brand-400' },
          ].map(s => (
            <div key={s.label} className="text-center p-2 rounded-lg bg-white/3">
              <div className={`text-lg font-bold ${s.color}`}>{s.value}</div>
              <div className="text-xs text-[var(--text-secondary)]">{s.label}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ═══════════ ROLE MANAGEMENT ═══════════ */
const discordRoles = [
  { name: 'Owner', color: '#e74c3c', members: 1, permissions: 'Full Access' },
  { name: 'Head Admin', color: '#e67e22', members: 2, permissions: 'Manage Server' },
  { name: 'Senior Moderator', color: '#f1c40f', members: 3, permissions: 'Ban, Kick, Manage Channels' },
  { name: 'Moderator', color: '#2ecc71', members: 5, permissions: 'Kick, Mute, Manage Messages' },
  { name: 'Event Manager', color: '#3498db', members: 2, permissions: 'Manage Events' },
  { name: 'Community Manager', color: '#9b59b6', members: 2, permissions: 'Manage Roles' },
  { name: 'Bot Developer', color: '#1abc9c', members: 1, permissions: 'Bot Administration' },
  { name: 'Member', color: '#95a5a6', members: 45, permissions: 'Basic Access' },
];

export function RoleManagementPanel() {
  return (
    <div className="space-y-4">
      <p className="text-sm text-[var(--text-secondary)]">View and manage Discord server roles and permissions.</p>

      <div className="grid grid-cols-2 gap-3">
        <div className="glass rounded-xl p-3 text-center">
          <div className="text-lg font-bold text-brand-400">{discordRoles.length}</div>
          <div className="text-xs text-[var(--text-secondary)]">Total Roles</div>
        </div>
        <div className="glass rounded-xl p-3 text-center">
          <div className="text-lg font-bold text-accent-400">{discordRoles.reduce((a, r) => a + r.members, 0)}</div>
          <div className="text-xs text-[var(--text-secondary)]">Total Members</div>
        </div>
      </div>

      <div className="glass rounded-xl p-4">
        <h4 className="text-sm font-semibold mb-3">Server Roles</h4>
        <div className="space-y-2">
          {discordRoles.map((role, i) => (
            <motion.div
              key={role.name}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
              whileHover={{ x: 4 }}
              className="flex items-center justify-between p-3 rounded-xl hover:bg-white/3 transition-all"
            >
              <div className="flex items-center gap-3">
                <span className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: role.color }} />
                <div>
                  <div className="text-sm font-medium">{role.name}</div>
                  <div className="text-xs text-[var(--text-secondary)]">{role.permissions}</div>
                </div>
              </div>
              <span className="text-xs text-[var(--text-secondary)] bg-white/5 px-2 py-0.5 rounded-lg">
                {role.members} member{role.members !== 1 ? 's' : ''}
              </span>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
