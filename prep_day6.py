import os

base_dir = r"C:\Users\cesar\Documents\New folder\TradesBySci\studios\day-6"

files = {
    "day6_study.md": """# Day 6 Study Guide: Timeframe Correlation — The Multi-Timeframe Framework

### 1. The Core Problem: Why Single-Timeframe Traders Always Lose
Most retail traders pick one chart — usually the 5-minute or 15-minute — and try to make all their decisions from that single view. This is the equivalent of trying to navigate a city by only looking at a one-block radius. You have no context, no direction, and no idea what's coming next.

**Timeframe Correlation** is the discipline of reading multiple timeframes in alignment — top-down — so that every trade entry you take has the full weight of higher-timeframe structure behind it.

The rule is simple: **A lower timeframe signal is only valid when it aligns with the higher timeframe direction.**

---
### 2. The Three-Tier Timeframe Hierarchy
The ICC framework uses a strict top-down hierarchy. Each tier has a specific job:
| Tier | Timeframe | Purpose |
| :--- | :--- | :--- |
| **Tier 1 — The Map** | Daily / 4-Hour | Overall trend direction & macro bias. This is the "big picture." |
| **Tier 2 — The Setup** | 1-Hour | Where is price in relation to key structural levels? |
| **Tier 3 — The Entry** | 15-Minute / 5-Minute | Pinpoint precision entry after the higher timeframes have aligned. |

**Critical Rule:** You NEVER use the 15-minute chart to determine direction. You use it ONLY to pull the trigger.

---
### 3. Understanding Correlation — The Traffic Light System
- 🔴 **Red (Daily/4H):** The overall trend direction. Are you in a bullish or bearish macro environment?
- 🟡 **Yellow (1-Hour):** The setup zone. Is price at a key reaction level?
- 🟢 **Green (15-Min):** The entry trigger.

**All three lights must be aligned before you pull the trigger.**

---
### 4. The Mistake of Timeframe Hopping
**Timeframe hopping** is when a trader switches timeframes to find a signal that confirms what they *want* to see. This is one of the most destructive habits in trading.

**The fix:** Commit to your analysis hierarchy **before** you look for entries. If the 1H says bearish, you only look for sells.

---
### 5. Final Rules
- **Higher timeframe always wins.**
- **Trade top-down, every single time.**
- **One bias per session.**
- **Zoom out when confused.**""",

    "day6_quiz.md": """# Day 6 Quiz: Timeframe Correlation

## Question 1
**What is the primary purpose of Timeframe Correlation in the ICC framework?**
- A) To find more entry signals by checking multiple charts
- B) To use lower timeframes to override higher timeframe signals
- **C) To ensure every trade entry is confirmed by higher-timeframe structural alignment ✓**
- D) To reduce the amount of time spent analyzing charts

> **Hint:** Think about why having the "big picture" context matters before executing a trade.

---
## Question 2
**According to the three-tier hierarchy, what is the SOLE purpose of the 15-Minute timeframe?**
- A) To determine the overall trend direction for the week
- **B) To provide a precise execution trigger AFTER higher timeframes are confirmed ✓**
- C) To identify major swing highs and swing lows
- D) To analyze the macro bias of the market

---
## Question 3
**What is "timeframe hopping" and why is it destructive?**
- A) Switching between Gold and NASDAQ to find better opportunities
- **B) Dropping to lower timeframes to find signals that confirm what you already want to do ✓**
- C) Using the Daily chart to override a 15-minute entry signal
- D) Trading on multiple timeframes simultaneously

---
## Question 4
**What does "confluence" mean in the context of timeframe correlation?**
- A) When two different assets move in the same direction at the same time
- B) When the market makes a false breakout on the 15-minute chart
- **C) When multiple timeframes all point to the same price level simultaneously ✓**
- D) When you use three different indicators on the same chart""",

    "day6_flashcards.json": """{
  "cards": [
    { "front": "What is 'Timeframe Correlation' in the ICC framework?", "back": "The discipline of reading multiple timeframes in alignment (top-down) so that every trade entry has the full weight of higher-timeframe structure confirming it." },
    { "front": "What are the three tiers of the timeframe hierarchy?", "back": "Tier 1: Daily/4-Hour (Map — overall direction). Tier 2: 1-Hour (Setup — structural analysis). Tier 3: 15-Minute/5-Minute (Entry — execution trigger)." },
    { "front": "What is the job of the Daily / 4-Hour timeframe?", "back": "To determine the overall trend direction and macro bias. It answers: 'Where is price going long-term?'" },
    { "front": "What is the job of the 1-Hour timeframe?", "back": "To identify where price is in relation to key structural levels — specifically, to confirm when a Correction is completing and where the entry zone is." },
    { "front": "What is the job of the 15-Minute timeframe?", "back": "Precision execution only. You use it to pull the trigger AFTER Tier 1 (4H) and Tier 2 (1H) are already confirmed. Never for determining direction." },
    { "front": "What is the 'Traffic Light System' in timeframe correlation?", "back": "Red (4H) = direction. Yellow (1H) = setup zone. Green (15M) = entry trigger. All three must be aligned before trading." },
    { "front": "Can you look for buys on the 1H if the 4H is bearish?", "back": "No. The higher timeframe always wins. If the 4H is bearish, you only look for sells — period." }
  ]
}""",

    "day6_mindmap.json": """{
  "name": "Day 6: Timeframe Correlation",
  "children": [
    {
      "name": "The Three-Tier Hierarchy",
      "children": [
        { "name": "Tier 1: Daily / 4H — The Map (Direction)" },
        { "name": "Tier 2: 1-Hour — The Setup (Structure)" },
        { "name": "Tier 3: 15-Minute — The Entry (Execution)" }
      ]
    },
    {
      "name": "The Traffic Light System",
      "children": [
        { "name": "RED: 4H Macro Bias" },
        { "name": "YELLOW: 1H Setup Zone" },
        { "name": "GREEN: 15M Entry Trigger" }
      ]
    }
  ]
}""",

    "day6_blog.md": """# Day 6 Blog Post: Why You're Trading the Wrong Timeframe

The single most common reason retail traders lose consistently isn't their entry technique. It's not their risk management. It's simpler than that: **they're staring at the wrong chart.**

Day 6 of the ICC series tackles this head-on with a concept called **Timeframe Correlation**.

## The Three-Tier Hierarchy
**Tier 1: The Map (Daily / 4-Hour)** Your macro bias.
**Tier 2: The Setup (1-Hour)** Your structural confirmation layer.
**Tier 3: The Trigger (15-Minute)** Execution only.

## The Timeframe Hopping Trap
The most dangerous habit in trading is **timeframe hopping** — dropping to a lower timeframe to justify a trade you've already decided you want to take. The fix: determine your bias top-down BEFORE looking for entries.""",

    "day6_newsletter.md": """# Day 6 Newsletter: The Secret Multi-Timeframe System

**Subject Line:** Why 90% of traders stare at the wrong chart (and what to do instead)

Hey [First Name],

Quick question: what timeframe do you usually trade on?

If your answer is anything below the 1-hour, we need to talk.

Day 6 of the ICCMAFIA AI series just dropped — and it covers the concept that took my trading from emotional guessing to structured confidence: **Timeframe Correlation.**

Before ANY trade, run this checklist:
🔴 **4H:** Bullish or bearish? (Your direction)
🟡 **1H:** Is the ICC setup forming at your level? (Your setup)
🟢 **15M:** Has the correction broken structure in your favor? (Your trigger)

All available now at **ICCMAFIA.ai**""",

    "day6_twitter.md": """# Day 6 Twitter Thread: Timeframe Correlation

**1/10**
Most traders lose because they stare at one timeframe and wonder why the market "doesn't make sense."

**2/10**
There are 3 timeframes you need. That's it.
🗺️ 4H/Daily = The MAP (direction)
⚙️ 1-Hour = The SETUP (structure)
🎯 15-Min = The TRIGGER (execution)

**3/10**
Think of it like a traffic light:
🔴 4H = Are you bullish or bearish?
🟡 1H = Is your setup forming at the right level?
🟢 15M = Is the correction over? Pull the trigger.

**4/10**
Why do lower timeframes lie? On the 5-minute chart, a correction looks like a crash. Zoom out to the 1H and suddenly — it's just a pullback before continuation.""",

    "day6_tiktok.md": """## [0:00-0:03] HOOK
"You've been staring at the wrong chart this whole time."

## [0:03-0:10] PAIN
"If you trade the 5-minute without checking the 1-hour and 4-hour first — the market will eat you alive. Every. Single. Time."

## [0:10-0:20] THE SYSTEM
"Day 6 of the ICC course gives you the exact framework: Timeframe Correlation.
🗺️ 4H → Direction
⚙️ 1H → Setup
🎯 15M → Pull the trigger."

## [0:20-0:28] THE RULE
"All three must align. Think of it like a traffic light.
Red 4H? Don't trade.
Yellow 1H? Wait for setup.
Green 15M? Execute." """,

    "day6_ytscript.md": """# Day 6 YouTube Script: Timeframe Correlation

**[INTRO — 0:00-0:30]**
What's up ICCMAFIA — welcome back. Day 6. And today we're covering the concept that will make everything you've learned in Days 1 through 5 actually click into place: Timeframe Correlation.

**[PROBLEM — 0:30-1:30]**
Let me ask you something. What chart are you trading on right now? 5-minute? 15-minute? 1-minute?
Here's the hard truth: if you're starting your analysis on a lower timeframe, you are driving without a map.

**[THE THREE-TIER SYSTEM — 1:30-4:00]**
The ICC framework uses three timeframes. Each has a specific job.
Tier 1 is the Daily and 4-Hour. This is your MAP. 
Tier 2 is the 1-Hour. This is your SETUP layer.
Tier 3 is the 15-Minute. This is EXECUTION ONLY.

**[TRAFFIC LIGHT — 4:00-5:30]**
I want you to think of it as a traffic light. Before any trade, you run three checks. All three green — you execute. One red — you wait. This single process eliminates 80% of bad entries.""",

    "day6_ig.md": """## Day 6: Timeframe Correlation — Instagram Caption

🚦 The reason most traders lose isn't their entry.
It's that they're staring at the WRONG chart.

Day 6 of the ICC series drops the framework that changed everything:
**Timeframe Correlation.**

🗺️ 4H/Daily → Direction
⚙️ 1-Hour → Setup
🎯 15-Min → Execution

All three must align before you trade. One red light = no trade. Period.

Study guide + flashcards + quiz now live at ICCMAFIA.ai 🔗 Link in bio.

#Trading #DayTrading #Futures #NASDAQ #Gold #PriceAction #ICC #TradesBySci""",

    "day6_linkedin.md": """# Day 6 LinkedIn Post: Timeframe Correlation

Most retail traders analyze markets the wrong way. They open a 5-minute chart, see a pattern, and enter. No context. No structure. No direction.

Day 6 of the ICC curriculum addresses this with **Timeframe Correlation** — the framework every professional trader uses.

📊 **Tier 1 — Daily/4H:** Macro bias. Bullish or bearish for this session?
📊 **Tier 2 — 1-Hour:** Where is the ICC correction completing? What is the reaction zone?
📊 **Tier 3 — 15-Minute:** Execute. The 15M gives you the precise entry trigger.

**The rule that changes everything:** Higher timeframe always wins.

Day 6 is live at ICCMAFIA.ai. #Trading #FuturesTrading #TradingStrategy #ICC #PriceAction #NASDAQ #Gold #TradingEducation""",

    "day6_datatable.md": """| Timeframe | Tier | Role | Analysis Focus | What You Mark |
|---|---|---|---|---|
| Daily | Tier 1 (Map) | Macro bias | Overall trend direction | Major swing highs, swing lows |
| 4-Hour | Tier 1 (Map) | Macro confirmation | Key structural levels | Swing highs/lows, broken structure points |
| 1-Hour | Tier 2 (Setup) | ICC setup identification | Correction completion | Entry zone, expected reaction level |
| 15-Minute | Tier 3 (Trigger) | Entry execution | Break of Structure | Entry trigger, stop loss placement |
| 5-Minute | ❌ NOT USED | Too much noise | N/A | N/A |

## Signal Quality Matrix
| 4H Bias | 1H Setup | 15M Trigger | Setup Grade |
|---|---|---|---|
| ✅ Bullish | ✅ Higher low at reaction level | ✅ BOS upside | **A+ — Full Confluence** |
| ✅ Bullish | ✅ Higher low forming | ❌ No BOS yet | **B — Wait for trigger** |
| ❌ Bearish | ✅ "Bullish" 1H signal | ✅ 15M buy | **F — Never take this — fighting 4H** |""",

    "day6_faq.md": """# Day 6 FAQ: Timeframe Correlation

**Q: Why can't I just use the 1-hour chart for everything?**
A: The 1H is your setup layer, not your direction layer. Without the 4H and Daily context, a 1H setup could be forming against the dominant macro trend. 

**Q: Can I use the 5-minute chart for entries instead of the 15-minute?**
A: The ICC framework uses the 15-minute as the minimum execution timeframe. Below that, the noise-to-signal ratio is too high. 

**Q: What if the Daily and 4H disagree?**
A: This means the 4H is in a correction within a larger bullish trend. Wait for the 4H correction to complete and confirm the bullish Daily trend is resuming.

**Q: What's the biggest sign I'm timeframe hopping?**
A: You already know what you want to trade BEFORE you analyze. If you open TradingView thinking "I want to buy NQ today" and then go looking for a signal — that's hopping."""
}

for filename, content in files.items():
    filepath = os.path.join(base_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.strip())

print("Created 13 files in studios/day-6/")
