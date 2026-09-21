# TIRENA Full Article Automation

## What this does

You add a small file listing your affiliate links + basic product info.
GitHub automatically writes the full article (using a free AI model), generates
a matching cover image and Pinterest pin image, and publishes everything to your
site. Total cost: $0. Your only manual steps per article: write the queue file,
and (once Pinterest's API access is approved) paste the pin onto Pinterest.

## One-time setup

### 1. Get a GitHub Models token
1. Go to github.com/settings/tokens?type=beta (Fine-grained personal access tokens)
2. Click "Generate new token"
3. Name it something like "tirena-models"
4. Under "Permissions", find "Models" and set it to "Read-only"
5. Generate the token and copy it immediately

### 2. Add it as a repo secret
1. Go to github.com/Dhinesh0024/tirena → Settings → Secrets and variables → Actions
2. New repository secret
3. Name: `GH_MODELS_TOKEN`
4. Value: paste the token from step 1

### 3. Upload all these files to your repo
Upload this entire folder structure to github.com/Dhinesh0024/tirena using
"Add file" → "Upload files" (drag in the whole unzipped folder), preserving
the folder paths (.github/workflows/, scripts/, fonts/, queue/).

## Publishing an article (the part you do every time)

1. Copy `queue/example.yaml` to a new file, e.g. `queue/my-new-article.yaml`
2. Fill in:
   - `title_hint`: roughly what the article should be about
   - `category`: one of hair-care, skin-care, body-care, reviews, comparisons
   - `context`: a few sentences on angle/focus (optional but improves quality)
   - `products`: each product's name, key info (copy from the Amazon listing —
     ingredients, key claims, what it's for), and your affiliate link
3. Commit and push
4. Check the "Actions" tab on GitHub to watch it run (takes 1-2 minutes)
5. Your new article, cover image, and pin image are now live on your site
6. Check `pins_output/` in your repo for the pin image and ready-to-paste
   Pinterest title/description text, since posting to Pinterest is still
   manual until their API access comes through

## Honest limitations

- The AI writes from what you give it in `context` and `products` — it does not
  search the web or verify claims independently. Give it good product info for
  good output.
- Icon selection is keyword-based from a growing library. New/unusual topics may
  get a generic fallback icon. Tell Claude in a chat session to add a bespoke
  icon for any recurring topic that deserves one.
- Always review the generated article before considering it final — treat this
  as a strong first draft, not guaranteed-perfect copy.
