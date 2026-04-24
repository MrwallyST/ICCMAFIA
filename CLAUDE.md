# ICCMAFIA-AI (Claude Code Reference)

**Project URL**: https://mrwallyst.github.io/ICCMAFIA/
**Description**: Static educational site & local trading journal for the ICC (Indication -> Correction -> Continuation) methodology.

## File Map
- `index.html`: Main course page
- `journal.html`: Trading journal
- `cheat-sheet.html`: ICC blueprint reference
- `psychology.html`: Psychology module
- `comments.html`: Community comments

## Tech Stack & Hard Rules
- **Vanilla HTML/CSS/JS ONLY.** No frameworks, no build tools, no npm.
- **Local Storage ONLY.** No backends, no DBs. 
- **DO NOT BREAK CSV Import/Export.** Required columns: Date, Pair/Ticker, Direction, Result / P&L ($), Tags, Notes & Analysis.
- **Maintain Aesthetics:** Dark theme, glassmorphism, existing CSS class structure, emoji usage.
- **Disclaimers & Mobile:** Educational disclaimer must stay on all pages. Minimum width: 375px.

## ICC Framework & Vocabulary
- **3 Phases**: Indication (initial sweep, DO NOT TRADE), Correction (pullback), Continuation (BOS entry).
- **Terms**: BOS, CHoCH, OB, FVG, Liquidity Pool, Sweeping Liquidity, HTF/LTF, PDH/PDL, R:R, ICC Inside ICC.

## Testing & Journal Features
- **Features**: Pre-market checklist, session analytics, emotional tracking, equity curve, multi-account, import/export.
- **Testing**: Open `.html` locally (no server). Test journal changes by logging a trade -> Export CSV -> Clear Storage -> Re-import CSV -> Verify data & equity curve.
