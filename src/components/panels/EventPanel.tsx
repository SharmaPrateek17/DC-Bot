'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';
import {
  Zap, Calendar, Plus, Play, Square, Clock, Users,
  CheckCircle2, AlertTriangle, Trash2
} from 'lucide-react';

const sampleEvents = [
  { id: 1, name: 'RP Factory', time: '8:00 PM', status: 'scheduled', participants: 12 },
  { id: 2, name: 'Biz War', time: '6:00 PM', status: 'live', participants: 16 },
  { id: 3, name: 'Bank Robbery', time: '9:00 PM', status: 'closed', participants: 8 },
];

export function EventManagementPanel() {
  const [events, setEvents] = useState(sampleEvents);
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState('');
  const [newTime, setNewTime] = useState('');

  const createEvent = () => {
    if (!newName.trim()) return;
    setEvents(prev => [...prev, {
      id: Date.now(),
      name: newName,
      time: newTime || 'TBD',
      status: 'scheduled',
      participants: 0
    }]);
    setNewName('');
    setNewTime('');
    setShowCreate(false);
  };

  const setStatus = (id: number, status: string) => {
    setEvents(prev => prev.map(e => e.id === id ? { ...e, status } : e));
  };

  const deleteEvent = (id: number) => {
    setEvents(prev => prev.filter(e => e.id !== id));
  };

  const statusColors: Record<string, string> = {
    scheduled: 'text-accent-400 bg-accent-500/10',
    live: 'text-emerald-400 bg-emerald-500/10',
    closed: 'text-red-400 bg-red-500/10',
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-[var(--text-secondary)]">Manage server events — create, go live, or close.</p>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setShowCreate(!showCreate)}
          className="glow-btn px-4 py-2 rounded-xl bg-gradient-to-r from-brand-500 to-accent-500 text-white text-sm font-medium flex items-center gap-2"
        >
          <Plus size={14} /> Create Event
        </motion.button>
      </div>

      <AnimatePresence>
        {showCreate && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="glass rounded-2xl p-4 space-y-3 overflow-hidden"
          >
            <input
              value={newName}
              onChange={e => setNewName(e.target.value)}
              placeholder="Event name..."
              className="w-full px-4 py-2.5 rounded-xl bg-white/5 border border-[var(--glass-border)] text-[var(--text-primary)] placeholder:text-[var(--text-secondary)] outline-none focus:ring-2 focus:ring-brand-500/30 text-sm"
            />
            <input
              value={newTime}
              onChange={e => setNewTime(e.target.value)}
              placeholder="Time (e.g. 8:00 PM)..."
              className="w-full px-4 py-2.5 rounded-xl bg-white/5 border border-[var(--glass-border)] text-[var(--text-primary)] placeholder:text-[var(--text-secondary)] outline-none focus:ring-2 focus:ring-brand-500/30 text-sm"
            />
            <div className="flex gap-2">
              <motion.button whileTap={{ scale: 0.95 }} onClick={createEvent} className="px-4 py-2 rounded-xl bg-brand-500/20 text-brand-400 text-sm font-medium hover:bg-brand-500/30 transition-colors">
                Add Event
              </motion.button>
              <motion.button whileTap={{ scale: 0.95 }} onClick={() => setShowCreate(false)} className="px-4 py-2 rounded-xl bg-white/5 text-[var(--text-secondary)] text-sm hover:bg-white/10 transition-colors">
                Cancel
              </motion.button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="space-y-2">
        {events.map((event) => (
          <motion.div
            key={event.id}
            layout
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="flex items-center justify-between p-4 rounded-xl bg-white/3 hover:bg-white/5 transition-all"
          >
            <div className="flex items-center gap-3">
              <Calendar size={16} className="text-brand-400" />
              <div>
                <div className="text-sm font-medium">{event.name}</div>
                <div className="text-xs text-[var(--text-secondary)] flex items-center gap-1">
                  <Clock size={10} /> {event.time} · <Users size={10} /> {event.participants}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className={`text-xs font-medium px-2.5 py-1 rounded-lg ${statusColors[event.status]}`}>
                {event.status}
              </span>
              {event.status === 'scheduled' && (
                <motion.button whileTap={{ scale: 0.9 }} onClick={() => setStatus(event.id, 'live')} className="p-1.5 rounded-lg text-emerald-400 hover:bg-emerald-500/10 transition-colors" title="Go Live">
                  <Play size={14} />
                </motion.button>
              )}
              {event.status === 'live' && (
                <motion.button whileTap={{ scale: 0.9 }} onClick={() => setStatus(event.id, 'closed')} className="p-1.5 rounded-lg text-red-400 hover:bg-red-500/10 transition-colors" title="Close">
                  <Square size={14} />
                </motion.button>
              )}
              <motion.button whileTap={{ scale: 0.9 }} onClick={() => deleteEvent(event.id)} className="p-1.5 rounded-lg text-[var(--text-secondary)] hover:text-red-400 hover:bg-red-500/10 transition-colors" title="Delete">
                <Trash2 size={14} />
              </motion.button>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
