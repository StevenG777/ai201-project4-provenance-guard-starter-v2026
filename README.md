# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->

Provenance Guard is a small backend a writing site could plug into. A piece of text goes in; a guess, a score, a plain-English label and a way to appeal come out.

1. **Request arrives.** `POST /submit` with `text` and `creator_id`. `app.py` validates it (missing, empty, too short, too long, not JSON) and creates a `content_id`.
2. **Signal one.** `detector.model_signal` scores how predictable the text is to a local gpt2 model → `model_score`.
3. **Signal two.** `stylometry.style_signal` scores the shape of the text → `style_score`.
4. **Combine.** `scoring.combine_signals` merges them into one `confidence` number (higher = more likely AI).
5. **Label.** `scoring.score_to_label` maps the number to one of three labels using the thresholds in `config.py`.
6. **Log.** `audit.log_decision` records the decision, both signal scores and status `decided`.
7. **Respond.** JSON with `content_id`, `guess`, `confidence`, `label`, `model_score`, `style_score`.

A writer who disagrees calls `POST /appeal` with the `content_id` and their reasoning. The item moves to `under_review` and the appeal is logged.



---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:** the perplexity of the raw text under a local language model (gpt2, in `detector.py`) — how surprised the model is by each next word. Low perplexity means predictable text. It is squashed onto 0–1, higher = more likely AI.

**Why that might differ between human and AI writing:** AI text is produced by picking likely next words, so a language model finds it easy to predict. Human writing has odd word choices, slang, errors and specifics, so it surprises the model more.

**What it can't see:** authorship. It only sees predictability, so plain writing in common words and short sentences (younger writers, second-language writers, anyone writing simply) looks machine-like. Measured: a plain human paragraph about a hometown had perplexity 9.4 and `model_score` 0.92, higher than a stiff AI-style paragraph at 0.79. Ornate human prose with rare words can look human, and ornate AI text can slip through.

### Signal two — the style signal

**What it measures:** the shape of the text, without understanding it (in `stylometry.py`): `sentence_length_spread` (do sentence lengths vary?), `type_token_ratio` (how much vocabulary repeats?) and `punctuation_density` (how much punctuation, weighting semicolons and dashes over full stops). Each is scaled and combined into one 0–1 score, higher = more likely AI.

**Why that might differ between human and AI writing:** AI prose tends toward even, mid-length sentences and a narrower vocabulary. Human writing is lumpier: a three-word sentence next to a forty-word one. Dashes and semicolons are only a weak hint, since humans use them too.

**What it can't see:** meaning. Typos, broken-up sentences or a pasted quotation change the shape without changing who wrote the text. It also only matches `[a-z0-9']+`, so non-Latin text (Chinese, Russian) yields no words and its output is unreliable. Plain human writing with short, even sentences can also look AI-ish to it.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:** a weighted average that leans on the model signal, with two safeguards aimed at false accusations.
1. Score = 0.6 × model_score + 0.4 × style_score. The model signal gets more weight because it measures predictability directly; the style signal only sees shape, and a few dashes or typos can move it.
2. If the signals differ by more than 0.4, the score is pulled halfway to 0.5. Two methods disagreeing is itself uncertainty, so it should land in "unsure", not wherever the average falls.
3. The score cannot enter the AI band unless both signals are at least 0.5. One signal alone never produces an AI label.

**The numbers** (all in `config.py`): `WEIGHT_MODEL_SIGNAL` 0.6, `WEIGHT_STYLE_SIGNAL` 0.4, `DISAGREEMENT_GAP` 0.4, `DISAGREEMENT_PULL` 0.5, `AI_BOTH_SIGNALS_MIN` 0.5; thresholds human ≤ 0.35, AI ≥ 0.65. I did not change the model-signal midpoint (45.0). Style signal: spread (weight 0.5), type-token ratio (0.25), punctuation density (0.25), each scaled to 0–1 AI-likeness in `stylometry.style_signal`.

**Calibration run** (both signals printed separately; higher = more likely AI):

| input | perplexity | model | style | combined | label |
|---|---|---|---|---|---|
| clearly AI | 16.1 | 0.84 | 0.41 | 0.58 | unsure |
| clearly human | 113.0 | 0.19 | 0.02 | 0.12 | human |
| formal human (Declaration of Independence opening) | 29.5 | 0.66 | 0.79 | 0.71 | **ai** |
| plain human (grandmother paragraph) | 13.9 | 0.87 | 0.70 | 0.80 | **ai** |
| lightly-edited AI | 30.5 | 0.65 | 0.14 | 0.47 | unsure |

**Where they agree:** the clearly human text (both low) and both false positives (both high).

**Where they disagree:** the clearly-AI text (model 0.84, style 0.41) and the lightly-edited AI (model 0.65, style 0.14).

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:**

The lightly-edited AI paragraph. Signal one says 0.65 because the words are still predictable. Signal two says 0.14, because casual edits ("honestly", "yeah", dashes, a lowercase "i") made the sentence lengths uneven and added punctuation. The signals differ by 0.51, which is over the 0.4 gap, so the rule pulls the 0.43 average toward 0.5 and the result is 0.47, "unsure". An AI paragraph gets through unflagged, which is the trade I chose: not accusing anyone costs less than missing one.

**What my calibration did not fix:** both false positives. The plain human paragraph (0.80) and the formal human text (0.71) are labelled AI because both signals agree, so the disagreement rule and the both-signals rule cannot help. The formal text is one very long sentence, so spread is 0 and reads as "uniform"; it is also a famous text, so gpt2 has probably seen it, which lowers perplexity. It is a poor test of formal writing and I should add a second formal sample. The clearly-AI paragraph only reaches "unsure" (0.58) because its sentence lengths vary more than my spread cutoff expects.

---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | 0.00 – 0.35 | We think this was probably written by a person. |
| unsure | 0.35 – 0.65 | We can't tell whether this was written by a person or with AI, so we haven't made a call. Nothing is wrong with your work. If you'd like someone to look at it, you can appeal. |
| high-confidence AI | 0.65 – 1.00 | Our tools think this was probably written with the help of AI. They can be wrong, especially with plain, simple writing. If you wrote it yourself, you can appeal and a person will take a look. |

**Why I worded the "unsure" one this way:**

It says "we haven't made a call" instead of hinting at a verdict, and says outright that nothing is wrong with the work, because most people who see it will have written every word themselves. It names the appeal as an option, not a next step they must take. The AI label also admits the tool can be wrong and names the case it is worst at (plain, simple writing), because that is the false positive I traced in DESIGN.md.



---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission** (Milestone 3: only signal one is wired in, so `guess`, `confidence`, `style_score` and the label are placeholders)

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "My grandmother grew up on a farm in Ohio. She woke up early every day to feed the animals. After breakfast she helped her mother clean the house. In the evening the family ate dinner together.", "creator_id": "writer_01"}'
```

