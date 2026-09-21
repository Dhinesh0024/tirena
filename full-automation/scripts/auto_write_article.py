"""
TIRENA full article automation.

Input (what you provide): a small YAML file in queue/, e.g. queue/new-article.yaml:

    title_hint: "Best Ceramide Moisturizers for Barrier Repair"
    category: skin-care
    context: |
      Article should cover what ceramides do and why barrier repair matters.
    products:
      - name: "CeraVe Moisturising Cream"
        info: "Ceramides 1, 3, 6-II, hyaluronic acid, MVE technology, fragrance-free"
        link: "https://link.amazon/XXXXXXX"
      - name: "Some Other Product"
        info: "..."
        link: "https://link.amazon/YYYYYYY"

Output: a full article committed to src/content/articles/, plus a cover image
and pin image, plus a text file with ready-to-paste Pinterest title/description
(since actually posting to Pinterest is still manual, pending API approval).
"""
import glob
import json
import os
import subprocess
import sys
import urllib.request

import yaml
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from icon_library import pick_icon, CREAM, CHARCOAL, SAGE_DEEP, SAGE_MUTED, CLAY, BRASS

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE_DIR = os.path.join(REPO_ROOT, "queue")
ARTICLES_DIR = os.path.join(REPO_ROOT, "src", "content", "articles")
PUBLIC_DIR = os.path.join(REPO_ROOT, "public")
PINS_OUT_DIR = os.path.join(REPO_ROOT, "pins_output")

FONTS_DIR = os.path.join(REPO_ROOT, "fonts")
SERIF_BOLD = os.path.join(FONTS_DIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONTS_DIR, "DejaVuSans.ttf")
SANS_BOLD = os.path.join(FONTS_DIR, "DejaVuSans-Bold.ttf")

SITE_URL = "https://tirena.tirena-evolve.workers.dev"

GITHUB_MODELS_URL = "https://models.github.ai/inference/chat/completions"
GITHUB_MODEL_NAME = "openai/gpt-4.1"

SYSTEM_PROMPT = """You are the writer for TIRENA, an evidence-aware personal care \
website covering hair, skin, and body care. Your voice: clear, honest, never hypey, \
always separates what's genuinely evidence-backed from marketing claims. You never \
invent statistics or studies you're not given. You write in the same structure every time:

1. A short intro paragraph framing the real problem/question (2-4 sentences)
2. 2-4 H2 sections (## Heading) explaining the relevant mechanism/science plainly
3. An honest caveat section if relevant (what the evidence does NOT support)
4. A closing section titled "## A place to start" (or similar) that naturally \
introduces the given product(s), each as a bolded product name, briefly explaining \
why it fits, using ONLY the product info given to you - never invent ingredients \
or claims not provided.
5. Directly before the product section, include this exact line on its own: \
"*This section contains affiliate links — if you buy through them, TIRENA may earn \
a small commission at no extra cost to you.*"

Return ONLY valid JSON with these exact keys: title, description (one sentence, \
under 160 characters), category (one of: hair-care, skin-care, body-care, reviews, \
comparisons), body (the full markdown body as described above, using [Product Name](LINK) \
markdown links for each product using the exact links given to you), pin_bullets \
(an array of exactly 3 short punchy phrases, each under 8 words, for a Pinterest \
pin graphic), pin_title (under 100 characters), pin_description (under 400 characters, \
include 2-3 relevant hashtags).

No text outside the JSON object."""


def call_github_models(user_content):
    token = os.environ["GH_MODELS_TOKEN"]
    payload = json.dumps({
        "model": GITHUB_MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.6,
    }).encode()

    req = urllib.request.Request(
        GITHUB_MODELS_URL, data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        result = json.loads(resp.read())
    content = result["choices"][0]["message"]["content"]
    # Strip markdown code fences if the model wrapped the JSON in them
    content = content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    return json.loads(content)


def slugify(title):
    import re
    s = title.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s.strip())
    return s[:80].strip("-")


