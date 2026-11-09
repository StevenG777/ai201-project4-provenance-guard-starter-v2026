# Design notes — Milestone 1

Written before building the endpoints. Fixed details here are the contract the code has to keep.

## 1. The path of a submission

1. **Request arrives.** `POST /submit` with `{"text", "creator_id"}`. The handler in `app.py` validates the input (missing, empty, too short, too long, not JSON) and creates a `content_id` (uuid).
2. **Signal one — `detector.model_signal(text)`.** Local gpt2 measures how predictable the text is (perplexity). Adds `model_score` (0–1, higher = more likely AI).
3. **Signal two — `stylometry.style_signal(text)`.** Measures the text as text: sentence-length spread, type-token ratio, punctuation density. Adds `style_score` (0–1, same direction).
4. **Combine — `scoring.combine_signals`.** Turns the two scores into one `confidence` number.
5. **Label — `scoring.score_to_label`.** Thresholds in `config.py` pick one of three bands and return `guess` + label text.
6. **Log — `audit.log_decision`.** Stores content_id, creator_id, both signal scores, combined score, guess, label, status `decided`.
7. **Response.** JSON with `content_id`, `guess`, `confidence`, `label`, `model_score`, `style_score`.

Appeal branch: `POST /appeal` → confirm `content_id` exists (`audit.entries_for`) → `audit.log_appeal` sets status `under_review` → confirm to the writer.

## 2. The two signals

### Signal one — model signal (`detector.py`)
- **Measures:** perplexity of the raw text under a local language model (gpt2). Low perplexity means the model could have guessed it.
- **Why it may differ:** AI text is built from likely next words, so it is predictable. Human text has odd word choices, slang, errors and specifics, so it surprises the model more.
- **Blind spot:** predictability is not authorship. Plain writing in common words and short sentences (young writers, second-language writers, anyone writing simply) scores as machine-like. Measured: a plain human paragraph had perplexity 9.4 → `model_score` 0.92, higher than a stiff AI-style paragraph (0.79). Ornate human prose with rare words can look human to it, and so can AI text that is deliberately ornate.

### Signal two — style signal (`stylometry.py`)
- **Measures:**
  - `sentence_length_spread` — do sentence lengths vary or march in step?
  - `type_token_ratio` — how much of the vocabulary repeats?
  - `punctuation_density` — how much punctuation and how varied (semicolons and dashes count more than full stops).
- **Why it may differ:** AI prose tends toward even, mid-length sentences and a narrower vocabulary.
- **Blind spots:**
  - It cannot read. Typos, broken-up sentences or pasted quotations change the shape without changing who wrote it.
  - `words()` matches only `[a-z0-9']+`, so non-Latin text (Chinese, Russian) yields no words and the signal is unreliable or meaningless for it.

## 3. Trace of a false positive

A student writes a simple paragraph about their hometown, in their own words.
- **Score:** signal one gives perplexity about 9 → `model_score` about 0.92. Signal two is not built yet; plain short even sentences will probably score AI-ish too (to be measured in Milestone 4). Combined likely above the 0.65 AI threshold.
- **Label:** the high-confidence AI label.
- **What they can do:** `POST /appeal` with their reasoning; the item moves to `under_review`.
- **Design consequences:** 
  - (a) the AI threshold may need to sit higher, or the AI label should need both signals to agree; 
  - (b) label wording must not read as an accusation; 
  - (c) the label should tell the writer an appeal exists.

## 4. Endpoint contracts

### POST /submit
Request (JSON):

| Field | Type | Required | Rules |
|---|---|---|---|
| `text` | string | yes | Non-empty after trimming; too short to score → 400; over the length cap (10,000 chars, to confirm) → 413 |
| `creator_id` | string | yes | Non-empty; opaque label, no login |

Response 200:

| Field | Type | Meaning |
|---|---|---|
| `content_id` | string (uuid) | Used by `/appeal` |
| `guess` | `"ai"` / `"human"` / `"unsure"` | Machine-readable verdict |
| `confidence` | float 0–1 | Combined score. **Higher = more likely AI** (not "confidence in the guess") |
| `label` | string | Full sentence the reader sees |
| `model_score` | float 0–1 | Signal one, higher = more likely AI |
| `style_score` | float 0–1 | Signal two, higher = more likely AI |

Errors are always `{"error": "<code>", "message": "<sentence>"}`:
400 `invalid_json`, `missing_text`, `missing_creator_id`, `text_too_short`; 413 `text_too_long`; 503 `detector_unavailable`. Non-Latin text must return a valid score or a clean 400, never a 500.

### POST /appeal
Request (JSON): `content_id` (string, must exist) and `reasoning` (string, non-empty, length-capped).

Response 200:
```json
{"content_id": "...", "status": "under_review",
 "message": "Thanks — your appeal was recorded and a person will review it."}
```
Errors: 400 `invalid_json` / `missing_content_id` / `missing_reasoning`; 404 `unknown_content_id`.

Decisions: appealing the same item twice returns 200 and records it again. The same creator submitting the same text twice gets a new `content_id` each time. `/appeal` does not check ownership (no `creator_id` in the request); this is a known limitation.