```json
{
  "confidence": null,
  "content_id": "1c37ba5c-e991-4055-82a2-8ecf61ada26f",
  "guess": null,
  "label": "PLACEHOLDER — not scored yet.",
  "model_score": 0.8531,
  "style_score": null
}
```

A bad request (no `text`) is refused and the refusal is logged:

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"creator_id": "writer_01"}'
```

```json
{
  "error": "invalid_text",
  "message": "The text content must be a str object."
}
```

**An appeal**

I appealed a plain human paragraph about a grandmother that the system labelled AI (score 0.7999).

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "da0d5511-c7b8-47d8-bc72-a503c62e3b1a", "reasoning": "I wrote this myself about my grandmother. I write in short, simple sentences."}'
```

```json
{
  "content_id": "da0d5511-c7b8-47d8-bc72-a503c62e3b1a",
  "message": "Thanks — your appeal was recorded and a person will review it.",
  "status": "under_review"
}
```

An unknown id returns 404 `unknown_content_id`, a missing `reasoning` returns 400 `missing_reasoning`, and a non-JSON body returns 400 `invalid_json`.

**What the log shows afterwards**

The original decision and the appeal sit side by side for the same `content_id`. The log is append-only, so the decision is never overwritten; the appeal entry carries the new status.

```json
{
  "combined_score": 0.7999,
  "content_id": "da0d5511-c7b8-47d8-bc72-a503c62e3b1a",
  "creator_id": "w",
  "guess": "ai",
  "label": "Our tools think this was probably written with the help of AI. They can be wrong, especially with plain, simple writing. If you wrote it yourself, you can appeal and a person will take a look.",
  "model_score": 0.8679,
  "status": "decided",
  "style_score": 0.6979,
  "timestamp": "2026-11-09T03:56:07+00:00"
}
{
  "content_id": "da0d5511-c7b8-47d8-bc72-a503c62e3b1a",
  "creator_id": "w",
  "event": "appeal",
  "reasoning": "I wrote this myself about my grandmother. I write in short, simple sentences.",
  "status": "under_review",
  "timestamp": "2026-11-09T03:59:08+00:00"
}
```

---

## How I Used AI

**Moment 1: checking my `/submit` validation**

- *What I asked for:* curl and Python requests to test the normal and error cases of my `/submit` route.
- *What came back:* the test requests, plus two problems it found in my handler. The `missing_text` branch could never run, because the check above it already rejected empty text. And a missing `creator_id` returned the error code `"invalid creator_id"` with a space, unlike every other code.
- *What I changed:* I split the type check from the empty check so `missing_text` is reachable, and I used the requests to confirm each error returns the status code I expected (400, 413). The `"invalid creator_id"` code is still inconsistent and I have not fixed it.

**Moment 2: building the style signal and combining rule**

- *What I asked for:* the second signal in `stylometry.py` and the combining rule in `scoring.py`, then to run my calibration inputs through both signals and print them separately.
- *What came back:* three scaled measures (sentence-length spread, type-token ratio, punctuation density), a 0.6/0.4 weighted average, a rule that pulls the score toward 0.5 when the signals disagree, and a rule that blocks the AI label unless both signals lean AI. The calibration table showed that both rules fail on exactly my false-positive case: a plain human paragraph scored 0.80 because both signals read short even sentences as AI. It also showed the clearly-AI paragraph only reaching "unsure" (0.58).
- *What I changed:* nothing in the numbers yet. I kept the weights and thresholds, and wrote the plain-human false positive and the weak style score into the README as unresolved findings, because tuning the cutoffs to those four inputs would only fit the sample.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:**  5 per minute, 40 per day

**Why those numbers and not others:**

A real writer submits their own work a few times an hour. Even a heavy session (paste a draft, read the label, edit, resubmit) is rarely more than a handful of submissions in a minute, so 5 per minute never gets in their way. 40 per day covers a full day of drafting and appeals with room to spare.

A script mapping my thresholds needs hundreds of probes with small variations. At 5 per minute and 40 per day it gets 40 data points a day from one identity, which is too few to map the 0.35 / 0.65 boundaries. I did not go lower because a writer who hits a limit while legitimately revising would be locked out of their own appeal path. I did not go higher because the starter's 10/min and 200/day would still let a script collect 200 probes a day.

**What a caller counts as:** the `creator_id` in the request body, falling back to the caller's IP address when `creator_id` is missing or not a string (`rate_limit_key` in `app.py`).

- Keying on `creator_id` means one household or office sharing an IP does not share a quota.
- The weaknesses are:
     - `creator_id` is self-reported. A script can rotate IDs to dodge the limit, and each fresh ID gets a fresh quota. 
     - Keying on IP alone fails the other way: one script is one caller, but one household is also one caller.
     - Storage is in-memory, so a restart forgets every count.

**The run of status codes when I pushed past it:**

`python run_attacks.py --flood 15` (15 submissions from one `creator_id`; saved to `results/flood_2026-11-15_1844.md`):

```
200 200 200 200 200 429 429 429 429 429 429 429 429 429 429
```

The first 5 pass, the remaining 10 are rejected with 429, and each rejection is written to `logs/audit.jsonl`.

---

## Attack Run — Before

56 attacks (`attack_set/attacks.csv` and `attack_set/attacks_malformed_requests.csv`), run once with `python run_attacks.py --set attack_set` before any change from this unit beyond the limiter (5/min, 40/day). Full output: `results/attack_run_2026-11-15_1042.md`.

