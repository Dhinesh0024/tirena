"""
TIRENA auto-pin pipeline.
Runs inside GitHub Actions whenever new article files are pushed.

What it does, in order:
1. Finds which article Markdown files changed in this push
2. Reads each one's frontmatter (title, description, category, draft)
3. Skips drafts
4. Generates an on-brand pin image (same design system as the manual pins)
5. Saves it into public/pins/<slug>.png and commits it back to the repo
6. Waits for Cloudflare to redeploy so the image is live at a public URL
7. Refreshes the Pinterest access token
8. Publishes the pin to the correct board via the Pinterest API
"""

import base64
import math
import os
import subprocess
import sys
import time

import requests
import yaml
from PIL import Image, ImageDraw, ImageFont, ImageFilter

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES_DIR = os.path.join(REPO_ROOT, "src", "content", "articles")
PINS_DIR = os.path.join(REPO_ROOT, "public", "pins")
FONTS_DIR = os.path.join(REPO_ROOT, "fonts")

SITE_URL = os.environ.get("SITE_URL", "https://tirena.tirena-evolve.workers.dev")

# ---------- Pinterest board routing ----------
# Add more categories here as you create more boards.
BOARD_ENV_MAP = {
    "hair-care": "PINTEREST_BOARD_ID_HAIR",
    "skin-care": "PINTEREST_BOARD_ID_SKIN",
    "body-care": "PINTEREST_BOARD_ID_BODY",
    "reviews": "PINTEREST_BOARD_ID_REVIEWS",
    "comparisons": "PINTEREST_BOARD_ID_COMPARISONS",
}

CATEGORY_HASHTAGS = {
    "hair-care": "#haircare #hairtips",
    "skin-care": "#skincare #skincaretips",
    "body-care": "#bodycare #selfcare",
    "reviews": "#productreview",
    "comparisons": "#beautycompare",
}

# ---------- Pin design (same system as the manual pins) ----------
W, H = 1000, 1500
SAGE_DEEP = (63, 77, 55)
SAGE_MID = (89, 106, 76)
SAGE_LIGHT = (150, 168, 132)
CREAM = (248, 245, 239)
CLAY = (163, 104, 79)
CLAY_LIGHT = (196, 146, 118)

SERIF_BOLD = os.path.join(FONTS_DIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONTS_DIR, "DejaVuSans.ttf")
SANS_BOLD = os.path.join(FONTS_DIR, "DejaVuSans-Bold.ttf")


def vertical_gradient(w, h, top_color, bottom_color):
    base = Image.new("RGB", (w, h), top_color)
    top = Image.new("RGB", (w, h), bottom_color)
    mask = Image.new("L", (w, h))
    mask.putdata([int(255 * (y / h)) for y in range(h) for _ in range(w)])
    base.paste(top, (0, 0), mask)
    return base


def draw_leaf(draw, cx, cy, length, width, angle_deg, color):
    angle = math.radians(angle_deg)
    tip = (cx + length * math.cos(angle), cy + length * math.sin(angle))
    perp = angle + math.pi / 2
    mid = (cx + (length * 0.5) * math.cos(angle), cy + (length * 0.5) * math.sin(angle))
    w1 = (mid[0] + (width / 2) * math.cos(perp), mid[1] + (width / 2) * math.sin(perp))
    w2 = (mid[0] - (width / 2) * math.cos(perp), mid[1] - (width / 2) * math.sin(perp))
    draw.polygon([(cx, cy), w1, tip, w2], fill=color)
    draw.line([(cx, cy), tip], fill=SAGE_DEEP, width=2)


def draw_sprig(draw, cx, cy, scale=1.0, base_angle=-90, color=SAGE_LIGHT):
    stem_len = 130 * scale
    angle = math.radians(base_angle)
    end = (cx + stem_len * math.cos(angle), cy + stem_len * math.sin(angle))
    draw.line([(cx, cy), end], fill=color, width=int(4 * scale))
    for t, side in zip([0.35, 0.55, 0.75, 0.95], [1, -1, 1, -1]):
        lx = cx + stem_len * t * math.cos(angle)
        ly = cy + stem_len * t * math.sin(angle)
        draw_leaf(draw, lx, ly, 55 * scale, 26 * scale, base_angle + side * 45, color)


