"""Count working image URLs and write the broken places to reports/broken_images.csv."""

import time
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
REPORT_COLUMNS = ("id", "name", "old_province", "image_url")


def is_image(session, url):
    try:
        with session.get(url, timeout=15, stream=True) as response:
            return response.status_code == 200 and response.headers.get("content-type", "").startswith("image/")
    except requests.RequestException:
        return False


def main():
    places = pd.read_csv(ROOT / "data" / "processed" / "places.csv", keep_default_na=False)
    session = requests.Session()
    session.headers["User-Agent"] = "VietNam-Travel-Recommendation-System link check"

    broken = Counter()
    broken_rows = []
    for place in places.itertuples(index=False):
        url = place.image_url
        if not url or not is_image(session, url):
            broken[urlparse(url).netloc if url else "(missing)"] += 1
            broken_rows.append({column: getattr(place, column) for column in REPORT_COLUMNS})
        time.sleep(0.2)

    report = ROOT / "reports" / "broken_images.csv"
    report.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(broken_rows, columns=REPORT_COLUMNS).to_csv(report, index=False)

    working = len(places) - sum(broken.values())
    print(f"{working}/{len(places)} image links work; broken by host: {dict(broken.most_common(8))}")


if __name__ == "__main__":
    main()
