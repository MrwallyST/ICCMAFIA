# AGENTS.md — System Context for AI Coding Agents

## 1. Project Overview
**Name:** ICCMAFIA-AI
**Purpose:** A static educational platform and trading journal for teaching the ICC (Indication → Correction → Continuation) trading framework, derived from the Trades by Sci curriculum.
**Live URL:** https://mrwallyst.github.io/ICCMAFIA/

This project serves as both an educational portal (housing course days, study guides, and flashcards) and a functional local trading journal with psychology tracking and CSV import/export functionality.

---

## 2. Technology Stack & Hard Rules
This project is built for pure simplicity, durability, and immediate local deployment. 

**Tech Stack:**
- Pure Vanilla HTML5
- Pure Vanilla CSS3
- Pure Vanilla JavaScript
- **NO FRAMEWORKS.** No React, no Next.js, no Vue, no Tailwind.
- **NO BUILD TOOLS.** No npm, no Webpack, no Vite.
- **DEPLOYMENT:** Deploys automatically via GitHub Pages upon push to the `main` branch.

### 🔴 HARD RULES THAT MUST NEVER BE BROKEN 🔴
1. **NO FRAMEWORKS:** Never introduce React, Node.js, npm, Tailwind, or any build steps.
2. **LOCAL STORAGE ONLY:** All user data (trades, screenshots, journal entries, weekly reviews) MUST live entirely in `localStorage` (and IndexedDB for images if applicable). There is NO backend, NO database (no PostgreSQL/MongoDB), and NO external API calls for user data. Privacy and local execution are paramount.
3. **CSV INTEGRATION MUST SURVIVE:** Never break the trading journal CSV import/export workflow. The parser explicitly expects these columns:
   - `Date`
   - `Pair/Ticker`
   - `Direction`
   - `Result / P&L ($)`
   - `Tags`
   - `Notes & Analysis`
4. **MAINTAIN DESIGN LANGUAGE:** Keep the dark theme (`#0d1117` background, `#161b22` surface, slate/blue accents). Match existing styling for buttons, cards, typography (Inter/system fonts), and emoji icon usage.
5. **DISCLAIMERS:** The educational/financial risk disclaimer must remain visible on the bottom of every page.
6. **MOBILE RESPONSIVE:** Every page must work perfectly on mobile devices down to 375px width.

---

## 3. Full File Map

| File / Folder | Purpose |
|---------------|---------|
| `index.html` | The main hub/course page. Contains the schedule for course days and links to the assets for each day. |
| `journal.html` | The core trading application. Includes trade logging, dashboard stats, emotional tracking, and weekly reviews. |
| `cheat-sheet.html` | The quick reference guide for the ICC blueprint, setups, and rules. |
| `psychology.html` | The psychology module, tracking mental states, revenge trading, and emotional discipline. |
| `comments.html` | A static community comments/discussion interface mock. |
| `calendar.html` | A visual calendar view of trading performance and events. |
| `seo-strategy-tradesbysci.html` | Internal SEO strategy documentation/landing page experiment. |
| `studios/` | Directory containing all generated assets (Markdown, JSON flashcards, MP3s, infographics, etc.) for each course "Day". |
| `sw.js` / `manifest.json` | Progressive Web App (PWA) configuration files for offline/mobile app installation. |

---

## 4. The ICC Trading Framework Context
Agents must understand the domain language to write appropriate UI text and tools. 
**ICC stands for: Indication → Correction → Continuation.**

### The Three Phases:
1. **Indication (Phase 1):** The market breaks a significant structural level, indicating a shift in momentum or trend.
2. **Correction (Phase 2):** The market pulls back to a logical reaction zone (like an Order Block or FVG) to trap retail traders and gather liquidity.
3. **Continuation (Phase 3):** The market resumes the direction of the Indication, sweeping liquidity and delivering the actual move.

### Key Trading Terminology Used Here:
- **BOS:** Break of Structure (Continuation of a trend).
- **CHoCH:** Change of Character (The first sign of a trend reversal).
- **OB:** Order Block (Last candle before an impulsive move).
- **FVG:** Fair Value Gap (An imbalance in price delivery).
- **Liquidity Pool:** Areas where retail stop-losses are clustered (usually above old highs or below old lows).
- **Sweeping Liquidity:** Market makers pushing price past a level to trigger stop-losses before reversing.
- **HTF / LTF:** Higher Timeframe / Lower Timeframe.
- **PDH / PDL:** Previous Daily High / Previous Daily Low.
- **R:R:** Risk-to-Reward ratio.
- **ICC Inside ICC:** The fractal nature of the market; seeing the 3-phase pattern on a 15M chart happening inside the Correction phase of a 4H chart.

---

## 5. Trading Journal Features (`journal.html`)
The `journal.html` file is a complex, stateful Vanilla JS application. It includes:
- **Trade Logging:** Modal for inputting Date, Pair, Direction, P&L, Tags, and Notes.
- **Pre-Market Checklist:** Daily checkboxes to ensure emotional and technical readiness.
- **Session Breakdown:** Analytics showing performance based on time of day.
- **ICC Setup Analytics:** Tracking win rates specifically for ICC setups.
- **Emotional State Tracking:** Logging psychology and mistakes (e.g., FOMO, Revenge Trading).
- **Equity Curve Chart:** Visual representation of cumulative P&L using Chart.js.
- **Weekly Reviews:** A modal system that calculates the current week's stats and saves a weekly journal entry (what went well, rules broken, goals).
- **Multi-Account Support:** Ability to switch between different trading accounts/prop firms and rename them.
- **CSV Import/Export:** Crucial data portability feature mapping local state to a standard spreadsheet format.

---

## 6. How to Test & Develop
- **Local Testing:** You do not need a local server. You can literally double-click `index.html` or `journal.html` to open them in the browser. File:// protocol works perfectly.
- **Journal Testing:** If making changes to `journal.html`, verify the data pipeline:
  1. Add a manual trade via the UI.
  2. Export the CSV.
  3. Delete the local storage / reset the app.
  4. Import the CSV.
  5. Verify the trade, P&L, tags, and equity curve restored accurately.
- **Mobile Testing:** Use Chrome DevTools device toolbar. Ensure layout does not break at 375px (iPhone SE width).

---

## 7. Style Guide & UI Conventions
When adding new UI elements, strictly adhere to the existing code:
- **Colors:** Background is `var(--bg)` (`#0d1117`), cards are `var(--surface)` (`#161b22`). Accents are specific hex codes (e.g., `var(--accent)` for primary buttons). Text is `var(--text)` and `var(--muted)`.
- **Buttons:** Match the `border-radius: 8px` or `12px`, with slight hover transitions (`transition: 0.2s; filter: brightness(1.1)`).
- **Cards:** Use `border: 1px solid var(--border)` with appropriate padding (e.g., `20px`).
- **Icons:** We use native system emojis (📈, ⚙️, 📝, 💰, 🗑️) instead of external icon libraries (no FontAwesome, no SVG sprites) for maximum performance and simplicity.
- **CSS Architecture:** Styles are embedded directly in the `<head>` of the respective HTML files. Keep it that way to maintain the single-file portability of the tools.