**How I marked held or broke.** The only accusation my service makes is the AI label, so I judged each family against that:
- *evasion*: the text is AI-written. HELD only if it came back labelled AI. "Unsure" counts as BROKE, because the AI text got past the detector.
- *false_positive*: the text is human-written. BROKE if it came back labelled AI (a real writer accused). "Unsure" or "human" is HELD.
- *prompt_injection*: HELD if the instruction in the text did not get what it asked for. BROKE if it did.
- *malformed*: HELD if the service rejected it cleanly or handled it without a crash and without a confident wrong answer. A 500, or a confident AI label on something that isn't writing, is BROKE.
- *flood_same_creator*: HELD if the limiter let the first requests through and then returned 429.

| Family | Held | Broke |
|---|---|---|
| evasion | 1 | 9 |
| false_positive | 4 | 4 |
| prompt_injection | 5 | 1 |
| malformed | 17 | 3 |
| flood_same_creator | 12 | 0 |
| **Total** | **39** | **17** |

| ID | Family | Status | Guess | Score | Mark | Note |
|---|---|---|---|---|---|---|
| EV01 | evasion | 200 | unsure | 0.412 | BROKE | AI text + typos; signal one scored it 0.16 (human-leaning) |
| EV02 | evasion | 200 | unsure | 0.441 | BROKE |  |
| EV03 | evasion | 200 | unsure | 0.521 | BROKE |  |
| EV04 | evasion | 200 | unsure | 0.579 | BROKE |  |
| EV05 | evasion | 200 | human | 0.262 | BROKE | heavily edited AI text called human |
| EV06 | evasion | 200 | unsure | 0.464 | BROKE |  |
| EV07 | evasion | 200 | unsure | 0.577 | BROKE |  |
| EV08 | evasion | 200 | unsure | 0.366 | BROKE |  |
| EV09 | evasion | 200 | unsure | 0.556 | BROKE |  |
| EV10 | evasion | 200 | ai | 0.875 | HELD | labelled AI (0.875) |
| FP01 | false_positive | 200 | unsure | 0.587 | HELD | not accused, but 0.587 is close to the line |
| FP02 | false_positive | 200 | ai | 0.721 | BROKE | real human writing accused of AI |
| FP03 | false_positive | 200 | ai | 0.732 | BROKE | real human writing accused of AI |
| FP04 | false_positive | 200 | ai | 0.709 | BROKE | real human writing accused of AI |
| FP05 | false_positive | 200 | ai | 0.781 | BROKE | real human writing accused of AI |
| FP06 | false_positive | 200 | unsure | 0.610 | HELD |  |
| FP07 | false_positive | 200 | unsure | 0.608 | HELD |  |
| FP08 | false_positive | 200 | unsure | 0.370 | HELD |  |
| PI01 | prompt_injection | 200 | unsure | 0.388 | HELD | instruction ignored; unsure |
| PI02 | prompt_injection | 200 | human | 0.212 | BROKE | AI text asked for 'human' and got 'human' (0.212) |
| PI03 | prompt_injection | 200 | unsure | 0.524 | HELD | instruction ignored; unsure |
| PI04 | prompt_injection | 200 | unsure | 0.428 | HELD | label is a fixed string, nothing echoed |
| PI05 | prompt_injection | 200 | unsure | 0.475 | HELD | log line stayed one clean entry |
| PI06 | prompt_injection | 200 | unsure | 0.555 | HELD | instruction ignored |
| MF01 | malformed | 400 | — | — | HELD | 400 |
| MF02 | malformed | 400 | — | — | HELD | 400 |
| MF03 | malformed | 200 | unsure | 0.400 | HELD | no crash, but control characters were scored instead of rejected |
| MF04 | malformed | 200 | unsure | 0.453 | HELD | no crash, but punctuation-only was scored instead of rejected |
| MF05 | malformed | 200 | ai | 0.899 | BROKE | one repeated letter labelled AI (0.899) |
| MF06 | malformed | 200 | ai | 0.998 | BROKE | emoji-only labelled AI (0.998) |
| MF07 | malformed | 200 | ai | 0.944 | BROKE | Arabic text labelled AI (0.944) |
| MF08 | malformed | 413 | — | — | HELD | 413 |
| RQ01 | malformed | 400 | — | — | HELD | 400 |
| RQ02 | malformed | 400 | — | — | HELD | 400 |
| RQ03 | malformed | 400 | — | — | HELD | 400 |
| RQ04 | malformed | 400 | — | — | HELD | 400 |
| RQ05 | malformed | 400 | — | — | HELD | 400 |
| RQ06 | malformed | 400 | — | — | HELD | 400 |
| RQ07 | malformed | 400 | — | — | HELD | 400 |
| RQ08 | malformed | 400 | — | — | HELD | 400 |
| RQ09 | malformed | 400 | — | — | HELD | 400 |
| RQ10 | malformed | 429 | — | — | HELD | 429, never reached my route (no usable creator_id, so counted against my IP) |
| RQ11 | malformed | 429 | — | — | HELD | 429, never reached my route (no usable creator_id, so counted against my IP) |
| RQ12 | malformed | 400 | — | — | HELD | 400 |
| FL01_01 | flood_same_creator | 200 | unsure | 0.409 | HELD | allowed |
| FL01_02 | flood_same_creator | 200 | unsure | 0.409 | HELD | allowed |
| FL01_03 | flood_same_creator | 200 | unsure | 0.409 | HELD | allowed |
| FL01_04 | flood_same_creator | 200 | unsure | 0.409 | HELD | allowed |
| FL01_05 | flood_same_creator | 200 | unsure | 0.409 | HELD | allowed |
| FL01_06 | flood_same_creator | 429 | — | — | HELD | 429 |
| FL01_07 | flood_same_creator | 429 | — | — | HELD | 429 |
| FL01_08 | flood_same_creator | 429 | — | — | HELD | 429 |
| FL01_09 | flood_same_creator | 429 | — | — | HELD | 429 |
| FL01_10 | flood_same_creator | 429 | — | — | HELD | 429 |
| FL01_11 | flood_same_creator | 429 | — | — | HELD | 429 |
| FL01_12 | flood_same_creator | 429 | — | — | HELD | 429 |

**Ten audit log entries from this run** (from `logs/audit.jsonl`; the last two are rejected requests, which carry fewer fields):

