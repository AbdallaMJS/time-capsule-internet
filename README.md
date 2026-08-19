# ⏳ Time Capsule Internet – Website History Tracker

**Time Capsule Internet** is a portfolio prototype that captures the visual appearance of public websites, compares snapshots over time, and lets the user travel through a website's history with an interactive timeline.

## How to try it
1. Open **Demo Timeline** for an instant six-month example.
2. Or open **Live Capture**, paste a public URL, and click **Capture Snapshot**.
3. Capture the same site again later to compare versions.
4. Use **Before / After** and the timeline slider to inspect changes.

## Features
- Live public-website screenshot capture
- Visual change score using perceptual image hashes
- Change counter
- Interactive timeline
- Before/after comparison
- Built-in six-month demo for reviewers
- Basic blocking of localhost/private-network URLs

## Technologies
Python, Streamlit, Selenium, Chromium/ChromeDriver, Pillow, ImageHash.

## Run locally
```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

## Streamlit Community Cloud
The repository includes `packages.txt` requesting Chromium and ChromeDriver as Linux dependencies.

## Prototype limitations
- New live snapshots in the hosted app are session-based.
- A production version should use persistent object storage/database and a daily/weekly scheduler.
- Some websites block automated browsers, logins, or CAPTCHA and may not capture successfully.

## Portfolio description
> Time Capsule Internet is a Python web application that captures public websites over time, detects visual changes, and displays their evolution on an interactive timeline. It demonstrates browser automation, image comparison, web security basics, data organization, and user-interface design.

Recommended repository name: `time-capsule-internet`
