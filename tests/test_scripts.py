"""Tests for the helper scripts: evaluation metrics and the two link checkers (network mocked)."""

import sys
from pathlib import Path

import pandas as pd
import pytest
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import check_image_links  # noqa: E402
import evaluate  # noqa: E402
import resolve_short_links  # noqa: E402

# --- evaluate.py ---------------------------------------------------------------------------------


def test_syllables_drops_punctuation_and_digits():
    assert evaluate.syllables("Chùa Một Cột, xây năm 1049!") == "chùa một cột xây năm"


def test_load_queries_keeps_tags_shared_by_3_to_30_places():
    places = pd.DataFrame({"keywords": ["biển, đảo", "biển", "Biển, chùa", "chùa", ""]})
    assert evaluate.load_queries(places) == {"biển": {0, 1, 2}}


@pytest.mark.parametrize(
    ("ranking", "expected"),
    [
        ([1, 2, 3, 9], {"P@3": 1.0, "R@10": 0.75, "MRR": 1.0}),
        ([9, 8, 1], {"P@3": 1 / 3, "R@10": 0.25, "MRR": 1 / 3}),
        ([9, 8, 7], {"P@3": 0.0, "R@10": 0.0, "MRR": 0}),
    ],
)
def test_metrics(ranking, expected):
    assert evaluate.metrics(ranking, {1, 2, 3, 4}) == pytest.approx(expected)


@pytest.fixture
def toy_places():
    return pd.DataFrame(
        {
            "description": ["bãi biển cát trắng", "chùa cổ trên núi", "bãi biển hoang sơ", "chợ đêm"],
            "keywords": ["biển", "chùa", "biển", "chợ"],
            "rating": [4.0, 5.0, 3.0, 4.5],
        }
    )


def test_tfidf_ranker_puts_matching_places_first(toy_places):
    ranking = list(evaluate.tfidf_ranker(evaluate.syllables)(toy_places, "bãi biển"))
    assert set(ranking[:2]) == {0, 2}


def test_rating_ranker_sorts_by_rating(toy_places):
    assert list(evaluate.rating_ranker(toy_places, "anything")) == [1, 3, 0, 2]


def test_perfect_ranker_scores_one(toy_places):
    queries = {"biển": {0, 2}}
    scores = evaluate.evaluate(lambda places, q: [0, 2, 1, 3], toy_places, queries)
    assert scores["MRR"] == 1.0
    assert scores["R@10"] == 1.0


def test_random_baseline_is_deterministic(toy_places, monkeypatch):
    monkeypatch.setattr(evaluate, "RANDOM_RUNS", 5)
    queries = {"biển": {0, 2}}
    first = evaluate.random_baseline(toy_places, queries)
    assert first.equals(evaluate.random_baseline(toy_places, queries))


# --- check_image_links.py / resolve_short_links.py -----------------------------------------------


class FakeResponse:
    def __init__(self, status_code=200, content_type="image/jpeg", text=""):
        self.status_code = status_code
        self.headers = {"content-type": content_type}
        self.text = text

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class FakeSession:
    def __init__(self, responses):
        self.responses = responses
        self.headers = {}

    def get(self, url, **kwargs):
        response = self.responses[url]
        if isinstance(response, Exception):
            raise response
        return response


@pytest.mark.parametrize(
    ("response", "expected"),
    [
        (FakeResponse(), True),
        (FakeResponse(content_type="text/html"), False),
        (FakeResponse(status_code=404), False),
        (requests.Timeout(), False),
    ],
)
def test_is_image(response, expected):
    assert check_image_links.is_image(FakeSession({"u": response}), "u") is expected


def test_link_check_counts_broken_links_by_host(tmp_path, monkeypatch, capsys):
    (tmp_path / "data" / "processed").mkdir(parents=True)
    pd.DataFrame(
        {
            "id": [1, 2, 3, 4],
            "name": ["Good", "Broken", "Timeout", "Missing"],
            "old_province": ["Hà Nội"] * 4,
            "image_url": ["https://ok.vn/a.jpg", "https://dead.vn/b.jpg", "https://dead.vn/c.jpg", ""],
        }
    ).to_csv(tmp_path / "data" / "processed" / "places.csv", index=False)
    session = FakeSession(
        {
            "https://ok.vn/a.jpg": FakeResponse(),
            "https://dead.vn/b.jpg": FakeResponse(status_code=404),
            "https://dead.vn/c.jpg": requests.ConnectionError(),
        }
    )
    monkeypatch.setattr(check_image_links, "ROOT", tmp_path)
    monkeypatch.setattr(check_image_links.requests, "Session", lambda: session)
    monkeypatch.setattr(check_image_links.time, "sleep", lambda s: None)

    check_image_links.main()

    assert capsys.readouterr().out.strip() == ("1/4 image links work; broken by host: {'dead.vn': 2, '(missing)': 1}")


