# Running FitFindr (capstone, Path B: local with logs)

**Prerequisite:** 
- Python 3.11, 3.12 or 3.13 (not 3.14)
- A Gemini API key. 
- No local model files (the model is called over the API). 
- Dependencies are pinned in `requirements.txt`.

---

**How to Set Up Environment:**
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # paste your GEMINI_API_KEY into .env
python test.py                  # should end "10 passed"
```

---

**How to Run the App:**
```bash
AI201_CACHE=0 \
PORT=5001 \
python serve.py   # the one start command; listens on :5001
```

NOTE: 
- I switched from PORT 5000 instead of 5001 because the Macbook Airplay is occupying PORT 5000.

---

**How to Use the App:**

1. Check Server's Health
```bash
curl http://localhost:5001/health
```

2. Ask for Clothes Fit

NOTE:
- Ask it (single quotes, so `$30` isn't expanded by the shell)
- Every `/ask` request appends one JSON line to `logs/requests.jsonl`.
- `AI201_CACHE=0` turns the response cache off so each run is a real model call.

```bash
curl -X POST http://localhost:5001/ask \
  -H 'Content-Type: application/json' \
  -d '{"query": "vintage graphic tee under $30"}'
```

---

**How to Run the Logging Visualizer App:**

```bash
streamlit run log_viewer.py
```