"""
TIRENA icon library — generic, parametric icons reused across the full-automation
pipeline. Each function draws one icon centered at (cx, cy). The picker below
selects one based on keywords in the article's title/category/context.
"""
import math

CREAM = (250, 247, 241)
CHARCOAL = (42, 40, 36)
SAGE_DEEP = (58, 71, 51)
SAGE_MUTED = (150, 165, 138)
CLAY = (188, 110, 78)
BRASS = (196, 164, 96)


def icon_dropper_bottle(draw, cx, cy, **kw):
    draw.rounded_rectangle([cx - 30, cy - 20, cx + 30, cy + 100], radius=10, fill=CREAM)
    draw.rectangle([cx - 10, cy - 55, cx + 10, cy - 20], fill=BRASS)
    draw.polygon([(cx - 10, cy - 55), (cx + 10, cy - 55), (cx, cy - 78)], fill=BRASS)
    draw.rectangle([cx - 30, cy + 15, cx + 30, cy + 30], fill=CLAY)


def icon_jar(draw, cx, cy, **kw):
    draw.rounded_rectangle([cx - 45, cy - 10, cx + 45, cy + 100], radius=16, fill=CREAM)
    draw.ellipse([cx - 45, cy - 26, cx + 45, cy - 4], fill=BRASS)
    for r in [24, 15]:
        draw.arc([cx - r, cy + 30 - r, cx + r, cy + 30 + r], start=20, end=300, fill=SAGE_DEEP, width=4)


def icon_pump_bottle(draw, cx, cy, **kw):
    draw.rounded_rectangle([cx - 45, cy - 20, cx + 45, cy + 100], radius=14, fill=CREAM)
    draw.rectangle([cx - 14, cy - 55, cx + 14, cy - 20], fill=BRASS)
    draw.rounded_rectangle([cx - 8, cy - 75, cx + 8, cy - 55], radius=4, fill=BRASS)
    draw.line([(cx + 8, cy - 68), (cx + 34, cy - 82)], fill=BRASS, width=6)
    draw.rectangle([cx - 45, cy + 10, cx + 45, cy + 24], fill=CLAY)


def icon_tube(draw, cx, cy, **kw):
    draw.rounded_rectangle([cx - 30, cy - 20, cx + 30, cy + 100], radius=14, fill=CREAM)
    draw.polygon([(cx - 30, cy - 20), (cx + 30, cy - 20), (cx + 16, cy - 45), (cx - 16, cy - 45)], fill=CREAM)
    draw.rectangle([cx - 30, cy + 15, cx + 30, cy + 32], fill=CLAY)


def icon_sun_moon_pair(draw, cx, cy, **kw):
    for dx, is_sun in [(-55, True), (55, False)]:
        x = cx + dx
        draw.rounded_rectangle([x - 26, cy - 10, x + 26, cy + 100], radius=10, fill=CREAM)
        draw.rectangle([x - 9, cy - 35, x + 9, cy - 10], fill=BRASS)
        if is_sun:
            sx, sy, r = x, cy - 65, 18
            draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=BRASS)
            for i in range(8):
                a = math.radians(i * 45)
                draw.line([(sx + (r + 6) * math.cos(a), sy + (r + 6) * math.sin(a)),
                           (sx + (r + 14) * math.cos(a), sy + (r + 14) * math.sin(a))], fill=BRASS, width=3)
        else:
            mx, my, r = x, cy - 65, 18
            draw.ellipse([mx - r, my - r, mx + r, my + r], fill=CREAM)
            draw.ellipse([mx - r + 10, my - r - 3, mx + r + 10, my + r - 3], fill=SAGE_DEEP)


def icon_molecule_chain(draw, cx, cy, **kw):
    draw.arc([cx - 100, cy - 40, cx + 100, cy + 160], start=195, end=345, fill=CREAM, width=8)
    nodes = [(cx - 70, cy - 90), (cx - 25, cy - 120), (cx + 25, cy - 95), (cx + 70, cy - 125)]
    for i in range(len(nodes) - 1):
        draw.line([nodes[i], nodes[i + 1]], fill=BRASS, width=4)
    for i, (nx, ny) in enumerate(nodes):
        r = 13 if i % 2 == 0 else 10
        draw.ellipse([nx - r, ny - r, nx + r, ny + r], fill=CLAY if i == 1 else CREAM)


def icon_comparison_vs(draw, cx, cy, **kw):
    for side, dx in [(-1, -55), (1, 55)]:
        x = cx + dx
        draw.rounded_rectangle([x - 26, cy - 60, x + 26, cy + 80], radius=10, fill=CREAM)
        draw.rectangle([x - 10, cy - 80, x + 10, cy - 60], fill=BRASS)
        color = CLAY if side == -1 else BRASS
        draw.rectangle([x - 20, cy + 20, x + 20, cy + 34], fill=color)
    from PIL import ImageFont
    vs_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 30)
    bbox = draw.textbbox((0, 0), "VS", font=vs_font)
    draw.text((cx - (bbox[2] - bbox[0]) / 2, cy - (bbox[3] - bbox[1]) / 2 - 5), "VS", font=vs_font, fill=CREAM)


