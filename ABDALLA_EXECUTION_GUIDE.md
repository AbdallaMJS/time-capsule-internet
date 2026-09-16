# Abdalla Execution Guide — Time Capsule Internet

This file is a **student execution guide**, not evidence that the work has already been completed. The branch was prepared with AI-assisted development support. Abdalla should personally run the steps, inspect the output, make any final decisions, and complete `PROJECT_JOURNAL.md` in his own words.

## Goal
Reproduce the application locally and validate that its browser automation, persistence, visual-change metric, and safety checks behave as documented.

## 1. Work on the execution branch
```bash
git clone https://github.com/AbdallaMJS/time-capsule-internet.git
cd time-capsule-internet
git checkout abdalla-execution
```

## 2. Create a clean environment and install
macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Windows PowerShell:
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Run the test suite
```bash
pytest -q
```
Save the terminal result. If anything fails, do not hide it; record the failure in the journal before fixing it.

## 4. Launch the application
```bash
python -m streamlit run app.py
```
Walk through the interface and use only controlled, clearly public test pages such as `https://example.com` during initial validation. Avoid arbitrary internal/private URLs.

Verify that Abdalla can explain:
- what Selenium does;
- where screenshot metadata is stored;
- why pHash is used for visual similarity;
- why SHA-256 serves a different purpose;
- how the timeline/before-after comparison works.

## 5. Build a small visual-change calibration set
Create a small set of known before/after screenshots or controlled page versions representing:
- almost no visible change;
- small text/layout change;
- moderate change;
- large change.

Record the resulting score/label and Abdalla's own visual judgment. The objective is not to force agreement; mismatches are useful evidence for discussing limitations.

Suggested evidence file: `results/change_calibration.md`.

## 6. Review the security boundary
Read the hostname/IP validation code and explain in the journal:
- which private/local address types are blocked;
- why a DNS check before navigation is useful;
- why it is not complete SSRF protection, especially around redirects/DNS changes;
- why a public deployment would need a stricter policy.

Do not claim the project is production-secure.

## 7. Final student-owned evidence
After the real run, Abdalla should personally add or approve:
- completed `PROJECT_JOURNAL.md` entries;
- `results/change_calibration.md` with genuine observations;
- one screenshot of the working application if useful;
- any correction he personally decided to make after testing.

Suggested final student commit:
```text
Document reproduced Time Capsule behavior and calibration findings
```

## Interview check
Abdalla should be able to answer without reading notes:
1. Why use perceptual hashing instead of only SHA-256?
2. What causes false-positive visual changes?
3. What does SQLite add to the architecture?
4. What security risk exists when a server fetches user-provided URLs?
5. What would you change before deploying this publicly?