```json
{"timestamp": "2026-11-15T18:41:57+00:00", "content_id": "254e4316-49ec-48e0-9697-d4bdc9b57f19", "creator_id": "attacker_EV01", "guess": "unsure", "model_score": 0.1635, "style_score": 0.5675, "combined_score": 0.4125, "label": "We can't tell whether this was written by a person or with AI, so we haven't made a call. Nothing is wrong with your work. If you'd like someone to look at it, you can appeal.", "status": "decided"}

{"timestamp": "2026-11-15T18:41:58+00:00", "content_id": "6db04892-dbd8-4dd8-a8bd-e13e39dc3f20", "creator_id": "attacker_EV05", "guess": "human", "model_score": 0.3212, "style_score": 0.1723, "combined_score": 0.2616, "label": "We think this was probably written by a person.", "status": "decided"}

{"timestamp": "2026-11-15T18:41:59+00:00", "content_id": "67fe0420-1dae-4de9-b825-8f569f1f0b0c", "creator_id": "attacker_PI02", "guess": "human", "model_score": 0.2044, "style_score": 0.2233, "combined_score": 0.212, "label": "We think this was probably written by a person.", "status": "decided"}

{"timestamp": "2026-11-15T18:41:58+00:00", "content_id": "9b3839a3-aab7-4397-aa99-97ab147f8f5a", "creator_id": "attacker_FP02", "guess": "ai", "model_score": 0.7387, "style_score": 0.6946, "combined_score": 0.7211, "label": "Our tools think this was probably written with the help of AI. They can be wrong, especially with plain, simple writing. If you wrote it yourself, you can appeal and a person will take a look.", "status": "decided"}

{"timestamp": "2026-11-15T18:41:59+00:00", "content_id": "dd655b36-3e4b-4c3d-a3f5-81b4d3e93b3f", "creator_id": "attacker_FP05", "guess": "ai", "model_score": 0.8005, "style_score": 0.751, "combined_score": 0.7807, "label": "Our tools think this was probably written with the help of AI. They can be wrong, especially with plain, simple writing. If you wrote it yourself, you can appeal and a person will take a look.", "status": "decided"}

{"timestamp": "2026-11-15T18:41:58+00:00", "content_id": "6fb3a6f2-036b-4934-9a82-6e2c9f702808", "creator_id": "attacker_FP03", "guess": "ai", "model_score": 0.8051, "style_score": 0.6215, "combined_score": 0.7317, "label": "Our tools think this was probably written with the help of AI. They can be wrong, especially with plain, simple writing. If you wrote it yourself, you can appeal and a person will take a look.", "status": "decided"}

{"timestamp": "2026-11-15T18:41:59+00:00", "content_id": "39987804-1dc9-48fd-8dac-2e602317ab36", "creator_id": "attacker_MF05", "guess": "ai", "model_score": 0.9976, "style_score": 0.75, "combined_score": 0.8986, "label": "Our tools think this was probably written with the help of AI. They can be wrong, especially with plain, simple writing. If you wrote it yourself, you can appeal and a person will take a look.", "status": "decided"}

{"timestamp": "2026-11-15T18:42:00+00:00", "content_id": "a6acb607-e0d2-4667-b5fb-4a16b9225f59", "creator_id": "attacker_MF06", "guess": "ai", "model_score": 0.9969, "style_score": 1.0, "combined_score": 0.9981, "label": "Our tools think this was probably written with the help of AI. They can be wrong, especially with plain, simple writing. If you wrote it yourself, you can appeal and a person will take a look.", "status": "decided"}

{"timestamp": "2026-11-15T18:42:00+00:00", "content_id": "f7a6d78f-047c-4139-8818-aa3802ec4f58", "creator_id": "attacker_MF07", "guess": "ai", "model_score": 0.9064, "style_score": 1.0, "combined_score": 0.9438, "label": "Our tools think this was probably written with the help of AI. They can be wrong, especially with plain, simple writing. If you wrote it yourself, you can appeal and a person will take a look.", "status": "decided"}

{"timestamp": "2026-11-15T18:41:59+00:00", "creator_id": "attacker_MF01", "event": "rejected", "status": "rejected", "reason": "missing_text"}

{"timestamp": "2026-11-15T18:42:00+00:00", "creator_id": "attacker_flood", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute"}
```

**Worst outcome: FP05.** A person's technical documentation ("To configure the service, edit the settings file...") came back labelled AI at a combined score of 0.78, with model_score 0.80 and style_score 0.75. Both signals leaned AI. Plain, instructional writing is exactly what a real writer produces, and this writer would be told AI probably wrote their own work.

---

## Run Log and Verdicts

`python run_eval.py --label before` (criteria 1, 2, 3, 5) and `python run_appeal_check.py --label before` (criterion 4, because `run_eval.py` only sends `/submit`). Three trials each, nothing changed in between. Files: `results/run_2026-11-15_2123_before.md`, `results/appeal_before_2026-11-15_2122.md`. Inputs are in `scenarios.py`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. My own writing flagged as AI | at most 2 of 10 labelled `ai` | 2/10 | 2/10 | 2/10 | MET (at the limit) |
| 2. Score spread | lowest AI confidence above highest human confidence | lowest AI 0.576, highest human 0.816 | same | same | MISSED |
| 3. All three labels reachable | each label at least 5 of 20 | human 0, unsure 14, ai 6 | same | same | MISSED |
| 4. Appeal always changes status and is logged | 2 of 2 | 2/2 | 2/2 | 2/2 | MET |
| 5. Empty or missing text returns 400, never a label or 500 | 3 of 3 | 3/3 | 3/3 | 3/3 | MET |

All three trials were identical for every criterion. That is expected: neither signal is random.

**Real output from one trial** (trial 1), pasted as text.

*Criterion 1.* From `run_eval.py::main`, scenario "my own writing". I removed the long `label` string from each entry to keep it readable; every other field is as returned.