def dot_texture(img, color, spacing=54, radius=1, opacity=18):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(0, img.size[1], spacing):
        for x in range(0, img.size[0], spacing):
            od.ellipse([x - radius, y - radius, x + radius, y + radius], fill=color + (opacity,))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def wrap_text(draw, text, font, max_width):
    words, lines, current = text.split(), [], ""
    for word in words:
        test = (current + " " + word).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def make_pin(category_label, headline, bullets, out_path):
    img = vertical_gradient(W, H, SAGE_MID, SAGE_DEEP)

    circle_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(circle_layer).ellipse([-260, 300, 640, 1200], fill=(255, 255, 255, 14))
    circle_layer = circle_layer.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img.convert("RGBA"), circle_layer).convert("RGB")
    img = dot_texture(img, CREAM)
    draw = ImageDraw.Draw(img)

    margin = 70
    draw_sprig(draw, W - 150, 60, 1.0, 115, SAGE_LIGHT)
    draw_sprig(draw, W - 60, 40, 0.7, 140, CLAY_LIGHT)

    logo_font = ImageFont.truetype(SERIF_BOLD, 46)
    draw.text((margin, 78), "TIRENA", font=logo_font, fill=CREAM)
    draw.line([(margin, 138), (margin + 130, 138)], fill=CLAY, width=3)

    cat_font = ImageFont.truetype(SANS_BOLD, 28)
    cat_text = category_label.upper()
    bbox = draw.textbbox((0, 0), cat_text, font=cat_font)
    pill_w = (bbox[2] - bbox[0]) + 64
    pill_y = 175
    draw.rounded_rectangle([margin, pill_y, margin + pill_w, pill_y + 58], radius=29, fill=CLAY)
    draw.ellipse([margin + 20, pill_y + 22, margin + 34, pill_y + 36], fill=CREAM)
    draw.text((margin + 46, pill_y + 14), cat_text, font=cat_font, fill=CREAM)

    headline_size = 80
    headline_font = ImageFont.truetype(SERIF_BOLD, headline_size)
    max_w = W - margin * 2 - 20
    lines = wrap_text(draw, headline, headline_font, max_w)
    while len(lines) > 4 and headline_size > 56:
        headline_size -= 4
        headline_font = ImageFont.truetype(SERIF_BOLD, headline_size)
        lines = wrap_text(draw, headline, headline_font, max_w)

    line_h = int(headline_size * 1.2)
    y = 420
    for line in lines:
        draw.text((margin, y), line, font=headline_font, fill=CREAM)
        y += line_h

    rule_y = y + 36
    draw.rectangle([margin, rule_y, margin + 100, rule_y + 6], fill=CLAY)

    bullet_font = ImageFont.truetype(SANS, 33)
    by = rule_y + 54
    for b in bullets:
        b_lines = wrap_text(draw, b, bullet_font, max_w - 55)
        draw_leaf(draw, margin + 8, by + 16, 20, 11, -20, CLAY_LIGHT)
        for i, bl in enumerate(b_lines):
            draw.text((margin + 40, by + i * 44), bl, font=bullet_font, fill=CREAM)
        by += 44 * len(b_lines) + 24

    card_y = H - 210
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(overlay).rounded_rectangle(
        [margin - 20, card_y, W - margin + 20, H - 90], radius=18, fill=CREAM + (255,)
    )
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.text((margin + 10, card_y + 22), "Read the full guide \u2192",
              font=ImageFont.truetype(SANS_BOLD, 32), fill=SAGE_DEEP)
    draw.text((margin + 10, card_y + 66), SITE_URL.replace("https://", ""),
              font=ImageFont.truetype(SANS, 24), fill=(120, 120, 110))

    img.save(out_path, "PNG")
    print(f"Generated pin: {out_path}")


# ---------- Article parsing ----------
def get_changed_article_files():
    before = os.environ.get("BEFORE_SHA", "")
    after = os.environ.get("AFTER_SHA", "HEAD")
    if not before or before == "0000000000000000000000000000000000000000":
        # First commit on the branch, or force-push: just process nothing automatically,
        # safer than accidentally re-posting every article that already exists.
        return []
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=AM", before, after],
        cwd=REPO_ROOT, capture_output=True, text=True, check=True
    )
    files = result.stdout.strip().split("\n") if result.stdout.strip() else []
    return [f for f in files if f.startswith("src/content/articles/") and f.endswith(".md")]


