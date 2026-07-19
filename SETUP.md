# Setup

Everything here is already generated except the ASCII portrait, which needs your photo.

## 0. Get it onto GitHub

Create a repo named exactly `NamanSingh24` (must match your username), public.

```bash
unzip naman-profile.zip
cd naman-profile
git init
git add -A
git commit -m "profile art"
git branch -M main
git remote add origin https://github.com/NamanSingh24/NamanSingh24.git
git push -u origin main
```

At this point your profile renders with a placeholder portrait and seeded
heatmap data. Fix both below.

## 1. Generate the real portrait

Convert your HEIC to JPG first (iPhone photos are HEIC; PIL will not open
them without extra plugins):

```bash
# macOS
sips -s format jpeg IMG_7182.HEIC --out source-photo.jpg

# or with imagemagick anywhere
magick IMG_7182.HEIC source-photo.jpg
```

Then:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/requirements.txt

python scripts/prep_photo.py source-photo.jpg   # writes source-prepped.png
python scripts/make_ascii_svg.py                # writes naman-ascii.svg
```

Open `source-prepped.png` and check the face is clearly readable in
grayscale. If it looks flat or muddy, bump `clipLimit` in `prep_photo.py`
from `2.5` up toward `4.0` and rerun.

Open `naman-ascii.svg` in a browser. If the portrait is too dark, raise the
gamma exponent in `make_ascii_svg.py` (`arr ** 1.05` toward `1.3`). Too
faint, lower it toward `0.85`.

`rembg` downloads a model on first run, so expect a slow first execution.

## 2. Get real contribution data

```bash
pip install requests beautifulsoup4
python scripts/fetch_contributions.py
python scripts/render_heatmap_svg.py
```

This replaces the seeded placeholder in `data/contributions.json`.

## 3. Commit

```bash
git add -A
git commit -m "real portrait + live contributions"
git push
```

## 4. Turn on the daily refresh

Go to the repo's **Actions** tab, pick **Update profile art**, and hit
**Run workflow** once to confirm it commits. After that it runs itself at
~06:17 UTC daily.

If the push step fails, check Settings > Actions > General > Workflow
permissions is set to **Read and write**.

## Editing the info card

All the copy lives in the `LINES` list in `scripts/make_info_card.py`.
Change it, rerun `python scripts/make_info_card.py`, commit.

For a frozen frame (useful for previewing locally):

```bash
STATIC=1 python scripts/make_info_card.py
```

## Notes

- GitHub strips `<script>` and inline `style` from READMEs. All motion
  lives inside the SVGs.
- `<br>` is the only vertical spacing GitHub honors.
- `<h1>` and `<h2>` draw a full-width underline rule. The README uses
  `<h3>` for the shell prompts to avoid that.
- Widths are aligned on purpose: heatmap 860 = portrait 370 + card 490.
  If you change one, change the others.
- If `fetch_contributions.py` stops finding cells, GitHub changed its
  markup. The selectors are at the top of `main()`.
