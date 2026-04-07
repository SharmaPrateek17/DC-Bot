'use client';

import { motion } from 'framer-motion';
import { useState } from 'react';
import {
  Zap, BarChart3, ScrollText, UserCog, Shield, Ticket,
} from 'lucide-react';
import FeatureCard from './FeatureCard';
import FeatureModal from './FeatureModal';
import { EventManagementPanel } from './panels/EventPanel';
import { AnalyticsPanel } from './panels/AnalyticsPanel';
import { LoggingPanel, LoginLogsPanel } from './panels/LoggingPanel';
import { AutoModPanel, RoleManagementPanel } from './panels/ModPanel';

const features = [
  {
    icon: <Zap size={20} />,
    title: 'Event Management',
    desc: 'Create, manage, and close server events with automated reminders and participant tracking.',
    panel: 'events',
  },
  {
    icon: <BarChart3 size={20} />,
    title: 'Live Analytics',
    desc: 'Real-time server activity monitoring with channel stats and live feed.',
    panel: 'analytics',
  },
  {
    icon: <ScrollText size={20} />,
    title: 'Logging System',
    desc: 'Comprehensive Discord logs for events, registrations, and bot command usage.',
    panel: 'logging',
  },
  {
    icon: <UserCog size={20} />,
    title: 'Login Tracking',
    desc: 'Track website login activity with status, IP, and user details.',
    panel: 'loginlogs',
  },
  {
    icon: <Shield size={20} />,
    title: 'Auto Moderation',
    desc: 'Configurable auto-mod controls — anti-spam, slur detection, link filtering, and more.',
    panel: 'automod',
  },
  {
    icon: <Ticket size={20} />,
    title: 'Role Management',
    desc: 'View and manage Discord server roles, permissions, and member assignments.',
    panel: 'roles',
  },
];

export default function Features() {
  const [activeModal, setActiveModal] = useState<string | null>(null);

  const getModalContent = (panelId: string) => {
    switch (panelId) {
      case 'events': return <EventManagementPanel />;
      case 'analytics': return <AnalyticsPanel />;
      case 'logging': return <LoggingPanel />;
      case 'loginlogs': return <LoginLogsPanel />;
      case 'automod': return <AutoModPanel />;
      case 'roles': return <RoleManagementPanel />;
      default: return null;
    }
  };

  const activeFeature = features.find(f => f.panel === activeModal);

  return (
    <section id="features" className="py-24 md:py-32 px-6 relative">
      <div className="max-w-6xl mx-auto">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
            Everything you need to{' '}
            <span className="gradient-text">manage your server</span>
          </h2>
          <p className="text-[var(--text-secondary)] text-base max-w-lg mx-auto">
            From event management to advanced moderation — all the tools your Discord server needs, in one place.
          </p>
        </motion.div>

        {/* Feature grid */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map((feature, i) => (
            <FeatureCard
              key={feature.title}
              icon={feature.icon}
              title={feature.title}
              description={feature.desc}
              index={i}
              onClick={() => setActiveModal(feature.panel)}
            />
          ))}
        </div>
      </div>

      {/* Feature Detail Modal */}
      <FeatureModal
        isOpen={activeModal !== null}
        onClose={() => setActiveModal(null)}
        title={activeFeature?.title || ''}
        icon={activeFeature?.icon || null}
      >
        {activeModal && getModalContent(activeModal)}
      </FeatureModal>
    </section>
  );
}
