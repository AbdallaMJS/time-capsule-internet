from __future__ import annotations

import hashlib
import io
import os
import time
from datetime import datetime
from urllib.parse import urlparse

import imagehash
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait

from .security import ensure_public_host, normalize_url


def build_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1440,1000")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--lang=en-US")

    for candidate in ("/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome"):
        if os.path.exists(candidate):
            options.binary_location = candidate
            break

    for candidate in ("/usr/bin/chromedriver", "/usr/lib/chromium/chromedriver"):
        if os.path.exists(candidate):
            return webdriver.Chrome(service=Service(candidate), options=options)

    return webdriver.Chrome(options=options)


def capture_website(raw_url: str) -> dict:
    url = normalize_url(raw_url)
    ensure_public_host(url)
    driver = None
    try:
        driver = build_driver()
        driver.set_page_load_timeout(35)
        driver.get(url)
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.readyState") in ("interactive", "complete")
        )
        time.sleep(1.0)

        png = driver.get_screenshot_as_png()
        html = driver.page_source or ""
        final_url = driver.current_url
        image = Image.open(io.BytesIO(png)).convert("RGB")

        return {
            "site_key": (urlparse(final_url).netloc or urlparse(url).netloc).lower(),
            "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
            "title": driver.title or urlparse(final_url).hostname or "Untitled website",
            "requested_url": url,
            "final_url": final_url,
            "png": png,
            "phash": str(imagehash.phash(image)),
            "html_hash": hashlib.sha256(html.encode("utf-8", errors="ignore")).hexdigest(),
            "html_length": len(html),
        }
    finally:
        if driver is not None:
            driver.quit()