def parse_frontmatter(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    return yaml.safe_load(parts[1])


def bullets_for(description):
    # Simple heuristic: split the description into short phrases for pin bullets.
    # Keeps it generic since we don't want to re-parse the whole article body.
    words = description.rstrip(".").split(" — ")
    return [w.strip() for w in words][:3] if len(words) > 1 else [description[:60]]


# ---------- Pinterest API ----------
def refresh_pinterest_token():
    client_id = os.environ["PINTEREST_CLIENT_ID"]
    client_secret = os.environ["PINTEREST_CLIENT_SECRET"]
    refresh_token = os.environ["PINTEREST_REFRESH_TOKEN"]
    basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    resp = requests.post(
        "https://api.pinterest.com/v5/oauth/token",
        headers={"Authorization": f"Basic {basic}", "Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "refresh_token", "refresh_token": refresh_token},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def publish_pin(access_token, board_id, image_url, link, title, description):
    resp = requests.post(
        "https://api.pinterest.com/v5/pins",
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        json={
            "board_id": board_id,
            "link": link,
            "title": title[:100],
            "description": description[:500],
            "media_source": {"source_type": "image_url", "url": image_url},
        },
        timeout=30,
    )
    if not resp.ok:
        print(f"Pinterest API error: {resp.status_code} {resp.text}", file=sys.stderr)
    resp.raise_for_status()
    return resp.json()


def git_commit_and_push(paths, message):
    subprocess.run(["git", "config", "user.name", "tirena-auto-pin-bot"], cwd=REPO_ROOT, check=True)
    subprocess.run(["git", "config", "user.email", "actions@users.noreply.github.com"], cwd=REPO_ROOT, check=True)
    subprocess.run(["git", "add", *paths], cwd=REPO_ROOT, check=True)
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=REPO_ROOT)
    if result.returncode == 0:
        print("Nothing new to commit.")
        return
    subprocess.run(["git", "commit", "-m", message], cwd=REPO_ROOT, check=True)
    subprocess.run(["git", "push"], cwd=REPO_ROOT, check=True)


def main():
    os.makedirs(PINS_DIR, exist_ok=True)
    changed = get_changed_article_files()
    if not changed:
        print("No new/changed articles in this push. Nothing to do.")
        return

    new_pin_paths = []
    pin_jobs = []

    for rel_path in changed:
        abs_path = os.path.join(REPO_ROOT, rel_path)
        if not os.path.exists(abs_path):
            continue
        fm = parse_frontmatter(abs_path)
        if not fm or fm.get("draft"):
            print(f"Skipping draft or unreadable file: {rel_path}")
            continue

        slug = os.path.splitext(os.path.basename(rel_path))[0]
        category = fm.get("category", "hair-care")
        title = fm.get("title", "New from TIRENA")
        description = fm.get("description", "")
        category_label = category.replace("-", " ").title()

        pin_path = os.path.join(PINS_DIR, f"{slug}.png")
        make_pin(category_label, title, bullets_for(description), pin_path)
        new_pin_paths.append(os.path.relpath(pin_path, REPO_ROOT))

        pin_jobs.append({
            "slug": slug,
            "category": category,
            "title": title,
            "description": f"{description} {CATEGORY_HASHTAGS.get(category, '')}".strip(),
            "image_url": f"{SITE_URL}/pins/{slug}.png",
            "link": f"{SITE_URL}/articles/{slug}/",
        })

    if not pin_jobs:
        print("No publishable articles found in this push.")
        return

    git_commit_and_push(new_pin_paths, "Auto-generate pin(s) for new article(s)")

    wait_seconds = int(os.environ.get("DEPLOY_WAIT_SECONDS", "100"))
    print(f"Waiting {wait_seconds}s for Cloudflare to deploy the new pin image(s)...")
    time.sleep(wait_seconds)

    access_token = refresh_pinterest_token()

    for job in pin_jobs:
        board_env_name = BOARD_ENV_MAP.get(job["category"])
        board_id = os.environ.get(board_env_name) if board_env_name else None
        if not board_id:
            print(f"No board configured for category '{job['category']}', skipping Pinterest post for {job['slug']}.")
            continue
        result = publish_pin(
            access_token, board_id, job["image_url"], job["link"], job["title"], job["description"]
        )
        print(f"Published to Pinterest: {job['slug']} -> pin id {result.get('id')}")


if __name__ == "__main__":
    main()
