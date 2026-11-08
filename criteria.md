# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---
## 1. False positives: plain human writing is rarely called AI

Of 10 pieces I wrote myself, each simple and short-sentenced, at most 2 get the
high-confidence AI label (`guess == "ai"`). The same 10 pieces are used in every
trial, and the limit has to hold in all three trials.

**Why this target:**

On a writing site, wrongly accusing a real writer costs more than missing some AI
text. Plain, short-sentence writing is the case the model signal is most likely to
get wrong. I allow 2 of 10 rather than 1 because the model can simply mispredict a
piece, and 1 in 10 would be too strict to hold reliably across three trials.

---

---

## 2. Score spread: clearly-AI text scores above clearly-human text

I choose 10 clearly-AI pieces and 10 clearly-human pieces by hand, and use the same
20 in every trial. On the combined `confidence` score, every AI piece scores above
every human piece: the lowest AI score is higher than the highest human score.

**Why this target:**

I chose 10 of each because with 2 or 3 pieces a good result could be luck, and 10
shows the separation holds. I chose "every" over an average because an average can
hide one badly wrong piece, and I would rather fail on a single outlier and look at it.

---

---

## 3. Label coverage: all three labels are reachable

I choose 20 inputs and use the same 20 in every trial. Counting the labels the
service actually returns (not the ones I expected), each of the three labels
(high-confidence human, unsure, high-confidence AI) appears at least 5 times out of 20.

**Why this target:**

I chose 20 inputs because 10 is too few to see three labels spread out. I chose at
least 5 per label rather than 3 because 3 per label only accounts for 9 of the 20
inputs and would let a label be nearly unreachable and still pass.

---

---

## 4. Appeal path: an appeal always changes status and is always recorded

In 2 of 2 test appeals, the service does the right thing. Appeal 1 is a valid
`content_id` with reasoning: the response confirms, the item's status becomes
`under_review`, and the appeal appears in the log. Appeal 2 is an unknown
`content_id`: the service returns a clear error and does not create a log entry
for a nonexistent item.

**Why this target:**

The appeal logic is deterministic, so it either works or it doesn't, and there is no
random chance to allow for. Two cases are enough: if both are right or both are wrong
it points to a logic error, and if only one is right it shows an edge case I missed.
It has to be 2 of 2 because this is the only thing standing between a wrong
accusation and nothing at all.

---

---

## 5. Bad input: missing or empty text is rejected, not labelled

When `text` is missing, empty, or only whitespace, `POST /submit` returns an error
response (HTTP 400 with an `error` field) in all 3 of those cases. It never returns a
label, and it never crashes with a 500.

**Why this target:**

Empty text was written by neither a person nor an AI, so it fits none of the three
labels, and any label or score returned for it would be made up. Rejecting it with a
clear error is the only honest answer. It has to be all 3 of 3 because a crash on
malformed input is one of the most common real failures.

---

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
