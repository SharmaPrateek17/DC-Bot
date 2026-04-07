'use client';

import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface FeatureCardProps {
  icon: ReactNode;
  title: string;
  description: string;
  index: number;
  onClick?: () => void;
}

export default function FeatureCard({ icon, title, description, index, onClick }: FeatureCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-60px' }}
      transition={{ duration: 0.5, delay: index * 0.08 }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className="feature-card group cursor-pointer"
    >
      <div className="relative z-10">
        {/* Icon */}
        <div className="w-10 h-10 rounded-lg bg-brand-500/10 border border-brand-500/10 flex items-center justify-center mb-4 group-hover:bg-brand-500/15 group-hover:border-brand-500/20 transition-all duration-300">
          <div className="text-brand-400 group-hover:text-brand-300 transition-colors">
            {icon}
          </div>
        </div>

        {/* Title */}
        <h3 className="text-base font-semibold text-[var(--text-primary)] mb-2 group-hover:text-brand-400 transition-colors">
          {title}
        </h3>

        {/* Description */}
        <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
          {description}
        </p>

        {/* Arrow hint */}
        <div className="mt-4 flex items-center gap-1 text-xs font-medium text-[var(--text-tertiary)] group-hover:text-brand-400 transition-all">
          <span>Explore</span>
          <motion.svg
            width="12"
            height="12"
            viewBox="0 0 12 12"
            className="group-hover:translate-x-1 transition-transform"
          >
            <path
              d="M4.5 3L7.5 6L4.5 9"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              fill="none"
            />
          </motion.svg>
        </div>
      </div>
    </motion.div>
  );
}
