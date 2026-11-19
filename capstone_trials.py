"""
Capstone trial runner: runs the five criteria in criteria.md, three trials each.

    python capstone_trials.py before     # writes results/capstone_before.json
    python capstone_trials.py after      # writes results/capstone_after.json

It starts its own copies of serve.py (cache off), so it needs nothing running:
  A  port 5101  normal
  B  port 5102  GEMINI_API_KEY deliberately invalid (to trigger `crashed`)
  C  port 5103  `ulimit -f 1` so every log write fails (criterion 5)
Every request is real HTTP; every check reads logs/requests.jsonl back.
"""
import json
import os
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
LOG = ROOT / "logs" / "requests.jsonl"
TAG = sys.argv[1] if len(sys.argv) > 1 else "before"
X_MS = 4533  # criterion 4 limit, fixed in criteria.md before any trials

BASE_FIELDS = {"ts", "id", "query", "http_status", "outcome", "error", "output",
               "duration_ms", "model_calls", "tokens", "waited_ms"}
FULL_FIELDS = BASE_FIELDS | {"found_item"}
QUERIES_10 = [
    "vintage graphic tee under $30", "black boots under $70", "denim jacket size M",
    "floral summer dress under $40", "leather belt", "sneakers size 9",
    "corduroy pants", "silk scarf", "levi's jeans", "bomber jacket",
]
JSON_H = {"Content-Type": "application/json"}


def lines():
    return LOG.read_text(encoding="utf-8").splitlines() if LOG.exists() else []


def send(port, method, path, body=None, headers=None):
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", method=method,
                                 data=body, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def ask(port, query):
    return send(port, "POST", "/ask", json.dumps({"query": query}).encode(), JSON_H)


def new_records(before_n):
    return [json.loads(l) for l in lines()[before_n:]]


def start(port, env_extra=None, wrapper=""):
    env = dict(os.environ, AI201_CACHE="0", PORT=str(port), **(env_extra or {}))
    # stderr goes through a pipe, not a file: `ulimit -f` caps regular files only,
    # and a capped stderr file would break the server for reasons unrelated to the log.
    p = subprocess.Popen(["bash", "-c", f"{wrapper} exec {sys.executable} serve.py"],
                         cwd=ROOT, env=env, stdout=subprocess.DEVNULL,
                         stderr=subprocess.PIPE, text=True)
    buf = []
    threading.Thread(target=lambda: [buf.append(l) for l in p.stderr], daemon=True).start()
    for _ in range(60):
        try:
            if send(port, "GET", "/health")[0] == 200:
                return p, buf
        except Exception:
            time.sleep(0.5)
    raise RuntimeError(f"server on {port} did not start")


def crit1(a):
    cases = [("GET", "/nope", None, None, 404), ("GET", "/ask", None, None, 405),
             ("POST", "/ask", b"{}", JSON_H, 400)]
    ok, detail = 0, []
    for m, path, body, h, status in cases:
        n = len(lines())
        got, _ = send(a, m, path, body, h)
        recs = new_records(n)
        good = (len(recs) == 1 and recs[0]["outcome"] == "rejected"
                and recs[0]["http_status"] == status)
        ok += good
        detail.append({"case": f"{m} {path}", "response": got, "new_lines": len(recs),
                       "record": recs[0] if recs else None, "pass": good})
    return ok, 3, detail


def four_outcomes(a, b):
    out = {}
    for name, port, q in [("rejected", a, None), ("crashed", b, "leather belt"),
                          ("stopped", a, "wool sweater size L under $50"),
                          ("completed", a, "leather belt")]:
        n = len(lines())
        if q is None:
            send(port, "POST", "/ask", b"{}", JSON_H)
        else:
            ask(port, q)
        recs = new_records(n)
        out[name] = recs[0] if len(recs) == 1 else {"_new_lines": len(recs)}
    return out


def crit2(rec):
    ok, detail = 0, []
    for name, r in rec.items():
        want = FULL_FIELDS if name in ("stopped", "completed") else BASE_FIELDS
        got = set(r) if "ts" in r else set()
        good = got == want and r.get("outcome") == name
        ok += good
        detail.append({"outcome": name, "got_outcome": r.get("outcome"),
                       "missing": sorted(want - got), "extra": sorted(got - want), "pass": good})
    return ok, 4, detail


def crit3(rec):
    want = {"rejected": (400, 0), "crashed": (500, None), "stopped": (200, 0),
            "completed": (200, 2)}
    ok, detail = 0, []
    for name, (status, calls) in want.items():
        r = rec[name]
        good = (r.get("http_status") == status and r.get("outcome") == name
                and (calls is None or r.get("model_calls") == calls))
        ok += good
        detail.append({"outcome": name, "http_status": r.get("http_status"),
                       "model_calls": r.get("model_calls"), "pass": good})
    return ok, 4, detail


def crit4(a):
    n = len(lines())
    for q in QUERIES_10:
        ask(a, q)
    recs = [r for r in new_records(n)]
    done = [r for r in recs if r["outcome"] == "completed"]
    under = sum(r["duration_ms"] <= X_MS for r in done)
    return under, 10, [{"query": r["query"], "outcome": r["outcome"],
                        "duration_ms": r["duration_ms"], "tokens": r["tokens"]} for r in recs]


def crit5(c, c_err):
    ok, detail = 0, []
    for _ in range(5):
        err_before = "".join(c_err).count("could not write log")
        n = len(lines())
        status, body = ask(c, "wool sweater size L under $50")
        time.sleep(0.2)
        err_after = "".join(c_err).count("could not write log")
        good = status == 200 and "Nothing matched" in body and err_after == err_before + 1
        ok += good
        detail.append({"status": status, "stderr_new": err_after - err_before,
                       "log_lines_added": len(lines()) - n, "pass": good})
    return ok, 5, detail


def main():
    procs = []
    try:
        a, _ = start(5101); procs.append(a)
        b, _ = start(5102, {"GEMINI_API_KEY": "invalid-key-for-test"}); procs.append(b)
        c, c_err = start(5103, wrapper="ulimit -f 1;"); procs.append(c)
        results = {f"c{i}": [] for i in range(1, 6)}
        for trial in range(1, 4):
            print(f"--- trial {trial}", flush=True)
            results["c1"].append(crit1(5101))
            rec = four_outcomes(5101, 5102)
            results["c2"].append(crit2(rec))
            results["c3"].append(crit3(rec))
            results["c4"].append(crit4(5101))
            results["c5"].append(crit5(5103, c_err))
            for k in results:
                print(k, results[k][-1][:2], flush=True)
        (ROOT / "results" / f"capstone_{TAG}.json").write_text(
            json.dumps(results, indent=2, ensure_ascii=False))
    finally:
        for p in procs:
            p.terminate()


if __name__ == "__main__":
    main()
