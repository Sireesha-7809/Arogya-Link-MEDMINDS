AROGYA LINK — MEDMINDS | H5 COMPLETE STARTER

This project is a runnable local-first starter covering the structure of all five required outputs. It is not yet a verified final submission because the organizer's private/supplied protocol corpus, test set, pre-cached models and household register must replace the placeholders/sample data.

RUN ON WINDOWS
1. Extract this ZIP.
2. Open the extracted folder in File Explorer.
3. Click the address bar, type cmd, press Enter.
4. Run: py -m pip install -r requirements.txt
5. Run: py -m streamlit run app.py

TESTS
- Add the organiser's escalation set in the expected JSON shape (see tests/escalation_test_template.json), then run:
  py evaluation.py path\to\organizer_escalation_test.json
- Baseline performance:
  py benchmark.py
- Keep evaluation reports for your presentation.

FOLDERS
- app.py: Streamlit interface, role screens, local protocol section retrieval, safety-first checks, local SQLite visit status and sync queue.
- protocols/: put official .txt or .md protocol documents here.
- data/households.csv: 500 synthetic demo households. Replace with the organizer's supplied register before final evaluation.
- data/arogya_link.db: created on first app launch; stores visit completion and pending sync records locally.
- safety_rules.json: configurable keyword rules; must be expanded and tested against every organizer must-escalate question.
- evaluation.py: computes recall/detection and false positives on a supplied test file.
- benchmark.py: measures local retrieval baseline only; it does NOT measure an AI model that is not integrated.
- reports/: save test and benchmark outputs here.

IMPORTANT
- No invented clinical protocols are included. Until official protocol files are added, the assistant refuses to guess and reports no matching protocol.
- Danger-sign keyword rules are a baseline and are NOT guaranteed to detect all 100% of code-mixed or spelling-variant questions. Run evaluation.py against the actual organiser set and improve until no misses remain.
- No pre-cached offline language/embedding model was included in this ZIP. Integrate the model provided by the organisers and measure its real model size, RAM and CPU latency.
- The current language UI contains Telugu and English labels; the sidebar lists all eight choices, but other interface translations fall back to English until reviewed. Do not claim all eight UI translations are complete in this starter.
- Do not enter real patient-identifying data.
- Student prototype only; not a medical device. Validate translations and safety behavior with qualified reviewers.