# ---------------- Image rendering (reusing the established brand system) ----------------
def wrap_text(draw, text, font, max_width):
    words, lines, current = text.split(), [], ""
    for word in words:
        test = (current + " " + word).strip()
        if draw.textbbox((0, 0), test, font=font)[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def render_cover_image(title, category, icon_fn, out_path):
    W, H = 1200, 630
    SPLIT_X = 760
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    draw.rectangle([SPLIT_X, 0, W, H], fill=SAGE_DEEP)
    draw.line([(SPLIT_X, 0), (SPLIT_X, H)], fill=BRASS, width=3)
    margin = 60

    r = 26
    draw.ellipse([margin + 24 - r, 56 - r, margin + 24 + r, 56 + r], outline=CHARCOAL, width=2)
    tf = ImageFont.truetype(SERIF_BOLD, 28)
    bbox = draw.textbbox((0, 0), "T", font=tf)
    draw.text((margin + 24 - (bbox[2] - bbox[0]) / 2 - bbox[0], 56 - (bbox[3] - bbox[1]) / 2 - bbox[1] - 1),
              "T", font=tf, fill=CHARCOAL)
    draw.text((margin + 58, 44), "TIRENA", font=ImageFont.truetype(SANS_BOLD, 22), fill=CHARCOAL)

    draw.text((margin, 108), category.upper(), font=ImageFont.truetype(SANS_BOLD, 20), fill=SAGE_MUTED)
    draw.line([(margin, 136), (margin + 40, 136)], fill=CLAY, width=2)

    max_w = SPLIT_X - margin - 40
    size = 54
    font = ImageFont.truetype(SERIF_BOLD, size)
    lines = wrap_text(draw, title, font, max_w)
    while len(lines) > 3 and size > 38:
        size -= 3
        font = ImageFont.truetype(SERIF_BOLD, size)
        lines = wrap_text(draw, title, font, max_w)
    line_h = int(size * 1.18)
    y = 170 + (300 - line_h * len(lines)) / 2
    for line in lines:
        draw.text((margin, y), line, font=font, fill=CHARCOAL)
        y += line_h

    draw.text((margin, H - 56), SITE_URL.replace("https://", ""), font=ImageFont.truetype(SANS, 20), fill=SAGE_MUTED)

    icon_fn(draw, SPLIT_X + (W - SPLIT_X) / 2, H / 2)
    img.save(out_path, "PNG")


def render_pin_image(title, category, bullets, icon_fn, out_path):
    W, H = 1000, 1500
    SAGE_MID = (89, 106, 76)
    CLAY_LIGHT = (196, 146, 118)

    base = Image.new("RGB", (W, H), SAGE_MID)
    top = Image.new("RGB", (W, H), SAGE_DEEP)
    mask = Image.new("L", (W, H))
    mask.putdata([int(255 * (y / H)) for y in range(H) for _ in range(W)])
    base.paste(top, (0, 0), mask)
    img = base

    circle_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(circle_layer).ellipse([-260, 300, 640, 1200], fill=(255, 255, 255, 14))
    circle_layer = circle_layer.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img.convert("RGBA"), circle_layer).convert("RGB")
    draw = ImageDraw.Draw(img)

    margin = 70
    logo_font = ImageFont.truetype(SERIF_BOLD, 46)
    draw.text((margin, 78), "TIRENA", font=logo_font, fill=CREAM)
    draw.line([(margin, 138), (margin + 130, 138)], fill=CLAY, width=3)

    cat_font = ImageFont.truetype(SANS_BOLD, 28)
    cat_text = category.upper()
    bbox = draw.textbbox((0, 0), cat_text, font=cat_font)
    pill_w = (bbox[2] - bbox[0]) + 64
    draw.rounded_rectangle([margin, 175, margin + pill_w, 175 + 58], radius=29, fill=CLAY)
    draw.ellipse([margin + 20, 197, margin + 34, 211], fill=CREAM)
    draw.text((margin + 46, 189), cat_text, font=cat_font, fill=CREAM)

    max_w = W - margin * 2 - 20
    size = 76
    font = ImageFont.truetype(SERIF_BOLD, size)
    lines = wrap_text(draw, title, font, max_w)
    while len(lines) > 3 and size > 54:
        size -= 4
        font = ImageFont.truetype(SERIF_BOLD, size)
        lines = wrap_text(draw, title, font, max_w)
    line_h = int(size * 1.18)
    y = 410
    for line in lines:
        draw.text((margin, y), line, font=font, fill=CREAM)
        y += line_h

    rule_y = y + 30
    draw.rectangle([margin, rule_y, margin + 100, rule_y + 6], fill=CLAY)

    bullet_font = ImageFont.truetype(SANS, 32)
    by = rule_y + 46
    for b in bullets:
        b_lines = wrap_text(draw, b, bullet_font, max_w - 55)
        draw.ellipse([margin + 2, by + 10, margin + 16, by + 24], fill=CLAY_LIGHT)
        for i, bl in enumerate(b_lines):
            draw.text((margin + 40, by + i * 42), bl, font=bullet_font, fill=CREAM)
        by += 42 * len(b_lines) + 20

    icy = min(by + 150, H - 340)
    icon_fn(draw, W / 2, icy)

    card_y = H - 210
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(overlay).rounded_rectangle([margin - 20, card_y, W - margin + 20, H - 90], radius=18, fill=CREAM + (255,))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.text((margin + 10, card_y + 22), "Read the full guide \u2192", font=ImageFont.truetype(SANS_BOLD, 32), fill=SAGE_DEEP)
    draw.text((margin + 10, card_y + 66), SITE_URL.replace("https://", ""), font=ImageFont.truetype(SANS, 24), fill=(120, 120, 110))

    img.save(out_path, "PNG")


