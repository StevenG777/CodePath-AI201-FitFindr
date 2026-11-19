"""Quick viewer for logs/requests.jsonl.   streamlit run log_viewer.py"""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

LOG = Path(__file__).parent / "logs" / "requests.jsonl"
st.set_page_config(page_title="FitFindr log", layout="wide")
st.title("FitFindr request log")

if not LOG.exists():
    st.warning(f"No log yet at {LOG}")
    st.stop()

rows = [json.loads(l) for l in LOG.read_text(encoding="utf-8").splitlines() if l.strip()]
df = pd.DataFrame(rows)
df["ts"] = pd.to_datetime(df["ts"])

outcomes = st.sidebar.multiselect("Outcome", sorted(df.outcome.unique()), default=list(df.outcome.unique()))
df = df[df.outcome.isin(outcomes)]
done = df[df.outcome == "completed"]

c = st.columns(5)
c[0].metric("Requests", len(df))
c[1].metric("Completed", len(done))
c[2].metric("Median ms (completed)", int(done.duration_ms.median()) if len(done) else 0)
c[3].metric("Max ms", int(df.duration_ms.max()) if len(df) else 0)
c[4].metric("Avg tokens (completed)", int(done.tokens.mean()) if len(done) else 0)

l, r = st.columns(2)
l.subheader("Duration per request (ms)")
l.bar_chart(df.set_index("ts")["duration_ms"])
r.subheader("Outcomes")
r.bar_chart(df.outcome.value_counts())

st.subheader("Requests")
st.dataframe(df[["ts", "outcome", "http_status", "query", "found_item", "duration_ms",
                 "model_calls", "tokens", "error"]], width="stretch")

if df.empty:
    st.info("No records match the filter.")
    st.stop()

by_id = {x["id"]: x for x in rows}
pick = st.selectbox("Inspect a record", df.id.tolist())
st.json(by_id.get(pick, {}))
