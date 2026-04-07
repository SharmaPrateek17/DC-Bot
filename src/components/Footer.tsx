'use client';

import { Mail, PlayCircle, MessagesSquare, ExternalLink } from 'lucide-react';

const footerSections = [
  {
    title: 'Product',
    links: [
      { label: 'Features', href: '/#features' },
      { label: 'Commands', href: '/commands' },
      { label: 'Dashboard', href: '/dashboard' },
    ],
  },
  {
    title: 'Community',
    links: [
      { label: 'Sarkar Discord', href: 'https://discord.gg/KY7MkscD', external: true },
      { label: 'Owner Discord', href: 'https://discord.gg/DNg6fPhY', external: true },
      { label: 'YouTube', href: 'https://www.youtube.com/@BittuSharmaRP', external: true },
    ],
  },
  {
    title: 'Info',
    links: [
      { label: 'About', href: '/#about' },
      { label: 'Contact', href: 'mailto:Bittu180712@gmail.com' },
    ],
  },
];

export default function Footer() {
  return (
    <footer className="border-t border-[var(--glass-border)] bg-[var(--bg-secondary)]">
      <div className="max-w-6xl mx-auto px-6 py-12 md:py-16">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-12">
          {/* Brand column */}
          <div className="col-span-2 md:col-span-1">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-7 h-7 rounded-md bg-gradient-to-br from-brand-500 to-accent-500 flex items-center justify-center">
                <span className="text-white font-bold text-xs">S</span>
              </div>
              <span className="text-sm font-semibold text-[var(--text-primary)]">Sarkar System</span>
            </div>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed max-w-xs mb-4">
              Next-level Discord bot system for automation, moderation, and event management.
            </p>
            <div className="flex items-center gap-1 text-xs text-[var(--text-tertiary)]">
              <Mail size={12} />
              <a href="mailto:Bittu180712@gmail.com" className="hover:text-[var(--text-secondary)] transition-colors">
                Bittu180712@gmail.com
              </a>
            </div>
          </div>

          {/* Link columns */}
          {footerSections.map((section) => (
            <div key={section.title}>
              <h4 className="text-xs font-semibold text-[var(--text-primary)] uppercase tracking-wider mb-4">
                {section.title}
              </h4>
              <ul className="space-y-2.5">
                {section.links.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      target={('external' in link && link.external) ? '_blank' : undefined}
                      rel={('external' in link && link.external) ? 'noopener noreferrer' : undefined}
                      className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors inline-flex items-center gap-1"
                    >
                      {link.label}
                      {('external' in link && link.external) && <ExternalLink size={10} className="opacity-50" />}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="pt-8 border-t border-[var(--glass-border)] flex flex-col sm:flex-row items-center justify-between gap-4">
          <span className="text-xs text-[var(--text-tertiary)]">
            © 2026 Sarkar System. Built by Bittu.
          </span>
          <div className="flex items-center gap-4">
            <a
              href="https://discord.gg/KY7MkscD"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[var(--text-tertiary)] hover:text-brand-400 transition-colors"
              title="Discord"
            >
              <MessagesSquare size={16} />
            </a>
            <a
              href="https://www.youtube.com/@BittuSharmaRP"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[var(--text-tertiary)] hover:text-red-400 transition-colors"
              title="YouTube"
            >
              <PlayCircle size={16} />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