# ---------------- Git commit ----------------
def git_commit_and_push(paths, message):
    subprocess.run(["git", "config", "user.name", "tirena-auto-article-bot"], cwd=REPO_ROOT, check=True)
    subprocess.run(["git", "config", "user.email", "actions@users.noreply.github.com"], cwd=REPO_ROOT, check=True)
    subprocess.run(["git", "add", *paths], cwd=REPO_ROOT, check=True)
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=REPO_ROOT)
    if result.returncode == 0:
        print("Nothing to commit.")
        return
    subprocess.run(["git", "commit", "-m", message], cwd=REPO_ROOT, check=True)
    subprocess.run(["git", "push"], cwd=REPO_ROOT, check=True)


def main():
    queue_files = glob.glob(os.path.join(QUEUE_DIR, "*.yaml")) + glob.glob(os.path.join(QUEUE_DIR, "*.yml"))
    if not queue_files:
        print("No queue entries found. Nothing to do.")
        return

    for queue_path in queue_files:
        with open(queue_path) as f:
            entry = yaml.safe_load(f)

        products_desc = "\n".join(
            f"- {p['name']}: {p['info']} (link: {p['link']})" for p in entry.get("products", [])
        )
        user_content = f"""Write a TIRENA article.

Title hint: {entry.get('title_hint', '')}
Category hint: {entry.get('category', '')}
Context: {entry.get('context', '')}

Products to feature (use ONLY this information, do not invent claims):
{products_desc}
"""

        print(f"Generating article for: {entry.get('title_hint')}")
        result = call_github_models(user_content)

        slug = slugify(result["title"])
        today = subprocess.run(["date", "+%Y-%m-%d"], capture_output=True, text=True).stdout.strip()
        filename = f"{today}-{slug}.md"

        image_slug = slug.replace("-", "_")
        cover_path = os.path.join(PUBLIC_DIR, f"{image_slug}.png")
        pin_path = os.path.join(PINS_OUT_DIR, f"{image_slug}_pin.png")
        os.makedirs(PINS_OUT_DIR, exist_ok=True)

        icon_fn = pick_icon(result["title"], result["category"], entry.get("context", ""))
        render_cover_image(result["title"], result["category"], icon_fn, cover_path)
        render_pin_image(result["title"], result["category"], result["pin_bullets"], icon_fn, pin_path)

        frontmatter = (
            "---\n"
            f"title: \"{result['title']}\"\n"
            f"description: \"{result['description']}\"\n"
            f"category: \"{result['category']}\"\n"
            f"publishDate: {today}\n"
            f"image: \"/{image_slug}.png\"\n"
            "draft: false\n"
            "---\n\n"
        )
        article_path = os.path.join(ARTICLES_DIR, filename)
        with open(article_path, "w") as f:
            f.write(frontmatter + result["body"])

        pin_info_path = os.path.join(PINS_OUT_DIR, f"{image_slug}_pinterest_content.txt")
        with open(pin_info_path, "w") as f:
            f.write(f"Pin title: {result['pin_title']}\n\n")
            f.write(f"Pin description: {result['pin_description']}\n\n")
            f.write(f"Destination URL: {SITE_URL}/articles/{today}-{slug}/\n")
            f.write(f"Pin image: pins_output/{image_slug}_pin.png\n")

        os.remove(queue_path)

        git_commit_and_push(
            [article_path, cover_path, queue_path, pin_info_path],
            f"Auto-publish article: {result['title']}"
        )
        print(f"Done: {article_path}")


if __name__ == "__main__":
    main()
