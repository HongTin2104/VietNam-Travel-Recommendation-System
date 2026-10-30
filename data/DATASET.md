# Dataset card: Vietnam tourist destinations

## Summary

315 tourist destinations, five for each of Vietnam's 63 pre-2025 provinces. Each place is also mapped to one of
the 34 provincial units in effect since 1 July 2025.

| | |
|---|---|
| Records | 315 |
| Provinces (before 1 July 2025) | 63, five places each |
| Provinces (from 1 July 2025) | 34; 11 with 5 places, 17 with 10, 6 with 15 |
| Language | Vietnamese |
| Collected | 2024, compiled by hand by the repository author |
| Working image links | 247 of 315 (checked 2026-10-30 with `scripts/check_image_links.py`) |

Running `python scripts/check_image_links.py` also writes `reports/broken_images.csv` with the
`id`, `name`, `old_province` and `image_url` of every broken or missing image, so contributors can
identify the places that need replacement links. The script keeps a 0.2-second delay per place.

## Files

| File | Description |
|---|---|
| `DataSet.xlsx` | The original hand-compiled sheet. Kept unchanged. |
| `short_links.csv` | `surl.li` image links from the sheet and the image URLs they point to (`scripts/resolve_short_links.py`). |
| `processed/places.csv` | The cleaned table the app reads, built with `python scripts/build_dataset.py`. |

## Columns of `processed/places.csv`

| Column | Type | Description |
|---|---|---|
| `id` | int | Row number from the original sheet (`STT`). |
| `name` | str | Name of the destination. |
| `province` | str | Province or centrally governed city since 1 July 2025 (34 units). |
| `old_province` | str | Province before 1 July 2025 (63 units), as in the original sheet. |
| `description` | str | Short Vietnamese description, median 148 characters. Used for the TF-IDF model. |
| `rating` | float | Rating out of 5 as written in the sheet. One value is missing. |
| `keywords` | str | Comma-separated tags. Empty for 100 places. |
| `image_url` | str | Link to an image hosted by a third party. Empty when the sheet had no usable URL (6 places). |

## Processing (`scripts/build_dataset.py`)

- Unicode NFC, collapsed whitespace, trailing spaces removed from province names.
- Province typos fixed: "Quang Ninh" to "Quảng Ninh", "Nam Đinh" to "Nam Định".
- Ratings parsed from "4.5/5", "4,4/5" and "4". "47/5" is read as 4.7.
- Keywords accepted both as `"a" , "b"` and as `a, b`.
- `surl.li` short links replaced with the image URL they lead to (60 of 65 resolved). These links answer with an
  HTML page, so they never displayed as images.
- Old provinces mapped to the new ones with `scripts/province_mapping.py`, following Resolution 202/2025/QH15 of the
  National Assembly (12 June 2025). Thừa Thiên Huế is listed under Huế, the centrally governed city it became on
  1 January 2025.

## Known issues

- Id 60 is named "Hồ Ba Bể" under Ninh Thuận, but its description is a salt-water lake in Ninh Thuận. Hồ Ba Bể is
  in Bắc Kạn (id 156). The name is probably wrong.
- Id 304 is listed under Hậu Giang while its description says "Vườn cò Tân Long (Vĩnh Long)"; id 98 has the same
  name under Sóc Trăng.
- Some places share a name across provinces because they span a border or are different sites with the same name:
  Cầu Mỹ Thuận, Hồ Dầu Tiếng, Thiền Viện Trúc Lâm, Động Thiên Cung.
- Descriptions are short and uneven in length, which limits how well TF-IDF can tell places apart.
- Ratings come from the compiler's sources and are not comparable across places.
- Images are hotlinked from third-party sites and search-engine thumbnails. 68 links are broken or missing, and more
  will break over time.
- Five places per old province is a sample, not a complete list of destinations.

## License

The text data (`DataSet.xlsx`, `processed/places.csv`) is released under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Images are not part of the dataset. They belong to their
owners and are only referenced by URL.
