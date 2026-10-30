# Security policy

The app stores nothing about its users. A query written only in ASCII (no Vietnamese diacritics) is
treated as English and sent to Google Translate, and the weather panel calls OpenWeatherMap with the
key from `OPENWEATHER_API_KEY`; nothing else leaves the machine. Keys belong in `.env` (see `.env.example`) and must never be
committed.

If you find a security problem, or an API key that was committed by mistake, please do not open a
public issue. Report it privately through
[GitHub's private vulnerability reporting](https://github.com/HongTin2104/VietNam-Travel-Recommendation-System/security/advisories/new)
or by email to hongtin2104@gmail.com. You should get a reply within a week.

A wrong place, broken image or bad recommendation is not a security issue; please open an ordinary
issue.

Only the latest release is supported.
