#!/usr/bin/env python3
"""Pull the current quotes (with tags) from the Google Sheet into data/quotes.csv.

Fetches the Apps Script web app's JSON and writes a CSV with columns
Quote, Author, Source, Theme, Tags. Intended to run in GitHub Actions (where
Google is reachable) so the repo — and the deployed page — stay a fresh,
Google-free mirror of the Sheet for networks that block Google.

Env:
  QE_SHEET_API  (required)  the Apps Script /exec URL
  QE_CSV_OUT    (optional)  output path override (default: data/quotes.csv)

Run:  QE_SHEET_API="https://script.google.com/macros/s/…/exec" python3 scripts/sync_from_sheet.py
"""
import os, sys, csv, json, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_PATH = os.environ.get("QE_CSV_OUT") or os.path.join(ROOT, "data", "quotes.csv")

api = os.environ.get("QE_SHEET_API", "").strip()
if not api:
    sys.exit("QE_SHEET_API is not set — nothing to sync from.")

req = urllib.request.Request(api, headers={"User-Agent": "quote-engine-sync"})
with urllib.request.urlopen(req, timeout=60) as resp:
    data = json.loads(resp.read().decode("utf-8"))

rows = data.get("quotes", [])
if not isinstance(rows, list):
    sys.exit("Unexpected response: no 'quotes' array.")

kept = [r for r in rows if str(r.get("quote", "")).strip()]
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
with open(OUT_PATH, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Quote", "Author", "Source", "Theme", "Tags"])
    for r in kept:
        w.writerow([r.get("quote", ""), r.get("author", ""), r.get("source", ""),
                    r.get("theme", ""), r.get("tags", "")])

print("Wrote", OUT_PATH, "-", len(kept), "quotes from the Sheet")
