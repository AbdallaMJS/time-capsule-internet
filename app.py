import hashlib
import io
import ipaddress
import os
import socket
import time
from datetime import datetime
from urllib.parse import urlparse

import imagehash
import streamlit as st
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait


APP_TITLE = "Time Capsule Internet"
DEFAULT_URL = "https://example.com"

st.set_page_config(
    page_title=f"{APP_TITLE} – Website History Tracker",
    page_icon="⏳",
    layout="wide",
)

CUSTOM_CSS = """
<style>
.block-container {max-width: 1180px; padding-top: 2rem;}
.hero {
    padding: 1.25rem 1.4rem;
    border: 1px solid rgba(128,128,128,.25);
    border-radius: 18px;
    margin-bottom: 1rem;
}
.hero h1 {margin: 0 0 .35rem 0; font-size: 2.25rem;}
.hero p {margin: 0; opacity: .82; font-size: 1.05rem;}
.step {
    padding: .85rem 1rem;
    border: 1px solid rgba(128,128,128,.22);
    border-radius: 14px;
    min-height: 92px;
}
.small-note {opacity: .72; font-size: .9rem;}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero">
      <h1>⏳ Time Capsule Internet</h1>
      <p><b>Website History Tracker</b> — capture a public website, detect visual changes, and travel through its history on a timeline.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "snapshots" not in st.session_state:
    st.session_state.snapshots = {}


def normalize_url(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        raise ValueError("Please enter a website URL.")
    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw
    parsed = urlparse(raw)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Please enter a valid http/https website URL.")
    return raw


def ensure_public_host(url: str) -> None:
    hostname = urlparse(url).hostname
    if not hostname:
        raise ValueError("Invalid host.")

    if hostname.lower() in {"localhost", "localhost.localdomain"}:
        raise ValueError("Local/private addresses are not allowed.")

    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        raise ValueError("The website address could not be resolved.")

    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            raise ValueError("Local/private network addresses are not allowed.")


def build_driver():
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

    chromium_candidates = [
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/usr/bin/google-chrome",
    ]
    for candidate in chromium_candidates:
        if os.path.exists(candidate):
            options.binary_location = candidate
            break

    driver_candidates = [
        "/usr/bin/chromedriver",
        "/usr/lib/chromium/chromedriver",
    ]
    for candidate in driver_candidates:
        if os.path.exists(candidate):
            return webdriver.Chrome(
                service=Service(candidate),
                options=options,
            )

    return webdriver.Chrome(options=options)


def capture_website(url: str) -> dict:
    ensure_public_host(url)
    driver = None

    try:
        driver = build_driver()
        driver.set_page_load_timeout(35)
        driver.get(url)

        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.readyState")
            in ("interactive", "complete")
        )
        time.sleep(1.2)

        png = driver.get_screenshot_as_png()
        title = (
            driver.title
            or urlparse(driver.current_url).hostname
            or "Untitled website"
        )
        html = driver.page_source or ""
        final_url = driver.current_url

        image = Image.open(io.BytesIO(png)).convert("RGB")
        phash = str(imagehash.phash(image))
        html_hash = hashlib.sha256(
            html.encode("utf-8", errors="ignore")
        ).hexdigest()

        return {
            "timestamp": datetime.now()
            .astimezone()
            .strftime("%Y-%m-%d %H:%M:%S %Z"),
            "title": title,
            "requested_url": url,
            "final_url": final_url,
            "png": png,
            "phash": phash,
            "html_hash": html_hash,
            "html_length": len(html),
        }

    finally:
        if driver is not None:
            driver.quit()


def visual_change_score(a: dict, b: dict) -> float:
    h1 = imagehash.hex_to_hash(a["phash"])
    h2 = imagehash.hex_to_hash(b["phash"])
    max_bits = h1.hash.size
    return round((h1 - h2) / max_bits * 100, 1)


def html_similarity(a: dict, b: dict) -> float:
    if a["html_hash"] == b["html_hash"]:
        return 100.0

    x = a["html_length"]
    y = b["html_length"]

    if max(x, y) == 0:
        return 100.0

    return round(min(x, y) / max(x, y) * 100, 1)


def count_visual_changes(items: list[dict], threshold: float = 4.0) -> int:
    if len(items) < 2:
        return 0

    changes = 0
    for previous, current in zip(items, items[1:]):
        if visual_change_score(previous, current) >= threshold:
            changes += 1

    return changes


live_tab, demo_tab, explainer_tab = st.tabs(
    ["🌐 Live Capture", "🕰️ Demo Timeline", "📘 How It Works"]
)

with live_tab:
    st.subheader("Capture a public website")
    st.caption(
        "Paste a URL, capture its current appearance, then capture it again later to detect visual changes."
    )

    url_input = st.text_input(
        "Website URL",
        value=DEFAULT_URL,
        placeholder="https://example.com",
        help="Public http/https websites only.",
    )

    col_capture, col_clear = st.columns([2, 1])

    with col_capture:
        capture_clicked = st.button(
            "📸 Capture Snapshot",
            type="primary",
            use_container_width=True,
        )

    with col_clear:
        clear_clicked = st.button(
            "🧹 Clear Session",
            use_container_width=True,
        )

    if clear_clicked:
        st.session_state.snapshots = {}
        st.rerun()

    if capture_clicked:
        try:
            normalized = normalize_url(url_input)

            with st.spinner(
                "Opening the website and capturing its appearance..."
            ):
                snap = capture_website(normalized)

            key = urlparse(snap["final_url"]).netloc.lower()
            st.session_state.snapshots.setdefault(key, []).append(snap)
            st.success("Snapshot captured successfully.")

        except Exception as exc:
            st.error(
                "Live capture could not complete for this website. "
                "Some websites block automated browsers, require login/CAPTCHA, "
                "or take too long to load."
            )
            st.code(str(exc))

    if st.session_state.snapshots:
        site_keys = list(st.session_state.snapshots.keys())

        chosen_site = st.selectbox(
            "Captured website",
            site_keys,
        )

        items = st.session_state.snapshots[chosen_site]

        st.divider()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Snapshots", len(items))
        m2.metric("Visual changes", count_visual_changes(items))
        m3.metric("First capture", items[0]["timestamp"].split(" ")[0])
        m4.metric("Latest capture", items[-1]["timestamp"].split(" ")[0])

        # Important fix:
        # Streamlit sliders require min_value < max_value.
        # With one snapshot, we simply display Snapshot 1 without a slider.
        if len(items) == 1:
            idx = 0
            st.caption("Timeline: Snapshot 1")
        else:
            idx = st.slider(
                "Travel through time",
                min_value=0,
                max_value=len(items) - 1,
                value=len(items) - 1,
                format="Snapshot %d",
            )

        current = items[idx]

        st.markdown(
            f"### {current['title']}\n"
            f"**Captured:** {current['timestamp']}  \n"
            f"**URL:** {current['final_url']}"
        )

        st.image(
            current["png"],
            use_container_width=True,
        )

        if len(items) >= 2:
            st.divider()
            st.subheader("Before / After comparison")

            before_col, after_col = st.columns(2)

            with before_col:
                before_idx = st.selectbox(
                    "Before snapshot",
                    range(len(items)),
                    index=max(0, len(items) - 2),
                    format_func=lambda i: (
                        f"#{i + 1} — {items[i]['timestamp']}"
                    ),
                )

            with after_col:
                after_idx = st.selectbox(
                    "After snapshot",
                    range(len(items)),
                    index=len(items) - 1,
                    format_func=lambda i: (
                        f"#{i + 1} — {items[i]['timestamp']}"
                    ),
                )

            before = items[before_idx]
            after = items[after_idx]

            score = visual_change_score(before, after)
            changed = score >= 4.0

            c1, c2, c3 = st.columns(3)
            c1.metric("Visual change score", f"{score}%")
            c2.metric("Appearance changed?", "Yes" if changed else "No")
            c3.metric(
                "Page-size similarity",
                f"{html_similarity(before, after)}%",
            )

            left, right = st.columns(2)

            with left:
                st.caption(f"BEFORE — {before['timestamp']}")
                st.image(
                    before["png"],
                    use_container_width=True,
                )

            with right:
                st.caption(f"AFTER — {after['timestamp']}")
                st.image(
                    after["png"],
                    use_container_width=True,
                )

    else:
        st.info(
            "No live snapshots yet. Try the Demo Timeline tab to see the complete idea immediately."
        )


with demo_tab:
    st.subheader("Six months of website history — instant demo")
    st.write(
        "This built-in demo lets reviewers understand the project immediately, "
        "without waiting months for real snapshots."
    )

    demo_items = [
        {
            "date": "2026-01-10",
            "label": "Launch",
            "image": "demo/demo_1.png",
            "change": "Initial homepage",
        },
        {
            "date": "2026-03-02",
            "label": "New Programs",
            "image": "demo/demo_2.png",
            "change": "New programs section and updated hero message",
        },
        {
            "date": "2026-05-18",
            "label": "Admissions",
            "image": "demo/demo_3.png",
            "change": "Admissions campaign and new call-to-action",
        },
        {
            "date": "2026-07-29",
            "label": "Summer Refresh",
            "image": "demo/demo_4.png",
            "change": "Navigation, statistics, and layout refreshed",
        },
    ]

    d1, d2, d3 = st.columns(3)
    d1.metric("Tracked period", "6 months")
    d2.metric("Snapshots", len(demo_items))
    d3.metric("Detected changes", len(demo_items) - 1)

    demo_idx = st.slider(
        "Timeline",
        0,
        len(demo_items) - 1,
        len(demo_items) - 1,
        format="Version %d",
        key="demo_timeline",
    )

    item = demo_items[demo_idx]

    st.markdown(f"### {item['date']} — {item['label']}")
    st.caption(item["change"])
    st.image(
        item["image"],
        use_container_width=True,
    )

    if demo_idx > 0:
        st.subheader("What changed from the previous version?")

        previous = demo_items[demo_idx - 1]

        left, right = st.columns(2)

        with left:
            st.caption(f"BEFORE — {previous['date']}")
            st.image(
                previous["image"],
                use_container_width=True,
            )

        with right:
            st.caption(f"AFTER — {item['date']}")
            st.image(
                item["image"],
                use_container_width=True,
            )

        st.success(f"Change detected: {item['change']}")


with explainer_tab:
    st.subheader("Project idea")
    st.write(
        "Time Capsule Internet tracks how public websites evolve. "
        "Each capture stores a screenshot and a visual fingerprint. "
        "Later captures are compared with earlier ones to detect visible change."
    )

    a, b, c, d = st.columns(4)

    with a:
        st.markdown(
            '<div class="step"><b>1. Enter URL</b><br>'
            '<span class="small-note">Choose a public website.</span></div>',
            unsafe_allow_html=True,
        )

    with b:
        st.markdown(
            '<div class="step"><b>2. Capture</b><br>'
            '<span class="small-note">Save its current appearance.</span></div>',
            unsafe_allow_html=True,
        )

    with c:
        st.markdown(
            '<div class="step"><b>3. Compare</b><br>'
            '<span class="small-note">Detect visual differences.</span></div>',
            unsafe_allow_html=True,
        )

    with d:
        st.markdown(
            '<div class="step"><b>4. Time Travel</b><br>'
            '<span class="small-note">Scrub through the timeline.</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown("### What this prototype demonstrates")

    st.markdown(
        """
- Browser automation and screenshot capture
- URL validation and basic private-network protection
- Visual fingerprinting with perceptual image hashes
- Change counting and before/after comparison
- Interactive timeline UI in Streamlit
- A built-in six-month demo so the concept is obvious to reviewers
        """
    )

    st.markdown("### Prototype limitation")

    st.info(
        "Snapshots created in the hosted app are session-based. "
        "A production version would store screenshots and metadata in "
        "persistent cloud storage/database and run captures on a scheduler "
        "(for example daily or weekly). Some websites may also block automated capture."
    )


st.divider()
st.caption(
    "Portfolio prototype • Python • Streamlit • Selenium • Pillow/ImageHash"
)
