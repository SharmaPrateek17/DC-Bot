'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { SignInButton, useAuth } from '@clerk/nextjs';
import { useState, useEffect } from 'react';
import {
  Users, Activity, Terminal, TrendingUp, ArrowUpRight,
  Clock, Shield, Zap, Lock, BarChart3, Calendar,
  Settings, ChevronRight, Bell, CheckCircle2,
  XCircle, AlertTriangle, Search, ToggleLeft, ToggleRight,
  RefreshCw, Eye, EyeOff, Hash, MessageSquare, UserCheck
} from 'lucide-react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell
} from 'recharts';
import PageTransition from '@/components/PageTransition';
import { SkeletonStat } from '@/components/PageTransition';

/* ═══════════ DATA ═══════════ */
const weeklyActivity = [
  { name: 'Mon', users: 45, commands: 120 },
  { name: 'Tue', users: 62, commands: 145 },
  { name: 'Wed', users: 38, commands: 98 },
  { name: 'Thu', users: 71, commands: 167 },
  { name: 'Fri', users: 89, commands: 210 },
  { name: 'Sat', users: 95, commands: 245 },
  { name: 'Sun', users: 78, commands: 190 },
];

const commandUsage = [
  { name: '!help', count: 87 },
  { name: '!events', count: 63 },
  { name: '!status', count: 52 },
  { name: '!raid', count: 41 },
  { name: '!quote', count: 35 },
  { name: '!ban', count: 28 },
];

const pieData = [
  { name: 'General', value: 35, color: '#8b5cf6' },
  { name: 'Events', value: 25, color: '#0ea5e9' },
  { name: 'Moderation', value: 20, color: '#ef4444' },
  { name: 'Fun', value: 12, color: '#ec4899' },
  { name: 'Admin', value: 8, color: '#f97316' },
];

const events = [
  { name: 'RP Factory', time: 'Today, 8:00 PM', status: 'upcoming', participants: 12, maxSlots: 20 },
  { name: 'Biz War', time: 'Tomorrow, 6:00 PM', status: 'upcoming', participants: 8, maxSlots: 16 },
  { name: 'Bank Robbery', time: 'Mar 28, 9:00 PM', status: 'scheduled', participants: 0, maxSlots: 12 },
  { name: 'Mall Event', time: 'Mar 30, 7:00 PM', status: 'scheduled', participants: 0, maxSlots: 24 },
];

const modLogs = [
  { user: '8bitGamer', action: 'Banned', reason: 'Spamming in #general', by: 'SARKAR', time: '2 hours ago', severity: 'high' },
  { user: 'ToxicRaider', action: 'Muted', reason: 'Inappropriate language', by: 'Ghost', time: '5 hours ago', severity: 'medium' },
  { user: 'FloodBot', action: 'Kicked', reason: 'Bot account detected', by: 'Auto-Mod', time: '1 day ago', severity: 'high' },
  { user: 'RandomUser', action: 'Warned', reason: 'Off-topic discussion', by: 'Vikram', time: '1 day ago', severity: 'low' },
  { user: 'SpamKing', action: 'Banned', reason: 'Advertising in DMs', by: 'SARKAR', time: '2 days ago', severity: 'high' },
];

const systemSettings = [
  { name: 'Auto-Moderation', desc: 'Automatically detect and remove spam, slurs, and raids.', enabled: true, icon: Shield },
  { name: 'Welcome Messages', desc: 'Send a greeting message when new members join.', enabled: true, icon: MessageSquare },
  { name: 'Event Reminders', desc: 'Send automated reminders before scheduled events.', enabled: true, icon: Bell },
  { name: 'Logging System', desc: 'Log all moderation actions and member changes.', enabled: true, icon: Eye },
  { name: 'Anti-Raid Protection', desc: 'Detect and block mass-join attacks automatically.', enabled: false, icon: AlertTriangle },
  { name: 'Verification Gate', desc: 'Require new members to verify before accessing channels.', enabled: false, icon: UserCheck },
];

const sidebarItems = [
  { id: 'overview', label: 'Overview', icon: BarChart3 },
  { id: 'analytics', label: 'Analytics', icon: TrendingUp },
  { id: 'events', label: 'Events', icon: Calendar },
  { id: 'moderation', label: 'Moderation', icon: Shield },
  { id: 'settings', label: 'Settings', icon: Settings },
];

