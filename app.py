from __future__ import annotations

from pathlib import Path

import streamlit as st

from timecapsule.analysis import SnapshotFingerprint, classify_change, html_similarity, visual_change_score
from timecapsule.capture import capture_website
from timecapsule.storage import SnapshotStore


APP_TITLE = "Time Capsule Internet"
DB_PATH = Path("data/time_capsule.db")

st.set_page_config(page_title=APP_TITLE, page_icon="⏳", layout="wide")
st.title("⏳ Time Capsule Internet")
st.caption("Persistent website-history tracking with browser automation, perceptual image hashing, and explainable change metrics.")

store = SnapshotStore(DB_PATH)

capture_tab, history_tab, methods_tab = st.tabs(["🌐 Capture", "🕰️ History", "🧪 Methodology"])

with capture_tab:
    st.subheader("Capture a public website")
    url = st.text_input("Website URL", value="https://example.com")
    if st.button("Capture snapshot", type="primary"):
        try:
            with st.spinner("Opening website and calculating fingerprints..."):
                snapshot = capture_website(url)
                snapshot_id = store.add(snapshot)
            st.success(f"Saved persistent snapshot #{snapshot_id} for {snapshot['site_key']}.")
            st.image(snapshot["png"], caption=snapshot["timestamp"], use_container_width=True)
        except Exception as exc:
            st.error("Capture failed. Some websites block automated browsers, require login/CAPTCHA, or time out.")
            st.code(str(exc))

    st.info(
        "For repeated monitoring, run `python monitor.py <url> --hours 24`. "
        "The scheduler stores snapshots in the same SQLite database."
    )

with history_tab:
    sites = store.list_sites()
    if not sites:
        st.info("No persistent snapshots yet. Capture a website first.")
    else:
        site = st.selectbox("Tracked website", sites)
        items = store.list_snapshots(site)
        st.write(f"**{len(items)} snapshot(s)** stored persistently for `{site}`")

        index = 0 if len(items) == 1 else st.slider("Timeline", 0, len(items) - 1, len(items) - 1)
        current = items[index]
        st.markdown(f"### {current.title}")
        st.caption(f"Captured {current.captured_at} · {current.final_url}")
        st.image(current.png, use_container_width=True)

        if len(items) >= 2:
            before_index = max(0, index - 1)
            before = items[before_index]
            a = SnapshotFingerprint(before.phash, before.html_hash, before.html_length)
            b = SnapshotFingerprint(current.phash, current.html_hash, current.html_length)
            score = visual_change_score(a, b)
            similarity = html_similarity(a, b)

            c1, c2, c3 = st.columns(3)
            c1.metric("Visual change", f"{score}%")
            c2.metric("Change class", classify_change(score).title())
            c3.metric("HTML-size similarity", f"{similarity}%")

            left, right = st.columns(2)
            with left:
                st.caption(f"BEFORE — {before.captured_at}")
                st.image(before.png, use_container_width=True)
            with right:
                st.caption(f"AFTER — {current.captured_at}")
                st.image(current.png, use_container_width=True)

        if st.button("Delete all snapshots for this site"):
            deleted = store.delete_site(site)
            st.success(f"Deleted {deleted} snapshot(s).")
            st.rerun()

with methods_tab:
    st.subheader("How the prototype works")
    st.markdown(
        """
1. **Browser automation:** Selenium opens the requested public page in headless Chromium.
2. **Security validation:** localhost, private, link-local, multicast, reserved, and unspecified IP ranges are blocked.
3. **Visual fingerprint:** each screenshot is converted to a perceptual hash (`pHash`).
4. **Content fingerprint:** page HTML is hashed with SHA-256 and its length is recorded as a lightweight secondary signal.
5. **Persistent storage:** screenshots and metadata are stored in SQLite, allowing the history to survive Streamlit sessions.
6. **Explainable comparison:** perceptual-hash distance is normalized to a percentage and mapped to minimal/small/moderate/large change classes.
7. **Scheduling:** an APScheduler worker can perform repeated captures locally or on a long-running host.
        """
    )
    st.warning(
        "This is a portfolio prototype, not a production crawler. A production system would add distributed scheduling, "
        "object storage, retries, robots-policy handling, authentication controls, and stronger content-diff algorithms."
    )
