"""
A whole field of tiny pixel-art CURSED SANDWICHES.

Pipeline:
  1. fan out N generator tasks  -> each paints one cursed sandwich (pixel grid)
  2. fan out N classifier tasks  -> each independently inspects the pixels and
     decides what *kind* of curse it is (it does not get told — it reads the art)
  3. one report task             -> a gallery, grouped by type

Standard library only. Runs on the devbox. Ends in a flushed Report.
"""

import asyncio
import random

import flyte
import flyte.report

env = flyte.TaskEnvironment(name="cursed_sandwiches")

# pixel palette: char -> (hex color, human label, feature it signals)
PALETTE = {
    ".": ("transparent", "void", None),
    "B": ("#e0b070", "bun", None),
    "b": ("#9c6b3c", "crust", None),
    "L": ("#6abe30", "lettuce", None),
    "M": ("#a33b3b", "meat", None),
    "C": ("#ffd23f", "cheese", None),
    "E": ("#ffffff", "eye", "eyes"),
    "P": ("#101018", "pupil", "eyes"),
    "T": ("#8e44ad", "tentacle", "tentacle"),
    "S": ("#37c837", "slime", "slime"),
    "W": ("#f4f4f4", "tooth", "teeth"),
    "X": ("#ff2bd6", "glitch", "glitch"),
}

WIDTH = 11


def _blank():
    """An empty sandwich: two buns and a 3-row filling band of base food."""
    rows = [
        list("..BBBBBBB.."),
        list(".BBBBBBBBB."),
        list("bbbbbbbbbbb"),
        list("LLLLLLLLLLL"),  # filling row 3
        list("MMMMMMMMMMM"),  # filling row 4
        list("LLLLLLLLLLL"),  # filling row 5
        list("bbbbbbbbbbb"),
        list(".BBBBBBBBB."),
        list("..BBBBBBB.."),
    ]
    return rows


def paint_sandwich(seed: int):
    """Deterministically paint one cursed sandwich, returning its pixel grid."""
    rng = random.Random(seed * 2654435761 & 0xFFFFFFFF)
    g = _blank()
    fill = (3, 4, 5)  # the filling rows we are allowed to curse

    # every sandwich gets a random helping of cheese drip first
    for c in range(1, WIDTH - 1):
        if rng.random() < 0.35:
            g[4][c] = "C"

    # pick 1-2 curses to embed; the classifier will have to figure them out
    curses = rng.sample(["eyes", "tentacle", "slime", "teeth", "glitch"],
                         k=rng.randint(1, 2))

    if "eyes" in curses:
        for _ in range(rng.randint(1, 3)):
            c = rng.randint(2, WIDTH - 3)
            r = rng.choice(fill)
            g[r][c] = "E"
            g[r][min(c + 1, WIDTH - 1)] = "P"

    if "tentacle" in curses:
        for c in range(1, WIDTH - 1):
            if rng.random() < 0.45:
                g[5][c] = "T"
                g[6][c] = "T" if rng.random() < 0.6 else g[6][c]  # dangle through crust
        g[7][rng.randint(2, WIDTH - 3)] = "T"

    if "slime" in curses:
        for r in fill:
            for c in range(WIDTH):
                if rng.random() < 0.4:
                    g[r][c] = "S"
        g[6][rng.randint(1, WIDTH - 2)] = "S"  # a drip

    if "teeth" in curses:
        r = rng.choice(fill)
        for c in range(1, WIDTH - 1, 2):
            g[r][c] = "W"

    if "glitch" in curses:
        for _ in range(rng.randint(4, 9)):
            g[rng.randint(0, 8)][rng.randint(0, WIDTH - 1)] = "X"

    return {"id": seed, "grid": ["".join(row) for row in g], "curses": curses}


@env.task
async def make_sandwich(seed: int) -> dict:
    s = paint_sandwich(seed)
    print(f"[gen] painted sandwich #{seed:02d} with curses {s['curses']}")
    return s


# classifier: looks ONLY at the pixels, never at the 'curses' hint.
# priority order decides the final label when several signals are present.
TYPES = [
    ("eyes", "Sentient", "👁", "It is watching you eat it."),
    ("tentacle", "Eldritch", "🐙", "Non-Euclidean filling. Do not unwrap."),
    ("slime", "Toxic", "☣", "Actively fermenting. Possibly sentient mold."),
    ("teeth", "Carnivorous", "🦷", "It bites back. BYO gauntlet."),
    ("glitch", "Glitched", "🌀", "Rendered in a dimension that hates you."),
]


