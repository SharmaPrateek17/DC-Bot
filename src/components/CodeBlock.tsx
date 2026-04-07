'use client';

import { motion } from 'framer-motion';
import { useState } from 'react';
import { Copy, Check } from 'lucide-react';

const codeLines = [
  { indent: 0, parts: [
    { text: 'const', cls: 'code-keyword' },
    { text: ' bot ', cls: '' },
    { text: '=', cls: 'code-punctuation' },
    { text: ' sarkar', cls: 'code-object' },
    { text: '.', cls: 'code-punctuation' },
    { text: 'events', cls: 'code-property' },
    { text: '.', cls: 'code-punctuation' },
    { text: 'create', cls: 'code-method' },
    { text: '({', cls: 'code-punctuation' },
  ]},
  { indent: 1, parts: [
    { text: 'name', cls: 'code-property' },
    { text: ':  ', cls: 'code-punctuation' },
    { text: "'RP Factory'", cls: 'code-string' },
    { text: ',', cls: 'code-punctuation' },
  ]},
  { indent: 1, parts: [
    { text: 'time', cls: 'code-property' },
    { text: ':  ', cls: 'code-punctuation' },
    { text: "'8:00 PM IST'", cls: 'code-string' },
    { text: ',', cls: 'code-punctuation' },
  ]},
  { indent: 1, parts: [
    { text: 'slots', cls: 'code-property' },
    { text: ': ', cls: 'code-punctuation' },
    { text: '20', cls: 'code-number' },
    { text: ',', cls: 'code-punctuation' },
  ]},
  { indent: 1, parts: [
    { text: 'reminders', cls: 'code-property' },
    { text: ': ', cls: 'code-punctuation' },
    { text: 'true', cls: 'code-keyword' },
    { text: ',', cls: 'code-punctuation' },
  ]},
  { indent: 0, parts: [
    { text: '});', cls: 'code-punctuation' },
  ]},
  { indent: 0, parts: [] },
  { indent: 0, parts: [
    { text: '// ✅ Event created with automatic 10-min reminders', cls: 'code-comment' },
  ]},
];

const plainCode = `const bot = sarkar.events.create({
  name:  'RP Factory',
  time:  '8:00 PM IST',
  slots: 20,
  reminders: true,
});

// ✅ Event created with automatic 10-min reminders`;

export default function CodeBlock() {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(plainCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="code-block shadow-2xl shadow-black/20">
      {/* Header bar */}
      <div className="code-block-header">
        <div className="code-block-dots">
          <span />
          <span />
          <span />
        </div>
        <span className="ml-3 text-[var(--text-tertiary)] text-xs">events.ts</span>
        <div className="ml-auto">
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={handleCopy}
            className="p-1 rounded text-[var(--text-tertiary)] hover:text-[var(--text-secondary)] transition-colors"
            title="Copy code"
          >
            {copied ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
          </motion.button>
        </div>
      </div>

      {/* Code content */}
      <pre className="text-[var(--text-primary)]">
        <code>
          {codeLines.map((line, lineIdx) => (
            <motion.div
              key={lineIdx}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 + lineIdx * 0.06, duration: 0.3 }}
              className="leading-relaxed"
            >
              {'  '.repeat(line.indent)}
              {line.parts.map((part, partIdx) => (
                <span key={partIdx} className={part.cls}>{part.text}</span>
              ))}
              {line.parts.length === 0 && '\n'}
            </motion.div>
          ))}
        </code>
      </pre>
    </div>
  );
}
