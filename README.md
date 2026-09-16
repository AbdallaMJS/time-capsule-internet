# ⏳ Time Capsule Internet

A Python portfolio project for tracking how public websites evolve over time. The application captures website screenshots, stores them persistently, computes explainable visual-change metrics, and lets users compare historical versions on an interactive timeline.

## Why this project
Web pages change constantly, but most changes are difficult to observe once they disappear. This prototype explores how browser automation, image fingerprints, persistent storage, and simple change metrics can be combined into a lightweight website-history system.

## Key features
- Public-website screenshot capture with Selenium + headless Chromium
- URL normalization and blocking of localhost/private-network destinations
- Perceptual image hashing (`pHash`) for visual-change measurement
- SHA-256 HTML fingerprint plus page-length similarity signal
- Persistent SQLite storage for screenshots and metadata
- Interactive timeline and before/after comparison in Streamlit
- Interpretable change classes: minimal, small, moderate, large
- Optional APScheduler worker for repeated captures
- Unit tests for the core comparison logic

## Architecture
```text
User / Scheduler
      |
      v
timecapsule.capture  ---> Selenium / Chromium
      |
      +--> timecapsule.security  (public-host validation)
      |
      v
Snapshot metadata + PNG
      |
      v
timecapsule.storage   ---> SQLite database
      |
      v
timecapsule.analysis  ---> visual-change + HTML-similarity metrics
      |
      v
Streamlit history / before-after UI
```

## Technologies
Python, Streamlit, Selenium, Chromium/ChromeDriver, Pillow, ImageHash, SQLite, APScheduler, pytest.

## Run locally
```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

For Linux/Streamlit Community Cloud, `packages.txt` requests Chromium and ChromeDriver.

## Scheduled monitoring
A long-running machine can collect snapshots automatically:

```bash
python monitor.py https://example.com --hours 24
```

The scheduler writes to the same `data/time_capsule.db` database used by the Streamlit application.

## Testing
```bash
pytest -q
```

The tests currently focus on the pure comparison functions so the core metric behavior is reproducible without launching a browser.

## How visual change is measured
Each screenshot is converted into a perceptual hash. The Hamming distance between two hashes is normalized to a percentage. Unlike a cryptographic hash, a perceptual hash is designed so visually similar images have similar fingerprints.

This is intentionally an interpretable prototype rather than a claim of semantic understanding. A visual score can be affected by banners, ads, animations, or other layout changes.

## Security choices
Before Selenium opens a URL, the application resolves the hostname and rejects private, loopback, link-local, multicast, reserved, and unspecified IP addresses. This is a basic defense against server-side request forgery (SSRF). It is not a complete production security layer.

## Limitations and future work
- Hosted Streamlit environments may not support long-running scheduler processes; use a worker/cron service for production monitoring.
- Some sites block automated browsers or require login/CAPTCHA.
- SQLite is appropriate for a prototype but not a large distributed crawler.
- Future versions could add object storage, retry queues, semantic DOM diffs, alerting, robots-policy support, and cloud deployment.

## Portfolio takeaway
This project demonstrates browser automation, image processing, web-security basics, persistent data storage, scheduling, testing, and user-interface design. It is a software-engineering/image-analysis project rather than a trained machine-learning system.