def icon_magnifying_label(draw, cx, cy, **kw):
    bw, bh = 130, 160
    draw.rounded_rectangle([cx - bw / 2 - 20, cy - bh / 2, cx + bw / 2 - 20, cy + bh / 2], radius=10, fill=CREAM)
    for i in range(5):
        ly = cy - bh / 2 + 30 + i * 24
        w = 70 if i != 1 else 45
        draw.line([(cx - bw / 2 - 5, ly), (cx - bw / 2 - 5 + w, ly)], fill=SAGE_DEEP, width=6)
    gx, gy, gr = cx + 55, cy + 55, 45
    draw.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], outline=BRASS, width=8)
    draw.line([(gx + gr * 0.7, gy + gr * 0.7), (gx + gr * 1.5, gy + gr * 1.5)], fill=BRASS, width=10)


def icon_chain_link(draw, cx, cy, **kw):
    for i, dx in enumerate([-90, -30, 30, 90]):
        x = cx + dx
        gap = 12 if i == 2 else 0
        draw.rounded_rectangle([x - 22 + gap, cy - 16, x + 22 - gap, cy + 16], radius=16, outline=CREAM, width=7)
    draw.line([(cx + 30 - 4, cy - 22), (cx + 30 + 4, cy - 8)], fill=CLAY, width=5)
    draw.line([(cx + 30 - 4, cy - 8), (cx + 30 + 4, cy - 22)], fill=CLAY, width=5)


def icon_ladder_steps(draw, cx, cy, **kw):
    for dx, dy, color in [(-70, 50, CREAM), (0, 10, BRASS), (70, -35, CLAY)]:
        x, y = cx + dx, cy + dy
        draw.rounded_rectangle([x - 30, y, x + 30, cy + 90], radius=8, fill=color)
    nodes = [(cx - 70, cy - 20), (cx, cy - 60), (cx + 70, cy - 100)]
    for i in range(len(nodes) - 1):
        draw.line([nodes[i], nodes[i + 1]], fill=CREAM, width=3)
    for nx, ny in nodes:
        draw.ellipse([nx - 9, ny - 9, nx + 9, ny + 9], fill=CREAM)


def icon_droplets_arc(draw, cx, cy, **kw):
    draw.arc([cx - 100, cy - 90, cx + 100, cy + 110], start=195, end=345, fill=CREAM, width=8)

    def teardrop(x, y, size, color):
        draw.ellipse([x - size, y, x + size, y + size * 2], fill=color)
        draw.polygon([(x - size * 0.9, y + size * 0.3), (x, y - size * 0.9), (x + size * 0.9, y + size * 0.3)], fill=color)

    teardrop(cx - 35, cy - 90, 11, BRASS)
    teardrop(cx + 5, cy - 105, 13, CLAY)
    teardrop(cx + 42, cy - 88, 11, BRASS)


def icon_bottle_sprig(draw, cx, cy, **kw):
    """Generic fallback: a bottle with a botanical sprig accent."""
    draw.rounded_rectangle([cx - 30, cy - 20, cx + 30, cy + 100], radius=10, fill=CREAM)
    draw.rectangle([cx - 10, cy - 45, cx + 10, cy - 20], fill=BRASS)
    draw.rectangle([cx - 30, cy + 15, cx + 30, cy + 30], fill=CLAY)
    # small sprig beside it
    sx, sy = cx + 55, cy - 30
    draw.line([(sx, sy), (sx, sy - 50)], fill=SAGE_MUTED, width=4)
    for t, side in [(0.4, 1), (0.7, -1), (1.0, 1)]:
        lx, ly = sx, sy - 50 * t
        draw.polygon([(lx, ly), (lx + side * 20, ly - 15), (lx, ly - 25)], fill=SAGE_MUTED)


# Keyword -> icon function. Checked in order; first match wins.
ICON_KEYWORD_MAP = [
    (["compar", " vs ", "versus"], icon_comparison_vs),
    (["ingredient label", "read a", "label"], icon_magnifying_label),
    (["bond", "repair treatment", "broken"], icon_chain_link),
    (["retinol", "retinaldehyde", "tretinoin", "explained"], icon_ladder_steps),
    (["am/pm", "morning", "night routine", "am and pm"], icon_sun_moon_pair),
    (["peptide", "molecule", "signal"], icon_molecule_chain),
    (["scalp", "dandruff", "oily scalp"], icon_droplets_arc),
    (["mask", "hair mask"], icon_jar),
    (["cleanser", "face wash", "wash"], icon_pump_bottle),
    (["lip", "balm"], icon_tube),
    (["sunscreen", "spf"], icon_dropper_bottle),
]


def pick_icon(title, category, context):
    text = f"{title} {category} {context}".lower()
    for keywords, fn in ICON_KEYWORD_MAP:
        if any(k in text for k in keywords):
            return fn
    return icon_bottle_sprig
