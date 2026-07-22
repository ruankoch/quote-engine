# Quote Engine

A single-file, offline random quote generator. Click **New quote** to surface a random
quote — with its author, source, and theme — from a curated library of **2,000 quotes across
20 themes**, drawn from books and saved posts.

It also supports lightweight **spaced-repetition weighting** (see some quotes more or less
often), **adding / importing / editing / deleting** quotes, and **portable preferences** so you
can carry your setup between devices.

> The whole app is one self-contained `index.html` — no build step required to run it, no server,
> no dependencies, no tracking. Just open it in a browser.

## Features

- **Random surfacing** — weighted-random picker; the same quote never repeats back-to-back.
- **Frequency tuning** — **More often / Less often** buttons (or the ↑ / ↓ keys) adjust how
  often each quote appears. A badge shows its standing (Rarely → Less → Normal → More → Often).
- **Theme filter** — narrow to any one of the themes, or show all.
- **Add / Edit / Import** — add a quote (with an option to create a new theme), edit the current
  one, or bulk-import from a CSV using the same `Quote, Author, Source, Theme` columns.
- **Delete** — hide a quote for good, with an Undo toast and a Restore-all option.
- **Backup & sync** — export your preferences (weights + added + hidden quotes) as a small JSON
  and import it on another machine; or export the full effective quote list back to CSV.
- **Light / dark** toggle, and the quote text auto-scales so it always fits the window.

Keyboard: **Space** = new quote · **↑ / ↓** = more / less often · **Esc** = close the Manage panel.

> Preferences and any quotes you add in the app are saved in your browser's local storage
> (per browser / per profile). Use **Export preferences** to move them between devices, and
> **Export quotes (CSV)** to fold your edits back into `data/quotes.csv`.

## Run it locally

Just open `index.html` in any modern browser — that's it.

## Live site (GitHub Pages)

This repo includes a GitHub Actions workflow (`.github/workflows/deploy.yml`) that publishes
`index.html` to GitHub Pages on every push to `main`.

To turn the live site on:

1. Repo → **Settings** → **Pages**.
2. Under **Build and deployment → Source**, choose **GitHub Actions**.
3. Push to `main` (or re-run the workflow). Your site goes live at:

   ```
   https://ruankoch.github.io/quote-engine/
   ```

## Editing the quote library

The quotes live in [`data/quotes.csv`](data/quotes.csv) (columns: `Quote, Author, Source, Theme`).
Two ways to change them:

- **In the app** (easiest): use the **☰ Manage** panel to add, edit, import, or delete quotes,
  then **Export quotes (CSV)** and replace `data/quotes.csv`.
- **Directly**: edit `data/quotes.csv`, then regenerate the app:

  ```bash
  python3 scripts/build.py
  ```

  This rewrites `index.html` with the new data (Python 3, standard library only).

## Project structure

```
quote-engine/
├── index.html                    # the app (self-contained; open this)
├── data/
│   └── quotes.csv                # 2,000 quotes — the source of truth
├── scripts/
│   └── build.py                  # regenerates index.html from data/quotes.csv
├── .github/workflows/deploy.yml  # GitHub Pages auto-deploy
├── .gitignore
├── LICENSE
└── README.md
```

## License

Application code: [MIT](LICENSE). Quoted text remains the property of its respective authors and
publishers; it's compiled here for personal, non-commercial use.
