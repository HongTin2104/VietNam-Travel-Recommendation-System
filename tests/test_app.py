import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

import recommendation
import translation
import weather

READING = {
    "temperature": 27.5,
    "description": "trời nắng",
    "humidity": 70,
    "icon": "https://openweathermap.org/img/wn/01d@2x.png",
}


@pytest.fixture(autouse=True)
def no_weather_key(monkeypatch):
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)


def run_app():
    return AppTest.from_file("../main.py", default_timeout=120).run()


def search(at, text, province=None):
    at.text_area[0].input(text)
    if province:
        at.selectbox[0].select(province)
    at.button[0].click().run()
    assert not at.exception
    return at


def markdown(at):
    return [m.value for m in at.markdown]


def one_result(monkeypatch, **overrides):
    row = {
        "name": "Bãi Dài",
        "description": "Bãi biển hoang sơ.",
        "similarity": 42.0,
        "province": "Khánh Hòa",
        "old_province": "Khánh Hòa",
        "image_url": "",
        **overrides,
    }
    monkeypatch.setattr(recommendation, "recommend_places", lambda *a, **k: pd.DataFrame([row]))


def test_weather_is_skipped_without_api_key():
    assert weather.get_weather("Khánh Hòa") is None


def test_app_shows_recommendations():
    at = search(run_app(), "bãi biển hoang sơ để tắm biển")
    assert len(at.subheader) == 3


def test_app_rejects_empty_input():
    at = run_app()
    at.button[0].click().run()
    assert at.error[0].value == "Vui lòng nhập mô tả mong muốn."


def test_province_filter_limits_results_to_that_province():
    at = search(run_app(), "chùa cổ linh thiêng", province="Huế")
    provinces = [m for m in markdown(at) if m.startswith("**Tỉnh, thành:**")]
    assert len(provinces) == len(at.subheader) > 0
    assert all(m.startswith("**Tỉnh, thành:** Huế") for m in provinces)


def test_input_with_only_stopwords_finds_nothing():
    at = search(run_app(), "và của là")
    assert "Không tìm thấy địa điểm phù hợp với yêu cầu của bạn." in markdown(at)


def test_english_input_is_translated_before_searching(monkeypatch):
    monkeypatch.setattr(translation, "translate_to_vietnamese", lambda text: "bãi biển hoang sơ")
    at = search(run_app(), "wild beach")
    assert at.info[0].value.startswith("Phát hiện ngôn ngữ là tiếng Anh")
    assert "Mô tả: bãi biển hoang sơ" in markdown(at)
    assert len(at.subheader) == 3


def test_failed_translation_falls_back_to_the_original_text(monkeypatch):
    monkeypatch.setattr(translation, "translate_to_vietnamese", lambda text: None)
    at = search(run_app(), "wild beach")
    assert at.warning[0].value == "Không dịch được, sẽ tìm kiếm với nội dung gốc."


def test_shows_weather_and_the_province_before_the_merger(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-key")
    asked = []
    monkeypatch.setattr(weather, "get_weather", lambda province: asked.append(province) or READING)
    one_result(monkeypatch, province="Tuyên Quang", old_province="Hà Giang")

    at = search(run_app(), "cao nguyên đá")
    text = markdown(at)
    assert asked == ["Hà Giang"]  # weather is looked up for the pre-2025 province
    assert "**Tỉnh, thành:** Tuyên Quang (trước 7/2025: Hà Giang)" in text
    assert "**Nhiệt độ:** 27.5°C" in text
    assert "**Độ ẩm:** 70%" in text
    assert "Không có hình ảnh cho địa điểm này." in text


def test_reports_when_weather_is_unavailable(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-key")
    monkeypatch.setattr(weather, "get_weather", lambda province: None)
    one_result(monkeypatch, image_url="https://example.com/bai-dai.jpg")

    at = search(run_app(), "bãi biển")
    assert "Không thể lấy thông tin thời tiết cho địa điểm này." in markdown(at)


def test_weather_without_an_icon_shows_no_image(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-key")
    monkeypatch.setattr(weather, "get_weather", lambda province: {**READING, "icon": None})
    one_result(monkeypatch)

    at = search(run_app(), "bãi biển")
    assert "**Thời tiết:** trời nắng" in markdown(at)
    assert len(at.get("imgs")) == 0


def test_unaccented_vietnamese_is_not_translated(monkeypatch):
    """Queries like 'bai bien hoang so' should search directly, not go to the translator."""
    translated = []
    monkeypatch.setattr(translation, "translate_to_vietnamese", lambda t: translated.append(t) or "")
    at = search(run_app(), "bai bien hoang so")
    assert translated == [], "translator must not be called for unaccented Vietnamese"
    assert not at.info, "no 'Detected English' info message should appear"
    assert len(at.subheader) == 3
