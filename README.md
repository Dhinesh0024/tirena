# TIRENA — Setup & Deploy

This is the full site: homepage, category pages (Hair/Skin/Body Care, Reviews, Comparisons),
an article template, and a content pipeline wired for Pages CMS. One sample article is
included so you can see the whole flow work before writing real content.

You are not writing any code from here on — everything below is one-time setup clicking.

## 1. Push this to GitHub (5 min)

1. Go to github.com → **New repository** → name it `tirena` → keep it **Public** (Cloudflare
   Pages free tier and Pages CMS both work with public repos with no extra cost) → Create.
2. On your computer, unzip this project, then in a terminal inside the folder run:
   ```
   git init
   git add .
   git commit -m "Initial TIRENA site"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/tirena.git
   git push -u origin main
   ```
   (No local Node/git setup? GitHub's web UI also lets you drag-and-drop the unzipped
   folder into a new repo directly — that works too, just slower for future edits.)

## 2. Connect Cloudflare Pages (5 min)

1. Go to the Cloudflare dashboard → **Workers & Pages** → **Create** → **Pages** →
   **Connect to Git**.
2. Select your `tirena` GitHub repo.
3. Build settings:
   - Framework preset: **Astro**
   - Build command: `npm run build`
   - Build output directory: `dist`
4. Deploy. You'll get a live URL like `tirena-xyz.pages.dev` immediately — that's your
   free hosting, no domain purchase needed yet.

## 3. Connect Pages CMS (5 min)

1. Go to **pagescms.org** → sign in with GitHub → **Add project** → select `tirena`.
2. It will read the `.pages.yml` file already in this repo and build the editing
   interface automatically — you'll see an "Articles" section matching the fields below.
3. To publish an article: New → Articles → fill in Title, Description, Category,
   Publish Date, Featured Image → write the body → Save.
4. Saving commits a new Markdown file to GitHub, which triggers an automatic Cloudflare
   Pages rebuild. The article is live in about a minute — no manual file editing, ever.

## What's already built

- Homepage exactly matching the planned layout: Hero → Explore Personal Care (3 categories)
  → Start Here → Latest from TIRENA (auto-updating feed) → Make a Better Choice
  (Reviews/Comparisons) → Why TIRENA → About
- Category pages for Hair Care, Skin Care, Body Care, Reviews, Comparisons — each
  auto-lists its own articles, and shows a clean empty-state until you publish
- Article template with breadcrumb, featured image, and a `Content` slot for the
  article body
- Mobile-first responsive layout (stacks cleanly on phone/tablet — this matters
  because Pinterest traffic is almost entirely mobile)
- An FTC-appropriate affiliate disclosure already in the footer and About page
- `.pages.yml` already configured — the CMS fields match the site's content schema
  exactly, so there's no separate setup step for that

## What's intentionally NOT done yet (do this after, not before, launch)

- No affiliate links inserted anywhere — add them once you're approved for a program
- No real articles beyond the one sample — replace/delete it before going live
- No custom domain connected — the free `.pages.dev` URL works fine for testing and
  even for early Pinterest pins while a domain purchase can wait
- No email capture — add this once you pick an email tool (Beehiiv/Kit/MailerLite)
- No Google Search Console / Analytics — add once the site is live at a stable URL

## Local preview (optional, only if you have Node.js installed)

```
npm install
npm run dev
```
Opens at `http://localhost:4321`.
"# tirena" 