def test_link_check_writes_broken_rows_and_preserves_request_delay(tmp_path, monkeypatch):
    (tmp_path / "data" / "processed").mkdir(parents=True)
    places = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "name": ["Working", 'Bãi biển, "đẹp"', "Error", "Not an image", "Missing"],
            "old_province": ["Khánh Hòa"] * 5,
            "image_url": [
                "https://ok.vn/a.jpg",
                "https://dead.vn/b.jpg",
                "https://dead.vn/c.jpg",
                "https://html.vn/d",
                "",
            ],
        }
    )
    places.to_csv(tmp_path / "data" / "processed" / "places.csv", index=False)
    session = FakeSession(
        {
            "https://ok.vn/a.jpg": FakeResponse(),
            "https://dead.vn/b.jpg": FakeResponse(status_code=404),
            "https://dead.vn/c.jpg": requests.ConnectionError(),
            "https://html.vn/d": FakeResponse(content_type="text/html"),
        }
    )
    sleeps = []
    monkeypatch.setattr(check_image_links, "ROOT", tmp_path)
    monkeypatch.setattr(check_image_links.requests, "Session", lambda: session)
    monkeypatch.setattr(check_image_links.time, "sleep", sleeps.append)

    check_image_links.main()

    report = pd.read_csv(tmp_path / "reports" / "broken_images.csv", keep_default_na=False)
    pd.testing.assert_frame_equal(report, places.iloc[1:].reset_index(drop=True))
    assert sleeps == [0.2] * len(places)


def test_link_check_overwrites_stale_report_with_headers_when_all_work(tmp_path, monkeypatch):
    (tmp_path / "data" / "processed").mkdir(parents=True)
    (tmp_path / "reports").mkdir()
    report_path = tmp_path / "reports" / "broken_images.csv"
    report_path.write_text("stale results\n", encoding="utf-8")
    pd.DataFrame(
        {
            "id": [1],
            "name": ["Working"],
            "old_province": ["Hà Nội"],
            "image_url": ["https://ok.vn/a.jpg"],
        }
    ).to_csv(tmp_path / "data" / "processed" / "places.csv", index=False)
    monkeypatch.setattr(check_image_links, "ROOT", tmp_path)
    monkeypatch.setattr(
        check_image_links.requests, "Session", lambda: FakeSession({"https://ok.vn/a.jpg": FakeResponse()})
    )
    monkeypatch.setattr(check_image_links.time, "sleep", lambda _: None)

    check_image_links.main()

    assert report_path.read_text(encoding="utf-8") == "id,name,old_province,image_url\n"


INTERSTITIAL = """
<img src="https://surl.li/static/logo.png">
<img src="https://web-screen.com/shot.jpg">
<meta content="https://cdn.example.com/photos/ha-long.webp?w=800">
"""


def test_resolve_skips_the_interstitial_images():
    session = FakeSession({"https://surl.li/abc": FakeResponse(text=INTERSTITIAL)})
    assert resolve_short_links.resolve(session, "https://surl.li/abc") == (
        "https://cdn.example.com/photos/ha-long.webp?w=800"
    )


def test_resolve_returns_empty_when_no_image_is_found():
    session = FakeSession({"https://surl.li/abc": FakeResponse(text="<p>gone</p>")})
    assert resolve_short_links.resolve(session, "https://surl.li/abc") == ""


def test_resolve_short_links_writes_one_row_per_unique_short_link(tmp_path, monkeypatch):
    raw = pd.DataFrame(
        {"Ảnh": ["https://surl.li/abc ", "https://surl.li/abc", "https://cdn.vn/x.jpg", None, "https://surl.li/xyz"]}
    )
    session = FakeSession(
        {
            "https://surl.li/abc": FakeResponse(text=INTERSTITIAL),
            "https://surl.li/xyz": FakeResponse(text=""),
        }
    )
    output = tmp_path / "data" / "short_links.csv"
    output.parent.mkdir()
    monkeypatch.setattr(resolve_short_links, "ROOT", tmp_path)
    monkeypatch.setattr(resolve_short_links, "OUTPUT", output)
    monkeypatch.setattr(resolve_short_links.pd, "read_excel", lambda path: raw)
    monkeypatch.setattr(resolve_short_links.requests, "Session", lambda: session)
    monkeypatch.setattr(resolve_short_links.time, "sleep", lambda s: None)

    resolve_short_links.main()

    assert output.read_text(encoding="utf-8") == (
        "short_url,image_url\n"
        "https://surl.li/abc,https://cdn.example.com/photos/ha-long.webp?w=800\n"
        "https://surl.li/xyz,\n"
    )


def test_main_writes_the_evaluation_report(tmp_path, monkeypatch):
    (tmp_path / "data" / "processed").mkdir(parents=True)
    (tmp_path / "reports").mkdir()
    descriptions = [
        "bãi biển cát trắng nước trong",
        "bãi biển hoang sơ yên tĩnh",
        "bãi biển nhiều hải sản tươi",
        "chùa cổ trên núi cao",
        "chùa cổ kiến trúc độc đáo",
        "chùa cổ linh thiêng",
        "chợ đêm đông vui",
    ]
    pd.DataFrame(
        {
            "description": descriptions,
            "keywords": ["biển"] * 3 + ["chùa"] * 3 + [""],
            "rating": [4.0, 4.5, 3.5, 5.0, "", 4.2, 4.8],
        }
    ).to_csv(tmp_path / "data" / "processed" / "places.csv", index=False)
    monkeypatch.setattr(evaluate, "ROOT", tmp_path)
    monkeypatch.setattr(evaluate, "RANDOM_RUNS", 3)

    evaluate.main()

    report = (tmp_path / "reports" / "evaluation.md").read_text(encoding="utf-8")
    assert "2 queries" in report  # "biển" and "chùa"; the untagged place is dropped
    assert "6 tagged places" in report
    rows = [line for line in report.splitlines() if line.startswith("| TF-IDF, syllables")]
    assert rows == ["| TF-IDF, syllables (no word segmentation) | 1.000 | 1.000 | 1.000 |"]
