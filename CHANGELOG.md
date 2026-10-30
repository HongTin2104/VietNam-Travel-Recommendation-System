# Changelog

## 1.1.0 (2026-10-30)

### Added
- `python scripts/check_image_links.py` writes `reports/broken_images.csv` (`id,name,old_province,image_url`)
  listing every missing or broken image. First part of #5 (#11).

### Project
- Tests for the app, weather, translation, dataset build, evaluation and link scripts; CI fails below
  95% coverage.
- CI runs on Python 3.11-3.13 with CodeQL and pre-commit lint, and checks that `reports/evaluation.md`
  is reproducible.
- Contributing guide, pull request template, Dependabot, and a dev container for Codespaces.

No changes to the dataset or the recommendation model.

## 1.0.0 (2026-10-30)

First tagged release.

- Data mapped to the 34 provinces in effect since 1 July 2025, with the old province kept for every place.
- Cleaned dataset `data/processed/places.csv` and a dataset card (`data/DATASET.md`). 60 broken
  `surl.li` image links resolved.
- Better matching: compound words keep their syllables, so "biển" matches "bãi biển". P@3 0.217 vs
  0.036 for random, see `reports/evaluation.md`.
- Filter results by province.
- Weather key read from `OPENWEATHER_API_KEY` / `.env`; the old `api_key` file is gone.
- Updated dependencies, Python 3.11+, tests and CI.
