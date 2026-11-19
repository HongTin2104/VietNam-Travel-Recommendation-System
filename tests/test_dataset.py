import sys
import unicodedata
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import build_dataset  # noqa: E402
from build_dataset import (  # noqa: E402
    build,
    clean_image_url,
    clean_text,
    load_short_links,
    parse_keywords,
    parse_rating,
)
from province_mapping import MERGERS, NEW_PROVINCES, OLD_TO_NEW, REGIONS  # noqa: E402


def test_mapping_covers_63_old_and_34_new_provinces():
    assert len(OLD_TO_NEW) == 63
    assert len(NEW_PROVINCES) == 34
    assert OLD_TO_NEW["Hà Giang"] == "Tuyên Quang"
    assert OLD_TO_NEW["Bình Dương"] == "TP. Hồ Chí Minh"
    assert OLD_TO_NEW["Thừa Thiên Huế"] == "Huế"
    assert OLD_TO_NEW["Quảng Ninh"] == "Quảng Ninh"


def test_each_old_province_merges_into_exactly_one_new_one():
    olds = [old for group in MERGERS.values() for old in group]
    assert len(olds) == len(set(olds))


def test_evry_new_provinces_has_exactly_one_region():
    provinces = {province for provinces in REGIONS.values() for province in provinces}
    assert sorted(provinces) == NEW_PROVINCES
    assert len(REGIONS) == 6


def test_parse_rating():
    assert parse_rating("4.5/5") == 4.5
    assert parse_rating("4,4/5") == 4.4
    assert parse_rating("47/5") == 4.7
    assert parse_rating("3") == 3.0
    assert parse_rating(float("nan")) is None


def test_parse_keywords_accepts_both_formats():
    assert parse_keywords('"biển" , "chụp ảnh " ,"văn hóa"') == "biển, chụp ảnh, văn hóa"
    assert parse_keywords("núi, thiên nhiên,  hùng vĩ.") == "núi, thiên nhiên, hùng vĩ"
    assert parse_keywords(None) == ""


def test_processed_csv_is_up_to_date():
    expected = build()
    actual = pd.read_csv("data/processed/places.csv", keep_default_na=False)
    assert len(actual) == len(expected) == 315
    assert actual["province"].nunique() == 34
    assert list(actual["province"]) == list(expected["province"])
    assert list(actual["name"]) == list(expected["name"])


def test_clean_text_composes_unicode_and_collapses_whitespace():
    decomposed = unicodedata.normalize("NFD", "  Hòa   Bình  ")
    assert clean_text(decomposed) == "Hòa Bình"
    assert clean_text(None) == ""


def test_clean_image_url_resolves_short_links_and_drops_bad_urls():
    short = {"https://surl.li/abc": "https://cdn.vn/a.jpg", "https://surl.li/dead": ""}
    assert clean_image_url(" https://surl.li/abc ", short) == "https://cdn.vn/a.jpg"
    assert clean_image_url("https://surl.li/dead", short) == ""
    assert clean_image_url("https://surl.li/unknown", short) == ""
    assert clean_image_url("ảnh đẹp", short) == ""
    assert clean_image_url(None, short) == ""


def test_load_short_links_without_the_file_is_empty(tmp_path):
    assert load_short_links(tmp_path / "missing.csv") == {}


def raw_rows(**overrides):
    row = {
        "STT": 1,
        "Tên địa điểm": "Hồ Ba Bể",
        "Vị trí": "Bắc Kạn",
        "Mô tả": "Hồ nước ngọt tự nhiên.",
        "Đánh giá": "4,6/5",
        "Từ Khóa": "hồ, thiên nhiên",
        "Ảnh": "https://cdn.vn/ba-be.jpg",
        **overrides,
    }
    return pd.DataFrame([row])


def test_build_fixes_province_typos_and_maps_to_the_new_province(tmp_path):
    source = tmp_path / "DataSet.xlsx"
    raw_rows(**{"Vị trí": "Nam Đinh"}).to_excel(source, index=False)
    place = build(source).iloc[0]
    assert (place["old_province"], place["province"]) == ("Nam Định", "Ninh Bình")
    assert place["rating"] == 4.6


def test_build_rejects_unknown_provinces(tmp_path):
    source = tmp_path / "DataSet.xlsx"
    raw_rows(**{"Vị trí": "Atlantis"}).to_excel(source, index=False)
    with pytest.raises(ValueError, match="Atlantis"):
        build(source)


def test_main_writes_the_processed_csv(tmp_path, monkeypatch, capsys):
    output = tmp_path / "data" / "processed" / "places.csv"
    monkeypatch.setattr(build_dataset, "ROOT", tmp_path)
    monkeypatch.setattr(build_dataset, "OUTPUT", output)
    places = pd.DataFrame({"name": ["Hồ Ba Bể", "Tràng An"], "province": ["Thái Nguyên", "Ninh Bình"]})
    monkeypatch.setattr(build_dataset, "build", lambda: places)

    build_dataset.main()

    assert pd.read_csv(output).equals(places)
    expected = f"2 places, 2 provinces -> {Path('data/processed/places.csv')}"
    assert capsys.readouterr().out.strip() == expected
