# ICCMAFIA-AI Agent Documentation (AGENTS.md)

Welcome, AI coding agent. This document serves as your comprehensive guide to the ICCMAFIA-AI codebase. Please review this document entirely before making any changes to the project.

## Project Overview
**ICCMAFIA-AI** is a static GitHub Pages site designed to teach the ICC (Indication → Correction → Continuation) trading framework, based on the Trades by Sci curriculum.
- **Live URL**: https://mrwallyst.github.io/ICCMAFIA/

## Full File Map
- `index.html` — The main course landing page and curriculum overview.
- `journal.html` — The comprehensive trading journal where users log trades, view analytics, and track psychology.
- `cheat-sheet.html` — The ICC blueprint reference, containing actionable checklists and setups.
- `psychology.html` — The psychology module, dedicated to mental resilience and avoiding emotional toxic loops.
- `comments.html` — Community comments and discussion sections.
- Asset folders (`/assets`, `/css`, `/js`, etc.) — Contains vanilla stylesheets, images, and scripts.

## Tech Stack
- **Languages**: Vanilla HTML, CSS, JavaScript ONLY.
- **Dependencies**: No frameworks, no npm, no build tools (e.g., React, Tailwind, Webpack are strictly forbidden).
- **Deployment**: Deploys automatically via GitHub Pages on push to the `main` branch.

## Hard Rules (NEVER BREAK THESE)
1. **No Frameworks Ever**: Vanilla code only. Do not install dependencies or suggest modern build tools.
2. **Local Storage Only**: All user data lives exclusively in the browser's `localStorage`. No backend, no database, no external APIs for user data tracking.
3. **Protect CSV Export/Import**: Never break the trading journal CSV import/export functionality. The expected columns must remain: `Date`, `Pair/Ticker`, `Direction`, `Result / P&L ($)`, `Tags`, `Notes & Analysis`.
4. **Preserve Aesthetics**: Keep the dark theme and existing design language (e.g., glassmorphism, specific hex codes).
5. **Educational Disclaimer**: Keep the educational disclaimer intact on every single page.
6. **Mobile Responsiveness**: All pages must be mobile-responsive. Always test UI changes at a minimum width of 375px.

## ICC Framework Context
The strategy is based on pure market structure and liquidity:
1. **Indication (The Explosion)**: A definitive sweep or break of a higher time frame (HTF) level or session liquidity. We NEVER trade this initial breakout.
2. **Correction (The Mess)**: The market retraces to grab liquidity from retail breakout traders. We monitor this on the lower time frame (LTF).
3. **Continuation (The Cleanup/Entry)**: The market realigns. Entry fires only when the LTF prints a Break of Structure (BOS) in the direction of the original indication.

**Key Terms Dictionary**:
- **BOS**: Break of Structure
- **CHoCH**: Change of Character (Micro-structure reversal)
- **OB**: Order Block
- **FVG**: Fair Value Gap
- **Liquidity Pool**: Areas where retail stops are resting
- **Sweeping Liquidity**: Institutional algorithms hunting and consuming those stops
- **HTF/LTF**: Higher Time Frame (1H/4H) / Lower Time Frame (5m/15m)
- **PDH/PDL**: Previous Day High / Previous Day Low
- **R:R**: Risk to Reward Ratio
- **ICC Inside ICC**: A fractal application of the ICC framework occurring on a micro level within a larger ICC setup.

## Trading Journal Features (`journal.html`)
The journal is fully offline and feature-rich. Key modules include:
- Trade logging
- Pre-market checklist
- Session breakdown analytics
- ICC setup analytics tracking
- Emotional state tracking
- Equity curve visualization
- Weekly reviews
- Multi-account support
- CSV import/export

## How to Test
- **Local Development**: Simply open `.html` files directly in your browser. No local server is required.
- **Journal Testing**: To test the journal, log a manual trade, export the CSV, delete the local storage data, re-import the CSV, and verify that all data (including the equity curve) populates correctly.

## Style Guide
- Match existing CSS classes precisely.
- Replicate the exact button styles (hover effects, borders), card styles (glassmorphism/translucency), and color palette (dark theme).
- Use matching emoji icons for UI elements as established in the current codebase.
- Maintain consistent typography and fonts.
