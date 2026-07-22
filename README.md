# Quote Engine

A single-file random quote generator. Click **New quote** to surface a random
quote — with its author, source, and theme — from a curated library of **2,000 quotes across
20 themes**, drawn from books and saved posts.

It supports lightweight **spaced-repetition weighting** (see some quotes more or less
often), **adding / editing / importing** quotes, and an **optional Google Sheet backend** so the
quotes come from a spreadsheet you can edit anywhere — and your Less/More/Never-show tweaks
write straight back to it.

> The app is one self-contained `index.html`. It runs with **no server and no build step** —
> just open it in a browser. The Google Sheet is optional and layers on top.

## Features

- **Random surfacing** — weighted-random picker; the same quote never repeats back-to-back.
- **Frequency tuning** — **More often / Less often** (or the ↑ / ↓ keys) adjust how often each
  quote appears (Rarely → Less → Normal → More → Often).
- **Never show** — hide a quote, with an Undo toast and a Restore-all option.
- **Add / Edit / Import** — add a quote, edit the current one, or bulk-import a CSV.
- **Theme filter** — narrow to one theme or show all.
- **Google Sheet backend (optional)** — keep the quotes in a Sheet, steer them with a `Tags`
  column (`exclude`, `more`, `less`, …), and have the in-app buttons write back to the Sheet.
- **Light / dark** toggle; quote text auto-scales to fit.

Keyboard: **Space** = new quote · **↑ / ↓** = more / less often · **Esc** = close the Manage panel.

## Two modes

Decided at build time by whether a Google Sheet URL is present:

| | **Local mode** (default) | **Sheet mode** (Google Sheet connected) |
|---|---|---|
| Source of quotes | built-in copy in `index.html` | your Google Sheet |
| Where changes save | this browser's `localStorage` | back to the Sheet |
| Edit from elsewhere | — | edit the Sheet directly; reload the app |
| Setup | none | see [Connect a Google Sheet](#connect-a-google-sheet-optional) |

If a Sheet is configured but unreachable, the app falls back to local mode so it always works.

## Run it locally

Just open `index.html` in any modern browser — that's it.

## Connect a Google Sheet (optional)

This makes a Google Sheet the source of quotes and lets the app read **and write** it. A static
page can't write to Google on its own, so a tiny (free) **Google Apps Script** bundled with the
Sheet acts as the read/write endpoint.

1. **Make the Sheet.** New Google Sheet → **File ▸ Import ▸ Upload** [`data/quotes.csv`](data/quotes.csv)
   (choose *Replace current sheet*). You'll have columns `Quote, Author, Source, Theme`. `ID` and
   `Tags` columns are added automatically on first run.
2. **Add the script.** **Extensions ▸ Apps Script**, delete the sample, paste
   [`google-apps-script/Code.gs`](google-apps-script/Code.gs), Save.
3. **Deploy it.** **Deploy ▸ New deployment ▸ Web app** → *Execute as:* **Me**, *Who has access:*
   **Anyone** → **Deploy**, authorise, and copy the **Web app URL** (ends in `/exec`).
4. **Bake the URL into the app** and rebuild:

   ```bash
   QE_SHEET_API="https://script.google.com/macros/s/AKfy…/exec" python3 scripts/build.py
   ```

   Commit the regenerated `index.html` and push. (You can also paste the URL into the
   `window.QE_CONFIG` line near the top of `index.html`; a rebuild overwrites hand-edits.)

That's it — the app now reads the Sheet and every Less/More/Never-show/Add writes back to it.

### Steering quotes with the `Tags` column

Type these in a row's **Tags** cell (by hand in the Sheet, or let the app's buttons set them):

| Tag | Effect |
|---|---|
| `exclude` (or `hide`, `off`) | never show this quote |
| `rarely` | show much less often |
| `less` | show less often |
| *(none)* | normal |
| `more` | show more often |
| `often` | show much more often |

Any other words you put in `Tags` are your own free-form labels — the app keeps them untouched
when it updates a row.

### A note on access

The web app is deployed as **Anyone**, so anyone who has the `/exec` URL can post to the Sheet.
For a personal tool that's usually fine. For a light deterrent you can set `WRITE_KEY` in
`Code.gs` and pass a matching `QE_SHEET_KEY="…"` to `build.py` — but since it ships inside the
page it only stops casual pokes, not a determined person. Real protection would mean adding
Google sign-in (heavier); ask if you want that.

## Adding quotes

- **In the app**: **☰ Manage ▸ Add a quote**, or bulk-import a CSV in the same panel. In Sheet
  mode these append rows to the Sheet; in local mode they save to this browser.
- **In the Sheet**: just add a row. It shows up in the app on reload.
- **In the library file**: edit [`data/quotes.csv`](data/quotes.csv), then `python3 scripts/build.py`
  to refresh the built-in copy.

## Live site (GitHub Pages)

A GitHub Actions workflow (`.github/workflows/deploy.yml`) publishes `index.html` to GitHub Pages
on every push to `main`, at `https://ruankoch.github.io/quote-engine/`.

## Project structure

```
quote-engine/
├── index.html                    # the app (self-contained; open this)
├── data/
│   └── quotes.csv                # 2,000 quotes — import this into your Sheet
├── scripts/
│   └── build.py                  # regenerates index.html (bakes in the Sheet URL)
├── google-apps-script/
│   └── Code.gs                   # the Sheet's read/write web-app backend
├── .github/workflows/deploy.yml  # GitHub Pages auto-deploy
├── .gitignore
├── LICENSE
└── README.md
```

## License

Application code: [MIT](LICENSE). Quoted text remains the property of its respective authors and
publishers; it's compiled here for personal, non-commercial use.
