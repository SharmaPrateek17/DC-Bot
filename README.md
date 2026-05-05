<p align="center">
  <img src="https://img.shields.io/badge/Bot-Sarkar%20System-7C3AED?style=for-the-badge&logo=discord&logoColor=white" alt="Sarkar System" />
  <img src="https://img.shields.io/badge/Runtime-Python%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Frontend-Next.js%2016-000000?style=for-the-badge&logo=next.js&logoColor=white" alt="Next.js" />
  <img src="https://img.shields.io/badge/Hosted-Vercel%20%2B%20Katabump-00C7B7?style=for-the-badge&logo=vercel&logoColor=white" alt="Hosting" />
</p>

# Sarkar System

> A comprehensive Discord server management platform combining an automated event bot with a modern web dashboard — built for GTA RP gaming communities.

---

## Developer

| Field | Details |
|-------|---------|
| **Name** | Prateek Sharma |
| **Email** | psharma180712@gmail.com |
| **GitHub** | [@SharmaPrateek17](https://github.com/SharmaPrateek17) |
| **Role** | Full-Stack Developer & Project Owner |

---

## Project Overview

Sarkar System is a two-part platform designed to automate event management, member coordination, and server moderation for Discord-based gaming communities. It consists of:

1. **Sarkar Bot** — A Python-powered Discord bot that handles scheduled events, participant registration, role-based moderation, and automated notifications.
2. **Sarkar Dashboard** — A Next.js 16 web application providing a premium landing page and an interactive control panel for real-time server monitoring.

Both components work in tandem: the bot runs 24/7 on a Katabump VPS handling Discord operations, while the dashboard is deployed on Vercel for public access.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Sarkar System                     │
├──────────────────────┬──────────────────────────────┤
│    Discord Bot       │      Web Dashboard           │
│   (Python 3.12)      │     (Next.js 16 + React 19)  │
│                      │                              │
│  ┌────────────────┐  │  ┌────────────────────────┐  │
│  │  Event Engine   │  │  │  Landing Page           │  │
│  │  (Scheduler)    │  │  │  (Hero, Features, CTA)  │  │
│  ├────────────────┤  │  ├────────────────────────┤  │
│  │  Cog Modules    │  │  │  Dashboard Panel        │  │
│  │  - Ban Manager  │  │  │  (Live Stats, Events)   │  │
│  │  - Cmd Center   │  │  ├────────────────────────┤  │
│  │  - Deep Clean   │  │  │  Commands Reference     │  │
│  │  - Clean Panel  │  │  ├────────────────────────┤  │
│  ├────────────────┤  │  │  Members Directory       │  │
│  │  Flask Dashboard│  │  └────────────────────────┘  │
│  │  (Web API)      │  │                              │
│  └────────────────┘  │  Styling: Tailwind CSS 4      │
│                      │  Animations: Framer Motion     │
│  Host: Katabump VPS  │  3D: React Three Fiber        │
│  Node: GRA-N54       │  Auth: Clerk                  │
│                      │  Host: Vercel                 │
└──────────────────────┴──────────────────────────────┘
```

---

## Features

### Discord Bot

| Category | Capabilities |
|----------|-------------|
| **Event Automation** | Scheduled event sessions across 6 channel categories — Informal, State Control, Biz War, RP Ticket, Other Events, and Special Events. Automatic session opening/closing with configurable timers. |
| **Registration System** | Reaction-based participant registration with live embed updates, slot counters, waiting lists, and auto-promoted queues when members cancel. |
| **Multi-Tier Reminders** | RP Factory reminders at 60, 45, 30, 15, and 5 minutes before events. Dedicated early alerts for Biz War, Mall, Bank Robbery, and Drug Lab. |
| **Pager System** | Configurable mass-notification pager with 6 tone categories (Serious, Motivational, Funny, Hype, Threat, Chill) for calling members to events. |
| **Moderation Cogs** | Ban Manager for tracking and auditing bans. Command Center for centralized admin controls. Deep Clean and Clean Panel for bulk message management. |
| **Announcement Engine** | Template-based announcement system with save/load functionality and rich embed formatting. |
| **GIF Integration** | Dynamic GIF attachments for event embeds and bot messages, configurable via JSON files without code changes. |
| **Leaderboard** | All-time participation leaderboard tracking member engagement across events. |
| **Flask Web Dashboard** | Built-in web panel with Discord OAuth authentication, profile pages, event scheduling, moderation tools, and server statistics. |

### Web Dashboard (Next.js)

| Section | Description |
|---------|-------------|
| **Landing Page** | Premium dark-themed hero section with 3D particle background, animated typography, and smooth scroll transitions. |
| **Features Showcase** | Interactive feature cards with modal detail views highlighting bot capabilities. |
| **Commands Reference** | Searchable command documentation for server members. |
| **Dashboard Panel** | Real-time event monitoring, role management, server statistics, and bot status indicators. |
| **Members Page** | Directory view of active server participants. |
| **Responsive Design** | Fully responsive layout optimized for desktop and mobile viewports. |

---

## Tech Stack

### Backend (Discord Bot)

| Technology | Purpose |
|-----------|---------|
| Python 3.12 | Core runtime |
| discord.py 2.x | Discord API wrapper |
| Flask | Embedded web dashboard server |
| aiohttp | Asynchronous HTTP requests |
| pytz | Timezone-aware event scheduling (UK Time) |
| aiosqlite | Lightweight async database operations |
| python-dotenv | Environment variable management |

### Frontend (Web Dashboard)

| Technology | Purpose |
|-----------|---------|
| Next.js 16 | React framework with App Router |
| React 19 | UI component library |
| Tailwind CSS 4 | Utility-first styling |
| Framer Motion | Page transitions and micro-animations |
| React Three Fiber | 3D WebGL particle backgrounds |
| Three.js | 3D rendering engine |
| Recharts | Data visualization charts |
| Clerk | Authentication and user management |
| Lucide React | Icon library |

---

## Project Structure

```
DC-Bot/
├── sarkar-bot/                  # Discord bot (Python)
│   ├── Bot.py                   # Main bot file (~3,400 lines)
│   ├── requirements.txt         # Python dependencies
│   ├── cogs/                    # Modular command extensions
│   │   ├── ban_manager.py       # Ban tracking and audit system
│   │   ├── command_center.py    # Centralized admin commands
│   │   ├── deep_clean.py        # Bulk message deletion
│   │   └── clean_panel.py       # Interactive cleanup panel
│   ├── config/                  # Runtime configuration
│   │   ├── eventGifs.json       # Event-specific GIF mappings
│   │   ├── botGifs.json         # General bot GIF assets
│   │   └── annTemplates.json    # Announcement templates
│   └── dashboard/               # Flask web dashboard
│       ├── server.py            # Flask routes and API
│       ├── auth.py              # Discord OAuth handler
│       └── templates/           # HTML templates (16 pages)
├── src/                         # Next.js web dashboard
│   ├── app/                     # App Router pages
│   │   ├── page.tsx             # Landing page
│   │   ├── layout.tsx           # Root layout
│   │   ├── globals.css          # Global styles
│   │   ├── dashboard/           # Dashboard panel
│   │   ├── commands/            # Commands reference
│   │   └── members/             # Members directory
│   └── components/              # React components
│       ├── Hero.tsx             # Hero section with 3D background
│       ├── SarkarHero3D.tsx     # Three.js particle system
│       ├── ParticleBackground.tsx # Animated particles
│       ├── Navbar.tsx           # Navigation bar
│       ├── Features.tsx         # Feature showcase grid
│       ├── About.tsx            # About section
│       ├── CTA.tsx              # Call-to-action section
│       ├── Footer.tsx           # Site footer
│       ├── CodeBlock.tsx        # Code display component
│       ├── FeatureCard.tsx      # Feature card with modal
│       ├── FeatureModal.tsx     # Feature detail modal
│       ├── PageTransition.tsx   # Framer Motion transitions
│       ├── ThemeProvider.tsx    # Dark/light theme toggle
│       └── panels/             # Dashboard sub-panels
├── Deploy.py                    # One-click Katabump deployment
├── package.json                 # Node.js dependencies
├── next.config.ts               # Next.js configuration
├── tsconfig.json                # TypeScript configuration
├── vercel.json                  # Vercel deployment config
└── .env                         # Environment variables (gitignored)
```

---

## Event Schedule

The bot operates on **UK Time (Europe/London)** and manages the following automated event categories:

| Category | Frequency | Events |
|----------|-----------|--------|
| Informal | Every hour at :30 | General participation events |
| Biz War | Twice daily (01:05, 19:05) | 25-slot organized PvP battles |
| State Control | Daily at 16:00 | 10-slot territorial control |
| RP Ticket Factory | Three times daily (10:30, 16:30, 22:30) | 25-slot RP earning sessions |
| Other Events | Throughout the day | Weed Farm, Harbor, Hotel Takeover, Weapons Factory, Foundry |
| Special Events | Scheduled days | Mall, Bank Robbery, Prison Protection, Drug Lab |

---

## Deployment

### Web Dashboard (Vercel)

The Next.js dashboard auto-deploys from the `main` branch via Vercel's GitHub integration. Every push triggers a new production build.

### Discord Bot (Katabump VPS)

Deploy the bot to Katabump with a single command:

```bash
python Deploy.py
```

This script uploads all bot files (Bot.py, cogs, configs, dashboard templates, and .env) to the Katabump server via SFTP. After deployment, restart the server from the [Katabump Control Panel](https://control.katabump.com).

---

## Environment Variables

Create a `.env` file in the project root with the following:

```env
DISCORD_TOKEN=your_discord_bot_token
FLASK_SECRET=your_flask_secret_key

DISCORD_CLIENT_ID=your_discord_client_id
DISCORD_CLIENT_SECRET=your_discord_client_secret

NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
CLERK_SECRET_KEY=your_clerk_secret_key
```

---

## Local Development

### Web Dashboard

```bash
npm install
npm run dev
```

Opens at [http://localhost:3000](http://localhost:3000).

### Discord Bot

```bash
cd sarkar-bot
pip install -r requirements.txt
python Bot.py
```

Requires a valid `DISCORD_TOKEN` in the `.env` file.

---

## License

This project is proprietary software developed by **Prateek Sharma**. All rights reserved. Unauthorized reproduction or distribution is prohibited without explicit written consent from the developer.

---

<p align="center">
  <sub>Engineered with precision by <strong>Prateek Sharma</strong> — psharma180712@gmail.com</sub>
</p>
