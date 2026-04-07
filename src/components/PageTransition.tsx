'use client';

import { motion } from 'framer-motion';
import { ReactNode } from 'react';

export default function PageTransition({ children }: { children: ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </motion.div>
  );
}

/* Skeleton loader components */
export function SkeletonCard() {
  return (
    <div className="glass rounded-2xl p-6 animate-pulse">
      <div className="w-12 h-12 rounded-xl bg-white/10 mb-4" />
      <div className="h-4 bg-white/10 rounded-lg w-3/4 mb-3" />
      <div className="h-3 bg-white/10 rounded-lg w-full mb-2" />
      <div className="h-3 bg-white/10 rounded-lg w-2/3" />
    </div>
  );
}

export function SkeletonStat() {
  return (
    <div className="glass rounded-2xl p-6 animate-pulse">
      <div className="flex justify-between mb-4">
        <div className="w-10 h-10 rounded-xl bg-white/10" />
        <div className="w-12 h-4 rounded-lg bg-white/10" />
      </div>
      <div className="h-6 bg-white/10 rounded-lg w-1/2 mb-2" />
      <div className="h-3 bg-white/10 rounded-lg w-1/3" />
    </div>
  );
}
