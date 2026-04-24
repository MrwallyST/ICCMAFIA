# ICCMAFIA-AI Context (CLAUDE.md)

**Project:** ICCMAFIA-AI (https://mrwallyst.github.io/ICCMAFIA/)
**Purpose:** Static site teaching the ICC (Indication → Correction → Continuation) trading framework + local trading journal.

## Core Rules (NEVER BREAK)
1. **Vanilla Only:** NO frameworks (React/Next), NO build tools (npm/Webpack), NO Tailwind. Just HTML/CSS/JS.
2. **Local Data Only:** All user data lives in `localStorage`. NO backend, NO database, NO external API calls.
3. **CSV Export/Import:** Never break the journal CSV logic. Columns: `Date`, `Pair/Ticker`, `Direction`, `Result / P&L ($)`, `Tags`, `Notes & Analysis`.
4. **Styling:** Keep the dark theme (`#0d1117`), system emojis, and mobile responsiveness (test at 375px).
5. **Disclaimer:** Keep the financial disclaimer visible on all pages.

## File Map
- `index.html`: Course hub and schedule.
- `journal.html`: The trading journal (trade logging, equity chart, weekly reviews, CSV tools, multi-account).
- `cheat-sheet.html`: Quick reference for ICC concepts.
- `psychology.html`: Mental state and discipline tracker.
- `comments.html`: Static community mock.
- `studios/`: Generated lesson assets (audio, flashcards, quizzes).

## Trading Context (ICC)
- **Phase 1 (Indication):** Market breaks structure (BOS/CHoCH).
- **Phase 2 (Correction):** Pullback to a reaction zone (Order Block/FVG) to sweep liquidity.
- **Phase 3 (Continuation):** The actual move in the Indication's direction.

## Testing workflow
1. Open `.html` files directly in the browser (`file://`).
2. For `journal.html`: Manually add a trade → Export CSV → Clear local storage → Import CSV → Verify data intact.