```json
[
 {
  "status": 200,
  "guess": "ai",
  "confidence": 0.8163,
  "model_score": 0.8605,
  "style_score": 0.75,
  "sent": "Today is a very good day and I am happy"
 },
 {
  "status": 200,
  "guess": "unsure",
  "confidence": 0.3953,
  "model_score": 0.1178,
  "style_score": 0.55,
  "sent": "Despite work it not busy, I still feel like my energy was drained by c"
 },
 {
  "status": 200,
  "guess": "unsure",
  "confidence": 0.4601,
  "model_score": 0.2548,
  "style_score": 0.6684,
  "sent": "If gradient descent is part of math optimization, dynamic programming "
 },
 {
  "status": 200,
  "guess": "unsure",
  "confidence": 0.5797,
  "model_score": 0.5636,
  "style_score": 0.6038,
  "sent": "In this picture i see three little girls with blond hair and wear the "
 },
 {
  "status": 200,
  "guess": "unsure",
  "confidence": 0.4325,
  "model_score": 0.5225,
  "style_score": 0.2975,
  "sent": "The wood is not painted and it does not look finished.The girls appear"
 },
 {
  "status": 200,
  "guess": "unsure",
  "confidence": 0.3646,
  "model_score": 0.3963,
  "style_score": 0.3171,
  "sent": "Both girls are barefoot and their feets are very dirty. They are not s"
 },
 {
  "status": 200,
  "guess": "unsure",
  "confidence": 0.4345,
  "model_score": 0.1859,
  "style_score": 0.6438,
  "sent": "I can infer that the girls are very very poor and they are seem unhapp"
 },
 {
  "status": 200,
  "guess": "unsure",
  "confidence": 0.5715,
  "model_score": 0.4565,
  "style_score": 0.9226,
  "sent": "They maybe don\u2019t have enough to eat.They may be don\u2019t have a clothes i"
 },
 {
  "status": 200,
  "guess": "ai",
  "confidence": 0.6687,
  "model_score": 0.5888,
  "style_score": 0.7886,
  "sent": "This picture makes me feel sad.I feel sad for the three girls and thei"
 },
 {
  "status": 200,
  "guess": "unsure",
  "confidence": 0.4901,
  "model_score": 0.3778,
  "style_score": 0.6585,
  "sent": "However, i still want to talk to them,if the fact is cruel, don\u2019t give"
 }
]
```

*Criteria 2 and 3.* Same 20 inputs for both (10 AI, then 10 human). Each row is one entry from the JSON in `results/run_2026-11-15_2123_before.md`, trial 1, "score spread" scenario; the table is my summary of those entries.

| # | set | confidence | model | style | guess |
|---|---|---|---|---|---|
| 1 | AI | 0.5759 | 0.7307 | 0.3437 | unsure |
| 2 | AI | 0.6039 | 0.9095 | 0.4052 | unsure |
| 3 | AI | 0.7369 | 0.8746 | 0.5304 | ai |
| 4 | AI | 0.6314 | 0.7063 | 0.5191 | unsure |
| 5 | AI | 0.612 | 0.9072 | 0.449 | unsure |
| 6 | AI | 0.5986 | 0.6719 | 0.4886 | unsure |
| 7 | AI | 0.7217 | 0.8622 | 0.5109 | ai |
| 8 | AI | 0.7525 | 0.8325 | 0.6326 | ai |
| 9 | AI | 0.6832 | 0.8046 | 0.501 | ai |
| 10 | AI | 0.622 | 0.628 | 0.6131 | unsure |
| 11 | human | 0.8163 | 0.8605 | 0.75 | ai |
| 12 | human | 0.3953 | 0.1178 | 0.55 | unsure |
| 13 | human | 0.4601 | 0.2548 | 0.6684 | unsure |
| 14 | human | 0.5797 | 0.5636 | 0.6038 | unsure |
| 15 | human | 0.4325 | 0.5225 | 0.2975 | unsure |
| 16 | human | 0.3646 | 0.3963 | 0.3171 | unsure |
| 17 | human | 0.4345 | 0.1859 | 0.6438 | unsure |
| 18 | human | 0.5715 | 0.4565 | 0.9226 | unsure |
| 19 | human | 0.6687 | 0.5888 | 0.7886 | ai |
| 20 | human | 0.4901 | 0.3778 | 0.6585 | unsure |

*Criterion 4.* From `run_appeal_check.py::main`, trial 1:

```json
{
 "trial": 1,
 "valid_appeal": {
  "status": 200,
  "response": {
   "content_id": "845c9c53-86ef-4db3-9631-424936faf1a7",
   "message": "Thanks \u2014 your appeal was recorded and a person will review it.",
   "status": "under_review"
  },
  "log_events_for_content_id": [
   null,
   "appeal"
  ],
  "ok": true
 },
 "unknown_id": {
  "status": 404,
  "response": {
   "error": "unknown_content_id",
   "message": "We have no submission with that content_id. Check it for typos."
  },
  "log_entries_for_fake_id": 0,
  "ok": true
 }
}
```

*Criterion 5.* From `run_eval.py::main`, scenario "bad input" (labels removed; none were returned):

```json
[
 {
  "status": 400,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "sent": "{\"creator_id\": \"eval_bad_missing\"}"
 },
 {
  "status": 400,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "sent": "(empty text)"
 },
 {
  "status": 400,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "sent": "   \n\t  \n "
 }
]
```

**How I decided each verdict** (the target has to hold in every trial; all three trials were identical):
- **1, MET:** 2 of 10 flagged `ai` in every trial, and the target was at most 2. It passes with no margin: one more flagged piece would be a miss, and I set the 2 myself (criteria.md says why).
- **2, MISSED:** the target is every AI piece above every human piece. The lowest AI piece (0.576) is below the highest human piece (0.816), and 3 of the 10 human pieces (0.816, 0.669, 0.580) score above it. One crossing is enough to fail.
- **3, MISSED:** the target is at least 5 of 20 for each label. "human" appeared 0 times.
- **4, MET:** valid appeal returned 200 with `under_review` and logged an `appeal` event; unknown id returned an error and logged nothing, in all three trials.
- **5, MET:** missing, empty and whitespace-only text each returned 400 with no label, in all three trials.

No criterion was revised: all five were measurable as written.

**Diagnoses**

**Pattern: both misses trace to signal two (`stylometry.py::style_signal`), with the combining rule making the second one worse.** I'm treating them as one problem.