/* ═══════════ AUTH GATE ═══════════ */
function DashboardGate() {
  const { isSignedIn } = useAuth();

  if (isSignedIn) return <DashboardPanel />;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6 }}
      className="glass rounded-3xl p-16 text-center max-w-lg mx-auto mt-12"
    >
      <div className="w-20 h-20 rounded-2xl bg-brand-500/10 flex items-center justify-center mx-auto mb-6">
        <Lock size={32} className="text-brand-400" />
      </div>
      <h2 className="text-2xl font-bold mb-2">Authentication Required</h2>
      <p className="text-[var(--text-secondary)] mb-6 text-sm">
        Sign in to access the Sarkar System dashboard and server analytics.
      </p>
      <SignInButton mode="modal">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="glow-btn px-8 py-3 rounded-2xl bg-gradient-to-r from-brand-500 to-accent-500 text-white font-semibold shadow-lg shadow-brand-500/25"
        >
          Sign In to Continue
        </motion.button>
      </SignInButton>
    </motion.div>
  );
}

/* ═══════════ MAIN DASHBOARD ═══════════ */
function DashboardPanel() {
  const [activeSection, setActiveSection] = useState('overview');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const timer = setTimeout(() => setLoading(false), 800);
    return () => clearTimeout(timer);
  }, [activeSection]);

  return (
    <div className="flex gap-6 mt-4">
      {/* Sidebar */}
      <motion.div
        initial={{ opacity: 0, x: -30 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
        className="hidden lg:block w-56 shrink-0"
      >
        <div className="glass rounded-2xl p-3 sticky top-28 space-y-1">
          {sidebarItems.map((item) => (
            <motion.button
              key={item.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setActiveSection(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
                activeSection === item.id
                  ? 'bg-brand-500/20 text-brand-400 shadow-lg shadow-brand-500/10'
                  : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-white/5'
              }`}
            >
              <item.icon size={18} />
              {item.label}
              {activeSection === item.id && <ChevronRight size={14} className="ml-auto" />}
            </motion.button>
          ))}
        </div>
      </motion.div>

      {/* Mobile Tabs */}
      <div className="lg:hidden fixed bottom-4 left-4 right-4 z-40 glass rounded-2xl p-2 flex gap-1">
        {sidebarItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveSection(item.id)}
            className={`flex-1 flex flex-col items-center gap-1 py-2 rounded-xl text-xs transition-all ${
              activeSection === item.id
                ? 'bg-brand-500/20 text-brand-400'
                : 'text-[var(--text-secondary)]'
            }`}
          >
            <item.icon size={16} />
            {item.label}
          </button>
        ))}
      </div>

      {/* Content Area */}
      <div className="flex-1 min-w-0">
        <AnimatePresence mode="wait">
          {loading ? (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-6"
            >
              <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {[...Array(4)].map((_, i) => <SkeletonStat key={i} />)}
              </div>
              <div className="grid lg:grid-cols-2 gap-6">
                <div className="glass rounded-2xl p-6 h-72 animate-pulse" />
                <div className="glass rounded-2xl p-6 h-72 animate-pulse" />
              </div>
            </motion.div>
          ) : (
            <motion.div
              key={activeSection}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {activeSection === 'overview' && <OverviewSection />}
              {activeSection === 'analytics' && <AnalyticsSection />}
              {activeSection === 'events' && <EventsSection />}
              {activeSection === 'moderation' && <ModerationSection />}
              {activeSection === 'settings' && <SettingsSection />}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

/* ═══════════ OVERVIEW ═══════════ */
function OverviewSection() {
  const stats = [
    { label: 'Total Commands', value: '1,247', change: '+12%', icon: Terminal, color: 'from-brand-500 to-brand-600' },
    { label: 'Active Users', value: '89', change: '+5%', icon: Users, color: 'from-accent-500 to-accent-600' },
    { label: 'Events Run', value: '34', change: '+3', icon: Calendar, color: 'from-emerald-500 to-emerald-600' },
    { label: 'Mod Actions', value: '156', change: '-8%', icon: Shield, color: 'from-red-500 to-red-600' },
  ];

  const systemStatus = [
    { name: 'Bot Core', status: 'online', detail: 'Running stable', icon: Zap },
    { name: 'Event Scheduler', status: 'online', detail: '2 events queued', icon: Clock },
    { name: 'Auto-Mod', status: 'online', detail: 'Monitoring active', icon: Shield },
    { name: 'Logging', status: 'online', detail: 'Recording all actions', icon: Activity },
  ];

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08 }}
            className="glass rounded-2xl p-5 card-lift cursor-default"
          >
            <div className="flex items-start justify-between mb-3">
              <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${stat.color} flex items-center justify-center shadow-lg`}>
                <stat.icon size={18} className="text-white" />
              </div>
              <span className={`text-xs font-semibold px-2 py-0.5 rounded-lg ${
                stat.change.startsWith('+') ? 'text-emerald-400 bg-emerald-500/10' : 'text-red-400 bg-red-500/10'
              }`}>
                {stat.change}
              </span>
            </div>
            <div className="text-2xl font-bold">{stat.value}</div>
            <div className="text-sm text-[var(--text-secondary)]">{stat.label}</div>
          </motion.div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass rounded-2xl p-6"
        >
          <h3 className="text-lg font-bold mb-1">Weekly Activity</h3>
          <p className="text-xs text-[var(--text-secondary)] mb-4">Users and commands over the past week</p>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={weeklyActivity}>
              <defs>
                <linearGradient id="colorUsers" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#7c3aed" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#7c3aed" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorCmds" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
              <XAxis dataKey="name" stroke="rgba(255,255,255,0.3)" fontSize={11} />
              <YAxis stroke="rgba(255,255,255,0.3)" fontSize={11} />
              <Tooltip contentStyle={{ backgroundColor: 'rgba(6,6,8,0.95)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px' }} />
              <Area type="monotone" dataKey="users" stroke="#7c3aed" fillOpacity={1} fill="url(#colorUsers)" strokeWidth={2} />
              <Area type="monotone" dataKey="commands" stroke="#0ea5e9" fillOpacity={1} fill="url(#colorCmds)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        {/* System Status */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass rounded-2xl p-6"
        >
          <h3 className="text-lg font-bold mb-1">System Status</h3>
          <p className="text-xs text-[var(--text-secondary)] mb-4">All subsystems running normally</p>
          <div className="space-y-3">
            {systemStatus.map((item, i) => (
              <div key={i} className="flex items-center gap-3 p-3 rounded-xl hover:bg-white/3 transition-all">
                <div className="w-9 h-9 rounded-xl bg-white/5 flex items-center justify-center text-brand-400">
                  <item.icon size={16} />
                </div>
                <div className="flex-1">
                  <div className="text-sm font-medium">{item.name}</div>
                  <div className="text-xs text-[var(--text-secondary)]">{item.detail}</div>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="text-xs text-emerald-400 font-medium capitalize">{item.status}</span>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}

/* ═══════════ ANALYTICS ═══════════ */
function AnalyticsSection() {
  return (
    <div className="space-y-6">
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Command Usage Bar Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass rounded-2xl p-6"
        >
          <h3 className="text-lg font-bold mb-1">Top Commands</h3>
          <p className="text-xs text-[var(--text-secondary)] mb-4">Most used commands this week</p>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={commandUsage} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
              <XAxis type="number" stroke="rgba(255,255,255,0.3)" fontSize={11} />
              <YAxis dataKey="name" type="category" stroke="rgba(255,255,255,0.3)" fontSize={11} width={55} />
              <Tooltip contentStyle={{ backgroundColor: 'rgba(6,6,8,0.95)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px' }} />
              <defs>
                <linearGradient id="barGrad" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#7c3aed" />
                  <stop offset="100%" stopColor="#0ea5e9" />
                </linearGradient>
              </defs>
              <Bar dataKey="count" fill="url(#barGrad)" radius={[0, 8, 8, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Category Distribution Pie */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass rounded-2xl p-6"
        >
          <h3 className="text-lg font-bold mb-1">Command Categories</h3>
          <p className="text-xs text-[var(--text-secondary)] mb-4">Distribution by category</p>
          <div className="flex items-center gap-6">
            <ResponsiveContainer width="50%" height={200}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={3} dataKey="value">
                  {pieData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: 'rgba(6,6,8,0.95)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px' }} />
              </PieChart>
            </ResponsiveContainer>
            <div className="space-y-2">
              {pieData.map((item) => (
                <div key={item.name} className="flex items-center gap-2 text-sm">
                  <span className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                  <span className="text-[var(--text-secondary)]">{item.name}</span>
                  <span className="font-medium ml-auto">{item.value}%</span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>

      {/* Usage Over Time */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="glass rounded-2xl p-6"
      >
        <h3 className="text-lg font-bold mb-1">Traffic Overview</h3>
        <p className="text-xs text-[var(--text-secondary)] mb-4">User activity & command trends</p>
        <ResponsiveContainer width="100%" height={250}>
          <AreaChart data={weeklyActivity}>
            <defs>
              <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#7c3aed" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#7c3aed" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
            <XAxis dataKey="name" stroke="rgba(255,255,255,0.3)" fontSize={11} />
            <YAxis stroke="rgba(255,255,255,0.3)" fontSize={11} />
            <Tooltip contentStyle={{ backgroundColor: 'rgba(6,6,8,0.95)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px' }} />
            <Area type="monotone" dataKey="commands" stroke="#7c3aed" fillOpacity={1} fill="url(#areaGrad)" strokeWidth={2.5} />
          </AreaChart>
        </ResponsiveContainer>
      </motion.div>
    </div>
  );
}

/* ═══════════ EVENTS ═══════════ */
function EventsSection() {
  return (
    <div className="space-y-6">
      {/* Summary stats */}
      <div className="grid sm:grid-cols-3 gap-4">
        {[
          { label: 'Upcoming Events', value: '2', icon: Calendar, color: 'text-brand-400' },
          { label: 'Registered Players', value: '20', icon: Users, color: 'text-accent-400' },
          { label: 'Events This Month', value: '4', icon: Activity, color: 'text-emerald-400' },
        ].map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08 }}
            className="glass rounded-2xl p-5 card-lift"
          >
            <stat.icon size={20} className={`${stat.color} mb-3`} />
            <div className="text-2xl font-bold">{stat.value}</div>
            <div className="text-sm text-[var(--text-secondary)]">{stat.label}</div>
          </motion.div>
        ))}
      </div>

      {/* Events List */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="glass rounded-2xl p-6"
      >
        <h3 className="text-lg font-bold mb-4">Scheduled Events</h3>
        <div className="space-y-3">
          {events.map((event, i) => (
            <motion.div
              key={event.name}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 + i * 0.08 }}
              whileHover={{ x: 4 }}
              className="flex items-center justify-between p-4 rounded-xl hover:bg-white/3 transition-all group"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-brand-500/10 flex items-center justify-center">
                  <Calendar size={20} className="text-brand-400" />
                </div>
                <div>
                  <div className="font-medium">{event.name}</div>
                  <div className="text-xs text-[var(--text-secondary)] flex items-center gap-2">
                    <Clock size={12} />
                    {event.time}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right hidden sm:block">
                  <div className="text-sm font-medium">{event.participants}/{event.maxSlots}</div>
                  <div className="text-xs text-[var(--text-secondary)]">Participants</div>
                </div>
                <div className="w-20">
                  <div className="h-1.5 rounded-full bg-white/5 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-brand-500 to-accent-500 rounded-full transition-all"
                      style={{ width: `${(event.participants / event.maxSlots) * 100}%` }}
                    />
                  </div>
                </div>
                <span className={`text-xs font-medium px-2.5 py-1 rounded-lg ${
                  event.status === 'upcoming' ? 'text-emerald-400 bg-emerald-500/10' : 'text-accent-400 bg-accent-500/10'
                }`}>
                  {event.status}
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}

/* ═══════════ MODERATION ═══════════ */
function ModerationSection() {
  const [filter, setFilter] = useState('all');
  const filtered = filter === 'all' ? modLogs : modLogs.filter(l => l.severity === filter);

  const severityColors: Record<string, string> = {
    high: 'text-red-400 bg-red-500/10',
    medium: 'text-orange-400 bg-orange-500/10',
    low: 'text-yellow-400 bg-yellow-500/10',
  };

  const actionIcons: Record<string, any> = {
    Banned: XCircle,
    Muted: EyeOff,
    Kicked: AlertTriangle,
    Warned: Bell,
  };

  return (
    <div className="space-y-6">
      {/* Quick stats */}
      <div className="grid sm:grid-cols-4 gap-4">
        {[
          { label: 'Total Bans', value: '23', color: 'text-red-400' },
          { label: 'Mutes', value: '47', color: 'text-orange-400' },
          { label: 'Kicks', value: '12', color: 'text-yellow-400' },
          { label: 'Warnings', value: '74', color: 'text-accent-400' },
        ].map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.06 }}
            className="glass rounded-2xl p-4 text-center card-lift"
          >
            <div className={`text-2xl font-bold ${stat.color}`}>{stat.value}</div>
            <div className="text-xs text-[var(--text-secondary)] mt-1">{stat.label}</div>
          </motion.div>
        ))}
      </div>

      {/* Mod Log */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="glass rounded-2xl p-6"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold">Moderation Log</h3>
          <div className="flex gap-1.5">
            {['all', 'high', 'medium', 'low'].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                  filter === f ? 'bg-brand-500/20 text-brand-400' : 'text-[var(--text-secondary)] hover:bg-white/5'
                }`}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
        </div>
        <div className="space-y-2">
          {filtered.map((log, i) => {
            const ActionIcon = actionIcons[log.action] || AlertTriangle;
            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.06 }}
                whileHover={{ x: 4 }}
                className="flex items-center gap-4 p-3 rounded-xl hover:bg-white/3 transition-all"
              >
                <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${severityColors[log.severity]}`}>
                  <ActionIcon size={16} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm">
                    <span className="font-medium">{log.user}</span>
                    <span className="text-[var(--text-secondary)]"> — {log.action}</span>
                  </div>
                  <div className="text-xs text-[var(--text-secondary)] truncate">{log.reason}</div>
                </div>
                <div className="text-right shrink-0 hidden sm:block">
                  <div className="text-xs text-[var(--text-secondary)]">by {log.by}</div>
                  <div className="text-xs text-[var(--text-secondary)] opacity-60">{log.time}</div>
                </div>
                <span className={`text-xs font-medium px-2 py-0.5 rounded-lg shrink-0 ${severityColors[log.severity]}`}>
                  {log.severity}
                </span>
              </motion.div>
            );
          })}
        </div>
      </motion.div>
    </div>
  );
}

/* ═══════════ SETTINGS ═══════════ */
function SettingsSection() {
  const [settings, setSettings] = useState(systemSettings);

  const toggle = (index: number) => {
    setSettings(prev => prev.map((s, i) => i === index ? { ...s, enabled: !s.enabled } : s));
  };

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass rounded-2xl p-6"
      >
        <h3 className="text-lg font-bold mb-1">Bot Settings</h3>
        <p className="text-xs text-[var(--text-secondary)] mb-6">Configure the Sarkar System bot features</p>
        <div className="space-y-3">
          {settings.map((setting, i) => (
            <motion.div
              key={setting.name}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.06 }}
              className="flex items-center justify-between p-4 rounded-xl hover:bg-white/3 transition-all"
            >
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center text-brand-400">
                  <setting.icon size={18} />
                </div>
                <div>
                  <div className="text-sm font-medium">{setting.name}</div>
                  <div className="text-xs text-[var(--text-secondary)]">{setting.desc}</div>
                </div>
              </div>
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={() => toggle(i)}
                className={`transition-colors ${setting.enabled ? 'text-emerald-400' : 'text-[var(--text-secondary)]'}`}
              >
                {setting.enabled ? <ToggleRight size={28} /> : <ToggleLeft size={28} />}
              </motion.button>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Server Info */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="glass rounded-2xl p-6"
      >
        <h3 className="text-lg font-bold mb-4">Server Information</h3>
        <div className="grid sm:grid-cols-2 gap-4">
          {[
            { label: 'Bot Version', value: 'v2.1.0' },
            { label: 'Command Prefix', value: '!' },
            { label: 'Server Region', value: 'India (Mumbai)' },
            { label: 'Bot Language', value: 'Python + Flask' },
            { label: 'Database', value: 'SQLite' },
            { label: 'API Status', value: 'Connected' },
          ].map((info) => (
            <div key={info.label} className="flex items-center justify-between p-3 rounded-xl bg-white/2">
              <span className="text-sm text-[var(--text-secondary)]">{info.label}</span>
              <span className="text-sm font-medium">{info.value}</span>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}

/* ═══════════ PAGE ═══════════ */
export default function DashboardPage() {
  return (
    <PageTransition>
      <div className="min-h-screen pt-28 pb-20 px-6">
        <div className="absolute inset-0 bg-mesh opacity-30 pointer-events-none" />
        <div className="max-w-7xl mx-auto relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="mb-6"
          >
            <h1 className="text-3xl md:text-4xl font-display font-bold mb-1">
              <span className="gradient-text">Dashboard</span>
            </h1>
            <p className="text-[var(--text-secondary)] text-sm">
              Sarkar System management panel and analytics.
            </p>
          </motion.div>
          <DashboardGate />
        </div>
      </div>
    </PageTransition>
  );
}
