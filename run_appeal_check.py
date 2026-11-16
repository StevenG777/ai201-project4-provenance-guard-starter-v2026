#!/usr/bin/env python3
"""
Criterion 4: an appeal always changes status and is always recorded.

    python run_appeal_check.py --label before

run_eval.py only sends /submit, so the appeal path is tested here. Each trial:
  Appeal 1: submit a text, appeal its content_id with reasoning. Expect 200,
            status "under_review", and an "appeal" event in GET /log.
  Appeal 2: appeal a content_id that does not exist. Expect a 4xx error with an
            "error" field, and NO log entry for that content_id.
Writes results/appeal_<label>_<date>.md with the real responses.
"""
import argparse
import datetime as dt
import json
from pathlib import Path

import requests

import config

TEXT = ("Today is a very good day and I am happy. I went for a long walk after "
        "lunch and the weather was lovely.")
FAKE_ID = "00000000-0000-0000-0000-000000000000"


def log_entries(url, content_id):
    entries = requests.get(f"{url}/log", timeout=10).json()
    if isinstance(entries, dict):
        entries = entries.get("entries", [])
    return [e for e in entries if e.get("content_id") == content_id]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=3)
    ap.add_argument("--label", default="")
    ap.add_argument("--url", default=f"http://{config.HOST}:{config.PORT}")
    args = ap.parse_args()

    out, passed = [], []
    for t in range(1, args.trials + 1):
        sub = requests.post(f"{args.url}/submit",
                            json={"text": TEXT, "creator_id": f"eval_appeal_{t}"}, timeout=90)
        cid = sub.json().get("content_id")
        ap1 = requests.post(f"{args.url}/appeal",
                            json={"content_id": cid, "reasoning": "I wrote this myself."}, timeout=10)
        body1 = ap1.json()
        events = [e.get("event") for e in log_entries(args.url, cid)]
        ok1 = (ap1.status_code == 200 and body1.get("status") == "under_review"
               and "appeal" in events)

        ap2 = requests.post(f"{args.url}/appeal",
                            json={"content_id": FAKE_ID, "reasoning": "Testing an unknown id."}, timeout=10)
        body2 = ap2.json()
        ok2 = (400 <= ap2.status_code < 500 and "error" in body2
               and not log_entries(args.url, FAKE_ID))

        passed.append((ok1, ok2))
        print(f"trial {t}: valid appeal {'OK' if ok1 else 'FAIL'} | unknown id {'OK' if ok2 else 'FAIL'}")
        out.append({"trial": t,
                    "valid_appeal": {"status": ap1.status_code, "response": body1,
                                     "log_events_for_content_id": events, "ok": ok1},
                    "unknown_id": {"status": ap2.status_code, "response": body2,
                                   "log_entries_for_fake_id": len(log_entries(args.url, FAKE_ID)),
                                   "ok": ok2}})

    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    path = Path("results") / f"appeal_{args.label or 'run'}_{stamp}.md"
    path.parent.mkdir(exist_ok=True)
    lines = ["# Criterion 4: appeal path", "",
             f"- Produced by: `run_appeal_check.py::main` · {args.trials} trials", "",
             "| Trial | Valid appeal | Unknown id |", "|---|---|---|"]
    for t, (a, b) in enumerate(passed, 1):
        lines.append(f"| {t} | {'OK' if a else 'FAIL'} | {'OK' if b else 'FAIL'} |")
    lines += ["", "```json", json.dumps(out, indent=2), "```", ""]
    path.write_text("\n".join(lines))
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