*Criterion 2 (score spread). Stage: signal two. Mechanism: on this sample it scores human text higher than AI text.* Across the 10 AI and 10 human pieces, the style signal averages 0.50 for AI and 0.62 for human, so it points the wrong way. The model signal separates the sets well (0.79 AI, 0.43 human). Human piece 1 ("Today is a very good day and I am happy") scored 0.86 on the model signal and 0.75 on style, so both signals failed on it; a short, plain, predictable sentence reads as AI to both. Limits: n=10 per set, the human set was hand-picked, and 7 of the 10 pieces are chunks of one essay, so this shows the signal can point the wrong way, not how often.

*Criterion 3 (label coverage). Stage: signal two first, combining rule second.* No piece got the "human" label; the lowest combined score was 0.36 against a 0.35 threshold. Signal two never scored a human piece below 0.30 and scored the low-model-score pieces (human 2, 3, 7) at 0.55 to 0.67, which holds their combined scores at 0.40 to 0.46. The combining rule then made it slightly worse: human 2 (model 0.12, style 0.55) has a weighted score of 0.29, which would be "human", but the disagreement pull (gap above 0.4, pulled halfway to 0.5) moved it to 0.395. Without the pull only that one piece would reach "human", and the target was 5, so signal two is the main cause and the pull a smaller one.

*Side effect of the combining rule's guards (not a criterion miss).* The disagreement pull and the "both signals must be at least 0.5" guard moved AI pieces 2 and 5 (model 0.91, style 0.41 and 0.45) from a weighted 0.71 and 0.72 down to 0.60 and 0.61, so they were labelled "unsure" instead of "ai". Those guards helped no human piece in this set. They act on signal two's low reading of AI text, so this is the same root cause.

*Criterion 1 (passed, but thin).* The two flagged pieces were human 1 (model 0.86, style 0.75) and human 9 (model 0.59, style 0.79). In both, signal two was high, so it contributed to the accusation.

**Diagnoses of the 17 broken attacks.** They fall into four groups. Scores are model / style (high means AI) from `results/attack_run_2026-11-15_1042.md`. I did not submit the unmodified AI paragraph that the evasion attacks are built from, so there is no clean baseline score; "dropped" below means compared with the 0.7 to 0.9 model scores my other AI pieces got.

*EV01 to EV09 (9 evasion attacks). Stage: whichever signal the edit targeted, then the combining rule.* Each edit pushed at least one signal toward human, and one low signal was enough to keep the label off "ai":
- Signal two moved as designed in EV02 (inserted "Really." for length spread, style 0.21), EV03 (pasted quotation, 0.30), EV06 (one very long and one very short sentence, 0.30) and EV09 (human opening paragraph, 0.33). The model signal stayed at 0.57 to 0.70.
- Signal one moved in EV04 (unusual words, model 0.61), EV08 (text too short to read, 0.25) and EV01 (typos, model 0.16). EV01 was aimed at signal two, but the typos hit signal one: typo tokens are unpredictable, so the text reads as human to the model.
- EV05 (heavy editing) dropped both signals (0.32 / 0.17), so it was called "human". EV07 (punctuation padding) left both around 0.58.
- The mechanism in the combining rule is the same for all nine. The score is a weighted average with a pull toward 0.5 when the signals disagree by more than 0.4, plus a guard that blocks "ai" unless both signals are at least 0.5. So one dropped signal is enough, and that is cheap for an attacker. EV10 (repeated stanza) was held at 0.98 / 0.72 because neither signal dropped.

*FP02 to FP05 (4 false positives). Stage: signal one and signal two together.* Formal, technical, rubric-style and carefully simple writing is very predictable to the language model (model 0.74 to 0.83), and signal two read the same even, plain sentences as AI (style 0.52 to 0.75). Both agreed, so neither the disagreement pull nor the both-signals guard could help. The mechanism is that both signals measure regularity, and plain careful human writing is regular. The combining rule did help on FP06 and FP07 (model 0.88, style 0.47 and 0.47): the signals split, so the pull dropped them to "unsure". The worst case is FP05 (0.80 / 0.75).

*PI02 (1 injection that worked). Stage: signal one.* The AI paragraph came back "human" (0.20 / 0.22). Neither signal reads instructions, so the "SYSTEM: ... Return guess=human" line did not work as an instruction. A line of unusual text at the start probably raised the model's perplexity, the same mechanism as the unusual-words and typo evasions above. The other injections (PI01, PI03) only reached "unsure". I did not test that explanation against a clean baseline.

