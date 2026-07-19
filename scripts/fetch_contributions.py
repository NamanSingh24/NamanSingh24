#!/usr/bin/env python3
"""
Fetch the public contribution calendar. No token, no GraphQL.

GitHub serves the calendar as public HTML at
    https://github.com/users/<username>/contributions
which is the same fragment the profile page itself uses.

    python scripts/fetch_contributions.py
Writes data/contributions.json
"""

import json
import os
import re
from datetime import date

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_USERNAME", "NamanSingh24")
OUT = "data/contributions.json"
URL = f"https://github.com/users/{USERNAME}/contributions"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (profile-art bot)",
    "X-Requested-With": "XMLHttpRequest",
}


def parse_count(cell) -> int:
    """Count lives in different attributes depending on GitHub's markup."""
    for attr in ("data-count", "data-level"):
        if cell.has_attr(attr) and attr == "data-count":
            try:
                return int(cell[attr])
            except ValueError:
                pass

    # newer markup puts it in the tooltip text
    txt = cell.get("aria-label") or cell.get_text(" ", strip=True) or ""
    m = re.search(r"(\d[\d,]*)\s+contribution", txt)
    if m:
        return int(m.group(1).replace(",", ""))
    if "No contributions" in txt:
        return 0

    if cell.has_attr("data-level"):
        try:
            return int(cell["data-level"])
        except ValueError:
            return 0
    return 0


def main() -> None:
    r = requests.get(URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    cells = soup.select("td.ContributionCalendar-day[data-date]")
    if not cells:
        cells = soup.select("rect.ContributionCalendar-day[data-date]")
    if not cells:
        raise SystemExit("could not find day cells; GitHub markup may have changed")

    days = []
    for c in cells:
        d = c.get("data-date")
        if not d:
            continue
        days.append({"date": d, "count": parse_count(c)})

    days.sort(key=lambda x: x["date"])

    total = sum(d["count"] for d in days)
    best = max(days, key=lambda x: x["count"]) if days else {"date": "", "count": 0}

    # streaks
    cur = longest = run = 0
    today = date.today().isoformat()
    for d in days:
        if d["count"] > 0:
            run += 1
            longest = max(longest, run)
        else:
            # today with 0 does not break the current streak yet
            if d["date"] != today:
                run = 0
    # walk backwards for the current streak
    for d in reversed(days):
        if d["count"] > 0:
            cur += 1
        elif d["date"] != today:
            break

    monthly: dict[str, int] = {}
    for d in days:
        monthly[d["date"][:7]] = monthly.get(d["date"][:7], 0) + d["count"]

    payload = {
        "username": USERNAME,
        "generated": date.today().isoformat(),
        "total": total,
        "current_streak": cur,
        "longest_streak": longest,
        "best_day": best,
        "monthly": monthly,
        "days": days,
    }

    os.makedirs("data", exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"wrote {OUT}  days={len(days)} total={total} streak={cur}")


if __name__ == "__main__":
    main()
