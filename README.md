# 🧬 Stump the Agent — Build It By Voice, Run It On Flyte

An expo-booth challenge. A visitor walks up and **speaks a vague, half-serious
idea** out loud. Claude Code — with no keyboard, no programming from the visitor
— turns it into a **real Flyte pipeline**, runs it **in parallel on a live Flyte
devbox**, and hands back an interactive report to explore. Real distributed
compute, built from a sentence.

> The pitch to attendees: *"Give it a weird idea. Watch it build a real parallel
> data pipeline and run it — live. No code. No keyboard."*

> **Running the booth?** Setup, pre-flight, and operations live in
> [SETUP.md](SETUP.md).

---

## How it works (the booth loop)

```
Visitor speaks an idea
        │
        ▼
Claude writes a Flyte task  →  tasks/<name>.py
        │
        ▼
Runs it on the local devbox  →  ~8–16 parallel nodes (flyte.map)
        │
        ▼
Open the printed localhost:30080/v2/... URL  →  live DAG + explorable Report
        │
        ▼
Operator presses Cmd+K twice  →  work archived, context cleared, next visitor
```

Everything the visitor sees is generated on the spot. The **creative wildcard**
(a `--seed`, plus their own words woven in) means the same idea never produces
the same result twice — so nobody can dismiss it as a canned script.

---

## Prompt menu (hand this to shy visitors)

Each prompt has a **[blank you fill in]** — so no two runs are alike — and builds
in **phases**. Say the whole thing at once, or grow it across several prompts
("now add a tab for…", "now also try…"). Every one fans out across the devbox and
ends in an explorable report. (The `[bracketed]` part is the bit *you* make up.)

- 🧠 **Train a model & sweep it.** *"Train a little model to predict
  **[ramen prices / dragon weights / meme virality — your pick]**, try a hundred
  different settings in parallel, and tell me which one learned best."*
  → fabricate a dataset → fan out gradient-descent training across a
  hyperparameter grid → report: config leaderboard + loss curves + the winner.

- 🤖 **Turn loose a swarm of agents.** *"Open a market for **[a made-up commodity
  — moon rubble, artisanal pixels, bottled echoes]**, set loose a pack of trader
  bots with different strategies, run the trading in parallel, and crown whoever
  ends up richest."*
  → define the price model → simulate each bot in parallel → report: P&L
  leaderboard + equity curves + strategy head-to-head.

- 🧪 **Be an ML engineer.** *"Invent a few feature recipes for predicting
  **[taco ratings / asteroid danger — you choose]**, train a model on each recipe
  in parallel, then write up which one you'd ship and why."*
  → propose feature recipes → fan out train-and-score each → report: the agent's
  recommendation + recipe scoreboard.

- 🗄️ **Invent a database & interrogate it.** *"Invent a database about
  **[a dragon HR department / an interstellar food court — name the world]**,
  fill it with fake records, then answer a battery of questions about it in
  parallel and chart what you find."*
  → design a schema + generate rows → fan out analytical queries → report:
  charts + tables + the most surprising finding.

- 🖼️ **Generate and classify a gallery.** *"Generate a whole field of tiny
  pixel-art **[alien flora / cursed sandwiches — your call]**, then run a parallel
  classifier that sorts them by type and shows me the gallery."*
  → procedurally generate tile "images" → fan out classify each → report: a
  rendered pixel gallery grouped by class.

- 🌆 **Simulate it a thousand ways.** *"Simulate how **[a glitter spill / a
  dad-joke epidemic — pick one]** spreads across a city grid over time, run a few
  hundred random trials in parallel, and show me the average outcome plus the
  wildest single run."*
  → define the spread rules → fan out randomized Monte-Carlo trials → report:
  average heatmap over time + outcome distribution + the most extreme run.

Each forces Claude to make real engineering choices, fans out across the devbox,
and produces an explorable report — echoing the real-world shapes from the
[Flyte/Union tutorials](https://www.union.ai/docs/v2/union/tutorials) (HPO,
multi-agent simulation, MLE agents, text-to-SQL, image classification,
Monte-Carlo modeling).

---

## The rules Claude follows (see `CLAUDE.md`)
- **Stdlib only** — no extra packages, so there's never a slow image build.
- **Always runs on the devbox**, never `--local` (parallel map needs the real backend).
- **Always a report** — visitors get something to explore.
- **Stays in `tasks/`** — touches nothing else; doesn't deploy to any cloud.