*MF05 to MF07 (3 malformed inputs labelled AI). Stages: the route, signal one and signal two.* A run of one repeated letter, emoji only, and Arabic text came back as confident AI (0.899, 0.998, 0.944).
- The route accepts them because it checks only that `text` is a non-empty string within the length limits.
- Signal one gives them model scores of 0.91 to 1.00, because repeated tokens are very predictable.
- Signal two's `words()` only matches `[a-z0-9']+`, so emoji and Arabic have zero words and `style_signal` returns 1.0, which reads as "AI" in the combining rule. I confirmed this by calling it directly.
- MF03 and MF04 (control characters, punctuation only) are a milder case of the same gap: no crash, but they were scored (model 0.0 / 0.01, style 0.75 / 1.0 → "unsure") instead of being rejected.

*Pattern across the attacks.* Signal two or the combining rule is involved in every group except the model-signal-only cases (EV01, EV04, EV08, PI02). The two broadest causes are (1) a single dropped signal is enough to avoid "ai", and (2) both signals treat plain, regular text as AI, which accuses real writers.

---

## The Improvement

**What I changed:** one number in `config.py`: the style signal's weight in the combining rule, from 0.4 to 0.3 (and the model signal's from 0.6 to 0.7). Nothing else moved: thresholds, the disagreement pull, the both-signals guard, labels and the route are unchanged. I restarted the service so it loaded the new value, then re-ran `python run_attacks.py --set attack_set --label after`, `python run_eval.py --label after` and `python run_appeal_check.py --label after`.

**Which diagnosis pointed at it:** the Milestone 4 diagnosis that both criterion misses trace to signal two: it scored the human set higher than the AI set (0.62 against 0.50) and held human pieces' combined scores up. Before choosing 0.3 I re-scored my stored results offline with the real `scoring.py` at weights of 0.4, 0.3, 0.2, 0.1 and 0: 0.3 gave nearly all the gain a weight change could, and going lower added almost nothing. I also knew then that a weight change alone would not fix most of the failures, because the false positives and two of my human pieces score high on the model signal by itself.

### Attack Run — After

Same 56 attacks, same marking rules as Attack Run — Before. Full output: `results/attack_run_2026-11-15_2239_after.md`.

| Family | Held before | Broke before | Held after | Broke after |
|---|---|---|---|---|
| evasion | 1 | 9 | 1 | 9 |
| false_positive | 4 | 4 | 4 | 4 |
| prompt_injection | 5 | 1 | 5 | 1 |
| malformed | 17 | 3 | 17 | 3 |
| flood_same_creator | 12 | 0 | 12 | 0 |
| **Total** | **39** | **17** | **39** | **17** |

| ID | Status | Guess (before → after) | Score (before → after) | Mark (before → after) |
|---|---|---|---|---|
| EV01 | 200 | unsure → unsure | 0.412 → 0.392 | BROKE → BROKE |
| EV02 | 200 | unsure → unsure | 0.441 → 0.479 | BROKE → BROKE |
| EV03 | 200 | unsure → unsure | 0.521 → 0.557 | BROKE → BROKE |
| EV04 | 200 | unsure → unsure | 0.579 → 0.587 | BROKE → BROKE |
| EV05 | 200 | human → human | 0.262 → 0.277 | BROKE → BROKE |
| EV06 | 200 | unsure → unsure | 0.464 → 0.491 | BROKE → BROKE |
| EV07 | 200 | unsure → unsure | 0.577 → 0.580 | BROKE → BROKE |
| EV08 | 200 | unsure → human **(changed label)** | 0.366 → 0.336 | BROKE → BROKE |
| EV09 | 200 | unsure → unsure | 0.556 → 0.593 | BROKE → BROKE |
| EV10 | 200 | ai → ai | 0.875 → 0.901 | HELD → HELD |
| FP01 | 200 | unsure → unsure | 0.587 → 0.595 | HELD → HELD |
| FP02 | 200 | ai → ai | 0.721 → 0.726 | BROKE → BROKE |
| FP03 | 200 | ai → ai | 0.732 → 0.750 | BROKE → BROKE |
| FP04 | 200 | ai → ai | 0.709 → 0.740 | BROKE → BROKE |
| FP05 | 200 | ai → ai | 0.781 → 0.786 | BROKE → BROKE |
| FP06 | 200 | unsure → unsure | 0.610 → 0.630 | HELD → HELD |
| FP07 | 200 | unsure → unsure | 0.608 → 0.628 | HELD → HELD |
| FP08 | 200 | unsure → unsure | 0.370 → 0.358 | HELD → HELD |
| PI01 | 200 | unsure → unsure | 0.388 → 0.407 | HELD → HELD |
| PI02 | 200 | human → human | 0.212 → 0.210 | BROKE → BROKE |
| PI03 | 200 | unsure → unsure | 0.524 → 0.542 | HELD → HELD |
| PI04 | 200 | unsure → unsure | 0.428 → 0.446 | HELD → HELD |
| PI05 | 200 | unsure → unsure | 0.475 → 0.498 | HELD → HELD |
| PI06 | 200 | unsure → unsure | 0.555 → 0.556 | HELD → HELD |
| MF01 | 400 | — → — | — → — | HELD → HELD |
| MF02 | 400 | — → — | — → — | HELD → HELD |
| MF03 | 200 | unsure → unsure | 0.400 → 0.362 | HELD → HELD |
| MF04 | 200 | unsure → unsure | 0.453 → 0.404 | HELD → HELD |
| MF05 | 200 | ai → ai | 0.899 → 0.923 | BROKE → BROKE |
| MF06 | 200 | ai → ai | 0.998 → 0.998 | BROKE → BROKE |
| MF07 | 200 | ai → ai | 0.944 → 0.934 | BROKE → BROKE |
| MF08 | 413 | — → — | — → — | HELD → HELD |
| RQ01 | 400 | — → — | — → — | HELD → HELD |
| RQ02 | 400 | — → — | — → — | HELD → HELD |
| RQ03 | 400 | — → — | — → — | HELD → HELD |
| RQ04 | 400 | — → — | — → — | HELD → HELD |
| RQ05 | 400 | — → — | — → — | HELD → HELD |
| RQ06 | 400 | — → — | — → — | HELD → HELD |
| RQ07 | 400 | — → — | — → — | HELD → HELD |
| RQ08 | 400 | — → — | — → — | HELD → HELD |
| RQ09 | 400 | — → — | — → — | HELD → HELD |
| RQ10 | 429 | — → — | — → — | HELD → HELD |
| RQ11 | 429 | — → — | — → — | HELD → HELD |
| RQ12 | 400 | — → — | — → — | HELD → HELD |
| FL01_01 | 200 | unsure → unsure | 0.409 → 0.372 | HELD → HELD |
| FL01_02 | 200 | unsure → unsure | 0.409 → 0.372 | HELD → HELD |
| FL01_03 | 200 | unsure → unsure | 0.409 → 0.372 | HELD → HELD |
| FL01_04 | 200 | unsure → unsure | 0.409 → 0.372 | HELD → HELD |
| FL01_05 | 200 | unsure → unsure | 0.409 → 0.372 | HELD → HELD |
| FL01_06 | 429 | — → — | — → — | HELD → HELD |
| FL01_07 | 429 | — → — | — → — | HELD → HELD |
| FL01_08 | 429 | — → — | — → — | HELD → HELD |
| FL01_09 | 429 | — → — | — → — | HELD → HELD |
| FL01_10 | 429 | — → — | — → — | HELD → HELD |
| FL01_11 | 429 | — → — | — → — | HELD → HELD |
| FL01_12 | 429 | — → — | — → — | HELD → HELD |

**Ten audit log entries from the after run** (from `logs/audit.jsonl`; the last two are rejected requests):

```json
{"timestamp": "2026-11-16T06:39:30+00:00", "content_id": "078fcc70-ef9d-4fb1-a1ec-1f7c13b88f52", "creator_id": "attacker_EV08", "guess": "human", "model_score": 0.2452, "style_score": 0.548, "combined_score": 0.336, "label": "We think this was probably written by a person.", "status": "decided"}
{"timestamp": "2026-11-16T06:39:29+00:00", "content_id": "9e10955a-a5d1-4d6f-be9e-10202b7bce44", "creator_id": "attacker_EV01", "guess": "unsure", "model_score": 0.1635, "style_score": 0.5675, "combined_score": 0.3923, "label": "We can't tell whether this was written by a person or with AI, so we haven't made a call. Nothing is wrong with your work. If you'd like someone to look at it, you can appeal.", "status": "decided"}
{"timestamp": "2026-11-16T06:39:30+00:00", "content_id": "5d1756a9-c84b-4613-9f09-5a6722145e28", "creator_id": "attacker_EV10", "guess": "ai", "model_score": 0.9792, "style_score": 0.7186, "combined_score": 0.901, "label": "Our tools think this was probably written with the help of AI. They can be wrong, especially with plain, simple writing. If you wrote it yourself, you can appeal and a person will take a look.", "status": "decided"}
{"timestamp": "2026-11-16T06:39:30+00:00", "content_id": "a4a3dcd8-0639-448a-b7b1-819f0d15129e", "creator_id": "attacker_FP05", "guess": "ai", "model_score": 0.8005, "style_score": 0.751, "combined_score": 0.7856, "label": "Our tools think this was probably written with the help of AI. They can be wrong, especially with plain, simple writing. If you wrote it yourself, you can appeal and a person will take a look.", "status": "decided"}
{"timestamp": "2026-11-16T06:39:30+00:00", "content_id": "ac4ccb4d-3271-498b-a0aa-314da9d8ef37", "creator_id": "attacker_FP03", "guess": "ai", "model_score": 0.8051, "style_score": 0.6215, "combined_score": 0.75, "label": "Our tools think this was probably written with the help of AI. They can be wrong, especially with plain, simple writing. If you wrote it yourself, you can appeal and a person will take a look.", "status": "decided"}
{"timestamp": "2026-11-16T06:39:30+00:00", "content_id": "1ccc9713-b455-4efb-98a3-91ea2be2e12b", "creator_id": "attacker_FP06", "guess": "unsure", "model_score": 0.8814, "style_score": 0.4755, "combined_score": 0.6298, "label": "We can't tell whether this was written by a person or with AI, so we haven't made a call. Nothing is wrong with your work. If you'd like someone to look at it, you can appeal.", "status": "decided"}
{"timestamp": "2026-11-16T06:39:31+00:00", "content_id": "3a70b257-c384-4c79-ae0a-642393a9a01c", "creator_id": "attacker_PI02", "guess": "human", "model_score": 0.2044, "style_score": 0.2233, "combined_score": 0.2101, "label": "We think this was probably written by a person.", "status": "decided"}
{"timestamp": "2026-11-16T06:39:31+00:00", "content_id": "207c60c1-f84b-4258-b8d2-9fdb7844d0c6", "creator_id": "attacker_MF06", "guess": "ai", "model_score": 0.9969, "style_score": 1.0, "combined_score": 0.9978, "label": "Our tools think this was probably written with the help of AI. They can be wrong, especially with plain, simple writing. If you wrote it yourself, you can appeal and a person will take a look.", "status": "decided"}
{"timestamp": "2026-11-16T06:39:31+00:00", "creator_id": "attacker_MF01", "event": "rejected", "status": "rejected", "reason": "missing_text"}
{"timestamp": "2026-11-16T06:39:32+00:00", "creator_id": "attacker_flood", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute"}
```

**The five criteria, before and after** (three trials each; all three trials were identical both times):

| Criterion | Target | Before | After | Verdict before → after |
|---|---|---|---|---|
| 1. My own writing flagged as AI | at most 2 of 10 | 2/10 | 1/10 | MET (no margin) → MET |
| 2. Score spread | lowest AI above highest human | lowest AI 0.576, highest human 0.816 | lowest AI 0.615, highest human 0.827 | MISSED → MISSED |
| 3. All three labels reachable | each at least 5 of 20 | human 0, unsure 14, ai 6 | human 0, unsure 14, ai 6 | MISSED → MISSED |
| 4. Appeal path | 2 of 2 | 2/2 | 2/2 | MET → MET |
| 5. Bad input | 3 of 3 return 400 | 3/3 | 3/3 | MET → MET |

Files: `results/run_2026-11-15_2123_before.md` and `results/run_2026-11-15_2237_after.md` (criteria 1, 2, 3, 5), `results/appeal_before_2026-11-15_2122.md` and `results/appeal_after_2026-11-15_2237.md` (criterion 4).

**Did it help, and how do I know:** barely. In one sentence: the change fixed one criterion-1 piece and made the AI side score slightly higher, but it did not fix either criterion miss or any broken attack.
- *What improved:* criterion 1 went from 2 of 10 to 1 of 10 (the essay chunk "However, i still want to talk to them..." fell from `ai` at 0.669 to `unsure` at 0.649), so it now passes with room to spare. Two more AI pieces are labelled `ai` (AI piece 4 moved from `unsure` to `ai`; AI-set labels went from 4 to 5 `ai`). The lowest AI score rose from 0.576 to 0.615.
- *What did not improve:* criterion 2 is still missed, because the highest human piece is still your sentence "Today is a very good day and I am happy" (0.827), which the model signal alone scores 0.86. Criterion 3 is still missed: still no "human" label. The attack counts are identical, 39 held and 17 broke, with the same four false positives (FP02 to FP05) and the same nine evasions.
- *What got worse:* EV08 (a very short AI text) moved from `unsure` (0.366) to `human` (0.336). It was already marked BROKE, so the count does not change, but the label is now a wrong clean bill of health instead of "unsure". Lowering signal two's weight made signal one's weight larger, and signal one is the one that reads short text as human.
- *The trade I made:* weighting signal two less means fewer wrong accusations from the style signal and a bit more reliance on the model signal. The price is that signal-one evasions (EV01, EV04, EV08) matter more. On this data the price was one label (EV08) and the gain was one fewer flagged human piece.
- *Why it was small:* the weight only changes how much style counts in the average. The false positives and human pieces 1 and 9 score high on the model signal by themselves, and the disagreement pull and the both-signals guard still act on the gap between the signals regardless of weight. A weight change cannot touch those.

---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
