"""Clean data/DataSet.xlsx and write data/processed/places.csv with old and new (2025) provinces."""

import re
import unicodedata
from pathlib import Path

import pandas as pd
from province_mapping import OLD_TO_NEW, PROVINCE_TO_REGION

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data" / "DataSet.xlsx"
SHORT_LINKS = ROOT / "data" / "short_links.csv"
OUTPUT = ROOT / "data" / "processed" / "places.csv"

TYPOS = {"Quang Ninh": "Quảng Ninh", "Nam Đinh": "Nam Định"}


def clean_text(value):
    if not isinstance(value, str):
        return ""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", value)).strip()


def parse_rating(value):
    match = re.match(r"\s*(\d+(?:[.,]\d+)?)", str(value))
    if not match:
        return None
    rating = float(match.group(1).replace(",", "."))
    # One entry reads "47/5", a missing decimal point for 4.7.
    return rating / 10 if rating > 5 else rating


def parse_keywords(value):
    if not isinstance(value, str):
        return ""
    # Some rows quote every keyword ("biển" , "chụp ảnh"), others are a plain comma-separated list.
    parts = re.findall(r'"([^"]*)"', value) if '"' in value else value.split(",")
    return ", ".join(k for k in (clean_text(k).rstrip(".") for k in parts) if k)


def load_short_links(path=SHORT_LINKS):
    if not path.exists():
        return {}
    links = pd.read_csv(path, keep_default_na=False)
    return dict(zip(links["short_url"], links["image_url"], strict=True))


def clean_image_url(value, short_links):
    url = clean_text(value)
    url = short_links.get(url, url)
    return url if url.startswith(("http://", "https://")) and "surl.li/" not in url else ""


def build(source=SOURCE):
    short_links = load_short_links()
    raw = pd.read_excel(source)
    raw.columns = [clean_text(c) for c in raw.columns]

    old_province = raw["Vị trí"].map(clean_text).replace(TYPOS)
    region = old_province.map(OLD_TO_NEW).map(PROVINCE_TO_REGION)
    unknown = sorted(set(old_province) - set(OLD_TO_NEW))
    if unknown:
        raise ValueError(f"Provinces missing from the mapping: {unknown}")

    return pd.DataFrame(
        {
            "id": raw["STT"],
            "name": raw["Tên địa điểm"].map(clean_text),
            "province": old_province.map(OLD_TO_NEW),
            "old_province": old_province,
            "region": region,
            "description": raw["Mô tả"].map(clean_text),
            "rating": raw["Đánh giá"].map(parse_rating),
            "keywords": raw["Từ Khóa"].map(parse_keywords),
            "image_url": raw["Ảnh"].map(lambda u: clean_image_url(u, short_links)),
        }
    )


def main():
    places = build()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    places.to_csv(OUTPUT, index=False, encoding="utf-8", lineterminator="\n")
    print(f"{len(places)} places, {places['province'].nunique()} provinces -> {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
