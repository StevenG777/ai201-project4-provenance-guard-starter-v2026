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

Provenance Guard is a small backend a writing site could plug into. A piece of text goes in; a guess, a score, a plain-English label and a way to appeal come out. More detail in [DESIGN.md](DESIGN.md).

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

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



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
