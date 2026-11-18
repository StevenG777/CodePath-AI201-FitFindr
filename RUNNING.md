# Running FitFindr (capstone, Path B: local with logs)

**Needs:** Python 3.11, 3.12 or 3.13 (not 3.14); a Gemini API key. No local model files (the model is called over the API). Dependencies are pinned in `requirements.txt`.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # paste your GEMINI_API_KEY into .env
python test.py                  # should end "10 passed"
AI201_CACHE=0 python serve.py   # the one start command; listens on :5000
```

Ask it (single quotes, so `$30` isn't expanded by the shell):

```bash
curl -X POST http://localhost:5000/ask -H 'Content-Type: application/json' \
  -d '{"query": "vintage graphic tee under $30"}'
curl http://localhost:5000/health
```

Every `/ask` request appends one JSON line to `logs/requests.jsonl`. `AI201_CACHE=0` turns the response cache off so each run is a real model call.

Not yet tested from a clean clone (see README, What's Still Broken).