@env.task
async def classify(s: dict) -> dict:
    chars = "".join(s["grid"])
    counts = {feat: 0 for feat in ("eyes", "tentacle", "slime", "teeth", "glitch")}
    for ch in chars:
        feat = PALETTE.get(ch, (None, None, None))[2]
        if feat in counts:
            counts[feat] += 1

    label, emoji, flavor = "Merely Stale", "🥪", "Cursed only by neglect."
    feat_hit = None
    for feat, name, em, fl in TYPES:
        if counts[feat] > 0:
            label, emoji, flavor, feat_hit = name, em, fl, feat
            break

    total = sum(counts.values())
    confidence = 0.5 if feat_hit is None else min(0.99, 0.6 + counts[feat_hit] / max(total, 1) * 0.4)
    print(f"[clf] sandwich #{s['id']:02d} -> {label} {emoji} "
          f"(conf {confidence:.0%}, signals {counts})")
    return {**s, "type": label, "emoji": emoji, "flavor": flavor,
            "confidence": round(confidence, 2)}


def render_svg(grid, scale=14):
    """Turn a pixel grid into a self-contained SVG."""
    h = len(grid)
    w = len(grid[0])
    rects = []
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            color = PALETTE.get(ch, (".",))[0]
            if color == "transparent":
                continue
            rects.append(
                f'<rect x="{c*scale}" y="{r*scale}" width="{scale}" height="{scale}" '
                f'fill="{color}"/>'
            )
    return (f'<svg width="{w*scale}" height="{h*scale}" '
            f'viewBox="0 0 {w*scale} {h*scale}" shape-rendering="crispEdges" '
            f'style="image-rendering:pixelated;background:#1a1a22;border-radius:6px">'
            + "".join(rects) + "</svg>")


def render_gallery_html(classified):
    """Build the full gallery HTML, grouped by curse-type."""
    buckets = {}
    for s in classified:
        buckets.setdefault((s["type"], s["emoji"], s["flavor"]), []).append(s)
    order = sorted(buckets.items(), key=lambda kv: -len(kv[1]))

    sections = []
    for (label, emoji, flavor), items in order:
        cards = []
        for s in sorted(items, key=lambda x: -x["confidence"]):
            cards.append(
                f'<figure style="margin:0;text-align:center">{render_svg(s["grid"])}'
                f'<figcaption style="color:#8a8aa0;font-size:11px;margin-top:4px">'
                f'#{s["id"]:02d} · {s["confidence"]:.0%}</figcaption></figure>'
            )
        sections.append(f"""
        <section style="margin:0 0 34px">
          <h2 style="margin:0 0 2px;font-size:22px">{emoji} {label}
            <span style="color:#6cf;font-size:15px">×{len(items)}</span></h2>
          <p style="margin:0 0 12px;color:#9a9ab0;font-style:italic">{flavor}</p>
          <div style="display:flex;flex-wrap:wrap;gap:14px">{''.join(cards)}</div>
        </section>""")

    chips = "".join(
        f'<span style="background:#26263a;border-radius:14px;padding:4px 12px;'
        f'margin:0 6px 6px 0;display:inline-block">{emoji} {label} '
        f'<b style="color:#6cf">{len(items)}</b></span>'
        for (label, emoji, flavor), items in order
    )

    html = f"""
    <div style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;
                background:#101018;color:#eee;padding:26px;min-height:100vh">
      <h1 style="margin:0 0 4px;font-size:30px">🥪 A Field of Cursed Sandwiches</h1>
      <p style="margin:0 0 16px;color:#9a9ab0">
        {len(classified)} specimens, each painted then sorted by a blind pixel classifier.</p>
      <div style="margin-bottom:24px">{chips}</div>
      {''.join(sections)}
    </div>"""

    return html


@env.task(report=True)
async def main(n: int = 24) -> str:
    print(f"[main] conjuring a field of {n} cursed sandwiches...")
    sandwiches = await asyncio.gather(*[make_sandwich(i) for i in range(n)])
    classified = await asyncio.gather(*[classify(s) for s in sandwiches])

    # paint the gallery straight into the default ("main") report tab,
    # so the run opens on the gallery — no extra tab to click through
    await flyte.report.replace.aio(render_gallery_html(classified))
    await flyte.report.flush.aio()

    tally = {}
    for s in classified:
        tally[s["type"]] = tally.get(s["type"], 0) + 1
    print(f"[main] report flushed. tally: {tally}")
    return f"{n} cursed sandwiches sorted into {len(tally)} types"
