# Time Capsule Internet: Visual Website History Tracker

**Time Capsule Internet** is an advanced software engineering and image analysis prototype built to track and visualize changes on public websites over time. It captures live browser snapshots, utilizes perceptual image hashing to quantify visual differences, and provides an interactive timeline for users to journey through a website's evolution.

## 🌟 Key Features

- **Live Snapshot Capture:** Automates a headless browser to visit public URLs and capture full-page, high-fidelity screenshots.
- **Perceptual Image Hashing:** Employs advanced image comparison techniques (perceptual hashing) to calculate a "Visual Change Score." Unlike simple pixel-by-pixel comparison, this method understands visual structure, reducing false positives from minor rendering differences.
- **Interactive Timeline Navigation:** Features a dynamic, scrubber-based timeline allowing users to jump between different historical captures of a website instantly.
- **Before & After Analysis:** Provides side-by-side visual comparisons and detailed change metrics between sequential snapshots.
- **Security & Validation:** Includes basic safety checks to prevent Server-Side Request Forgery (SSRF) by blocking localhost, private network IPs, and invalid URLs.
- **Demonstration Mode:** Comes pre-loaded with a six-month demo timeline for immediate evaluation without requiring live capture.

## 🛠️ Technologies & Architecture

- **Core Language:** Python
- **Web Framework:** Streamlit (for rapid UI prototyping and interactive data apps)
- **Browser Automation:** Selenium WebDriver, Chromium (headless data extraction)
- **Image Processing & Analysis:** Pillow (PIL), ImageHash (for perceptual hashing and structural comparison)
- **Deployment & Environment:** Configured for Linux environments (via `packages.txt`) to ensure automated browser dependencies are met.

## 💡 How It Works

1. **Input & Validation:** The user provides a URL. The system validates it to ensure it's a publicly accessible, safe internet address.
2. **Headless Capture:** A hidden Chromium browser instance is launched via Selenium. It navigates to the URL, waits for dynamic content to load, and captures a screenshot.
3. **Data Storage:** The snapshot is saved, and its metadata (timestamp, URL) is logged.
4. **Comparison Engine:** When a new snapshot is captured for a previously tracked URL, the system uses `ImageHash` to compute a perceptual hash for both the old and new images. It then calculates the Hamming distance between these hashes to generate a human-readable visual change score.
5. **Visualization:** The Streamlit interface updates the interactive timeline and displays the calculated differences and visual comparisons.

## 🚀 Setup and Installation

To run this project locally, follow these steps:

### 1. Clone the repository

```
git clone https://github.com/AbdallaMJS/time-capsule-internet.git
cd time-capsule-internet
```
2. Create a virtual environment
```
python3 -m venv venv
```
3. Activate the virtual environment
```
source venv/bin/activate
```
After activation, the terminal prompt should usually begin with:
```
(venv)
```
4. Install the required packages
```
python -m pip install -r requirements.txt
```
6. Run the Streamlit application
```
python -m streamlit run app.py
```
## 🧠 Educational Value

This project highlights a strong foundation in practical software engineering and data extraction techniques. It goes beyond simple web development by integrating browser automation and computer vision concepts (image hashing). The ability to architect a system that independently gathers data, processes it algorithmically to find meaning (visual changes), and presents it interactively demonstrates the technical maturity and problem-solving skills highly valued in rigorous AI and computer science programs.

## 🔮 Future Enhancements

- **Persistent Database:** Transitioning from session-based storage to a robust database (e.g., PostgreSQL or MongoDB) for long-term tracking.
- **Automated Scheduling:** Implementing a cron job or Celery task queue to automatically capture targeted sites daily or weekly without user intervention.
- **Advanced Computer Vision:** Upgrading from perceptual hashing to structural similarity index (SSIM) or deep learning-based feature extraction for even more nuanced change detection (e.g., detecting *what* changed, like text vs. images).

---
*Developed by Abdalla M.J.S. Alblooshi as part of a technical portfolio demonstrating software engineering, automation, and applied image analysis.*
