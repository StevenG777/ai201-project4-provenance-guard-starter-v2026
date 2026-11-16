# Attack run — after

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-15 22:39
- Auto-marked BROKE (5xx, crash, no response): **0**
- Left for you to judge: **56**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `9e10955a-a5d1-4d6f-be9e-10202b7bce44` | unsure | 0.392 |  |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `75ed26bb-f2c0-491d-9fdf-b2005083f877` | unsure | 0.479 |  |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `78276e34-e675-406b-9e14-b2a23261db29` | unsure | 0.557 |  |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `23ab71df-744d-437d-9f11-e5d68cf365e4` | unsure | 0.587 |  |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `7850a6b8-c394-4aba-899d-b0d3d8e51ac2` | human | 0.277 |  |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `49c63402-af37-4174-ba96-f6de8977b67e` | unsure | 0.491 |  |
| EV07 | evasion | signal two: padding with punctuation | 200 | `cc702347-289e-4d55-9ec2-f7a0eddb1379` | unsure | 0.580 |  |
| EV08 | evasion | signal one: text below the token window | 200 | `078fcc70-ef9d-4fb1-a1ec-1f7c13b88f52` | human | 0.336 |  |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `c3f12d05-f280-4b8d-8e62-a5fcc294b4a7` | unsure | 0.593 |  |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `5d1756a9-c84b-4613-9f09-5a6722145e28` | ai | 0.901 |  |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `00ea6ac3-a966-40e7-9b1c-f4fa770ea0a6` | unsure | 0.595 |  |
| FP02 | false_positive | human writing in a formal register | 200 | `8cda2a71-5e91-419f-bf67-1a32594d5481` | ai | 0.726 |  |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `ac4ccb4d-3271-498b-a0aa-314da9d8ef37` | ai | 0.750 |  |
| FP04 | false_positive | a student essay written to a rubric | 200 | `c4c347ca-34e0-48be-9f4a-875b974406a1` | ai | 0.740 |  |
| FP05 | false_positive | technical documentation written by a person | 200 | `a4a3dcd8-0639-448a-b7b1-819f0d15129e` | ai | 0.786 |  |
| FP06 | false_positive | a person imitating a formal template | 200 | `1ccc9713-b455-4efb-98a3-91ea2be2e12b` | unsure | 0.630 |  |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `bc0e2f25-7fdb-4e0e-bb0b-3ef69b7bfd87` | unsure | 0.628 |  |
| FP08 | false_positive | very short genuine human submission | 200 | `79c538d4-e4bc-4e8a-b8cc-abafe74618f8` | unsure | 0.358 |  |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `707f799b-f22c-4127-9049-7b386d6d8a8f` | unsure | 0.407 |  |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `3a70b257-c384-4c79-ae0a-642393a9a01c` | human | 0.210 |  |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `b20f7f1f-24f8-4001-9a57-d622be799dea` | unsure | 0.542 |  |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `56d05f27-edb1-453c-91a5-068d463b9da4` | unsure | 0.446 |  |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `e1e0faa3-531c-44b6-b27c-8d7e8b6cbea4` | unsure | 0.498 |  |
| PI06 | prompt_injection | instruction plus real human text | 200 | `9d6b3306-eefc-4f12-ac23-98175b4dcaed` | unsure | 0.556 |  |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — |  |
| MF02 | malformed | text is a single character | 400 | `—` | — | — |  |
| MF03 | malformed | text is control characters | 200 | `94f0b2f6-0608-43ee-8c27-9208cfdb13e9` | unsure | 0.362 |  |
| MF04 | malformed | text is only punctuation | 200 | `df063e07-1320-4d57-b7af-80a09ca1c614` | unsure | 0.404 |  |
| MF05 | malformed | text is a very long single word | 200 | `819614b5-c419-4213-a53e-b890de4cb4ec` | ai | 0.923 |  |
| MF06 | malformed | text is emoji only | 200 | `207c60c1-f84b-4258-b8d2-9fdb7844d0c6` | ai | 0.998 |  |
| MF07 | malformed | text is right-to-left script | 200 | `9748a4c6-88cf-4234-9644-fcdf78f4ca52` | ai | 0.934 |  |
| MF08 | malformed | text is 60,000 characters | 413 | `—` | — | — |  |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — |  |
| RQ02 | malformed | no creator_id | 400 | `—` | — | — |  |
| RQ03 | malformed | text is a number | 400 | `—` | — | — |  |
| RQ04 | malformed | text is a list | 400 | `—` | — | — |  |
| RQ05 | malformed | text is null | 400 | `—` | — | — |  |
| RQ06 | malformed | creator_id is an object | 400 | `—` | — | — |  |
| RQ07 | malformed | body is a JSON array, not an object | 400 | `—` | — | — |  |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — |  |
| RQ09 | malformed | body is empty | 400 | `—` | — | — |  |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | `—` | — | — |  |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | `—` | — | — |  |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — |  |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `cc5827e8-3775-4fb9-90d2-e1a62cfeca33` | unsure | 0.372 |  |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `aaee95f0-4afa-490b-8337-26f6b62b7b13` | unsure | 0.372 |  |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `03f60e28-d963-43d8-afcb-053ecb671ef8` | unsure | 0.372 |  |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `10702dbc-997a-4d39-be12-ccfc4128dd33` | unsure | 0.372 |  |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c656e97e-914f-495e-b437-6400f28f8579` | unsure | 0.372 |  |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 0 | 10 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 0 | 20 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "9e10955a-a5d1-4d6f-be9e-10202b7bce44",
  "creator_id": "attacker_EV01",
  "guess": "unsure",
  "confidence": 0.3923,
  "model_score": 0.1635,
  "style_score": 0.5675,
  "label": "We can't tell whether this was written by a person or with AI, so we haven't made a call. Nothing is wrong with your work. If you'd like someone to look at it, you can appeal.",
  "error": null,
  "verdict": ""
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "75ed26bb-f2c0-491d-9fdf-b2005083f877",
  "creator_id": "attacker_EV02",
  "guess": "unsure",
  "confidence": 0.4795,
  "model_score": 0.5943,
  "style_score": 0.2116,
  "label": "We can't tell whether this was written by a person or with AI, so we haven't made a call. Nothing is wrong with your work. If you'd like someone to look at it, you can appeal.",
  "error": null,
  "verdict": ""
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "78276e34-e675-406b-9e14-b2a23261db29",
  "creator_id": "attacker_EV03",
  "guess": "unsure",
  "confidence": 0.5573,
  "model_score": 0.6662,
  "style_score": 0.3033,
  "label": "We can't tell whether this was written by a person or with AI, so we haven't made a call. Nothing is wrong with your work. If you'd like someone to look at it, you can appeal.",
  "error": null,
  "verdict": ""
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "23ab71df-744d-437d-9f11-e5d68cf365e4",
  "creator_id": "attacker_EV04",
  "guess": "unsure",
  "confidence": 0.5871,
  "model_score": 0.6114,
  "style_score": 0.5303,
  "label": "We can't tell whether this was written by a person or with AI, so we haven't made a call. Nothing is wrong with your work. If you'd like someone to look at it, you can appeal.",
  "error": null,
  "verdict": ""
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "7850a6b8-c394-4aba-899d-b0d3d8e51ac2",
  "creator_id": "attacker_EV05",
  "guess": "human",
  "confidence": 0.2765,
  "model_score": 0.3212,
  "style_score": 0.1723,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "49c63402-af37-4174-ba96-f6de8977b67e",
  "creator_id": "attacker_EV06",
  "guess": "unsure",
  "confidence": 0.4914,
  "model_score": 0.5727,
  "style_score": 0.3018,
  "label": "We can't tell whether this was written by a person or with AI, so we haven't made a call. Nothing is wrong with your work. If you'd like someone to look at it, you can appeal.",
  "error": null,
  "verdict": ""
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "cc702347-289e-4d55-9ec2-f7a0eddb1379",
  "creator_id": "attacker_EV07",
  "guess": "unsure",
  "confidence": 0.5795,
  "model_score": 0.5862,
  "style_score": 0.564,
  "label": "We can't tell whether this was written by a person or with AI, so we haven't made a call. Nothing is wrong with your work. If you'd like someone to look at it, you can appeal.",
  "error": null,
  "verdict": ""
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 200,
  "content_id": "078fcc70-ef9d-4fb1-a1ec-1f7c13b88f52",
  "creator_id": "attacker_EV08",
  "guess": "human",
  "confidence": 0.336,
  "model_score": 0.2452,
  "style_score": 0.548,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "c3f12d05-f280-4b8d-8e62-a5fcc294b4a7",
  "creator_id": "attacker_EV09",
  "guess": "unsure",
  "confidence": 0.593,
  "model_score": 0.7042,
  "style_score": 0.3335,
  "label": "We can't tell whether this was written by a person or with AI, so we haven't made a call. Nothing is wrong with your work. If you'd like someone to look at it, you can appeal.",
  "error": null,
  "verdict": ""
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "5d1756a9-c84b-4613-9f09-5a6722145e28",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.901,
  "model_score": 0.9792,
  "style_score": 0.7186,
  "label": "Our tools think this was probably written with the help of AI. They can be wrong, especially with plain, simple writing. If you wrote it yourself, you can appeal and a person will take a look.",
  "error": null,
  "verdict": ""
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "00ea6ac3-a966-40e7-9b1c-f4fa770ea0a6",
  "creator_id": "attacker_FP01",
  "guess": "unsure",
  "confidence": 0.5945,
  "model_score": 0.6175,
  "style_score": 0.5409,
  "label": "We can't tell whether this was written by a person or with AI, so we haven't made a call. Nothing is wrong with your work. If you'd like someone to look at it, you can appeal.",
  "error": null,
  "verdict": ""
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "8cda2a71-5e91-419f-bf67-1a32594d5481",
  "creator_id": "attacker_FP02",
  "guess": "ai",
  "confidence": 0.7255,
  "model_score": 0.7387,
  "style_score": 0.6946,
  "label": "Our tools think this was probably written with the help of AI. They can be wrong, especially with plain, simple writing. If you wrote it yourself, you can appeal and a person will take a look.",
  "error": null,
  "verdict": ""
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "ac4ccb4d-3271-498b-a0aa-314da9d8ef37",
  "creator_id": "attacker_FP03",
  "guess": "ai",
  "confidence": 0.75,
  "model_score": 0.8051,
  "style_score": 0.6215,
  "label": "Our tools think this was probably written with the help of AI. They can be wrong, especially with plain, simple writing. If you wrote it yourself, you can appeal and a person will take a look.",
  "error": null,
  "verdict": ""
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "c4c347ca-34e0-48be-9f4a-875b974406a1",
  "creator_id": "attacker_FP04",
  "guess": "ai",
  "confidence": 0.7397,
  "model_score": 0.8329,
  "style_score": 0.5224,
  "label": "Our tools think this was probably written with the help of AI. They can be wrong, especially with plain, simple writing. If you wrote it yourself, you can appeal and a person will take a look.",
  "error": null,
  "verdict": ""
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "a4a3dcd8-0639-448a-b7b1-819f0d15129e",
  "creator_id": "attacker_FP05",
  "guess": "ai",
  "confidence": 0.7856,
  "model_score": 0.8005,
  "style_score": 0.751,
  "label": "Our tools think this was probably written with the help of AI. They can be wrong, especially with plain, simple writing. If you wrote it yourself, you can appeal and a person will take a look.",
  "error": null,
  "verdict": ""
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "1ccc9713-b455-4efb-98a3-91ea2be2e12b",
  "creator_id": "attacker_FP06",
  "guess": "unsure",
  "confidence": 0.6298,
  "model_score": 0.8814,
  "style_score": 0.4755,
  "label": "We can't tell whether this was written by a person or with AI, so we haven't made a call. Nothing is wrong with your work. If you'd like someone to look at it, you can appeal.",
  "error": null,
  "verdict": ""
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "bc0e2f25-7fdb-4e0e-bb0b-3ef69b7bfd87",
  "creator_id": "attacker_FP07",
  "guess": "unsure",
  "confidence": 0.6284,
  "model_score": 0.8816,
  "style_score": 0.4653,
  "label": "We can't tell whether this was written by a person or with AI, so we haven't made a call. Nothing is wrong with your work. If you'd like someone to look at it, you can appeal.",
  "error": null,
  "verdict": ""
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 200,
  "content_id": "79c538d4-e4bc-4e8a-b8cc-abafe74618f8",
  "creator_id": "attacker_FP08",
  "guess": "unsure",
  "confidence": 0.3578,
  "model_score": 0.3223,
  "style_score": 0.4407,
  "label": "We can't tell whether this was written by a person or with AI, so we haven't made a call. Nothing is wrong with your work. If you'd like someone to look at it, you can appeal.",
  "error": null,
  "verdict": ""
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "707f799b-f22c-4127-9049-7b386d6d8a8f",
  "creator_id": "attacker_PI01",
  "guess": "unsure",
  "confidence": 0.4068,
  "model_score": 0.4625,
  "style_score": 0.2767,
  "label": "We can't tell whether this was written by a person or with AI, so we haven't made a call. Nothing is wrong with your work. If you'd like someone to look at it, you can appeal.",
  "error": null,
  "verdict": ""
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "3a70b257-c384-4c79-ae0a-642393a9a01c",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.2101,
  "model_score": 0.2044,
  "style_score": 0.2233,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "b20f7f1f-24f8-4001-9a57-d622be799dea",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.5416,
  "model_score": 0.5943,
  "style_score": 0.4186,
  "label": "We can't tell whether this was written by a person or with AI, so we haven't made a call. Nothing is wrong with your work. If you'd like someone to look at it, you can appeal.",
  "error": null,
  "verdict": ""
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "56d05f27-edb1-453c-91a5-068d463b9da4",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.446,
  "model_score": 0.4998,
  "style_score": 0.3206,
  "label": "We can't tell whether this was written by a person or with AI, so we haven't made a call. Nothing is wrong with your work. If you'd like someone to look at it, you can appeal.",
  "error": null,
  "verdict": ""
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "e1e0faa3-531c-44b6-b27c-8d7e8b6cbea4",
  "creator_id": "attacker_PI05",
  "guess": "unsure",
  "confidence": 0.4985,
  "model_score": 0.6401,
  "style_score": 0.1633,
  "label": "We can't tell whether this was written by a person or with AI, so we haven't made a call. Nothing is wrong with your work. If you'd like someone to look at it, you can appeal.",
  "error": null,
  "verdict": ""
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "9d6b3306-eefc-4f12-ac23-98175b4dcaed",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.5559,
  "model_score": 0.5583,
  "style_score": 0.5502,
  "label": "We can't tell whether this was written by a person or with AI, so we haven't made a call. Nothing is wrong with your work. If you'd like someone to look at it, you can appeal.",
  "error": null,
  "verdict": ""
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 200,
  "content_id": "94f0b2f6-0608-43ee-8c27-9208cfdb13e9",
  "creator_id": "attacker_MF03",
  "guess": "unsure",
  "confidence": 0.3625,
  "model_score": 0.0,
  "style_score": 0.75,
  "label": "We can't tell whether this was written by a person or with AI, so we haven't made a call. Nothing is wrong with your work. If you'd like someone to look at it, you can appeal.",
  "error": null,
  "verdict": ""
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 200,
  "content_id": "df063e07-1320-4d57-b7af-80a09ca1c614",
  "creator_id": "attacker_MF04",
  "guess": "unsure",
  "confidence": 0.4039,
  "model_score": 0.0112,
  "style_score": 1.0,
  "label": "We can't tell whether this was written by a person or with AI, so we haven't made a call. Nothing is wrong with your work. If you'd like someone to look at it, you can appeal.",
  "error": null,
  "verdict": ""
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 200,
  "content_id": "819614b5-c419-4213-a53e-b890de4cb4ec",
  "creator_id": "attacker_MF05",
  "guess": "ai",
  "confidence": 0.9233,
  "model_score": 0.9976,
  "style_score": 0.75,
  "label": "Our tools think this was probably written with the help of AI. They can be wrong, especially with plain, simple writing. If you wrote it yourself, you can appeal and a person will take a look.",
  "error": null,
  "verdict": ""
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 200,
  "content_id": "207c60c1-f84b-4258-b8d2-9fdb7844d0c6",
  "creator_id": "attacker_MF06",
  "guess": "ai",
  "confidence": 0.9978,
  "model_score": 0.9969,
  "style_score": 1.0,
  "label": "Our tools think this was probably written with the help of AI. They can be wrong, especially with plain, simple writing. If you wrote it yourself, you can appeal and a person will take a look.",
  "error": null,
  "verdict": ""
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 200,
  "content_id": "9748a4c6-88cf-4234-9644-fcdf78f4ca52",
  "creator_id": "attacker_MF07",
  "guess": "ai",
  "confidence": 0.9345,
  "model_score": 0.9064,
  "style_score": 1.0,
  "label": "Our tools think this was probably written with the help of AI. They can be wrong, especially with plain, simple writing. If you wrote it yourself, you can appeal and a person will take a look.",
  "error": null,
  "verdict": ""
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 413,
  "content_id": null,
  "creator_id": "attacker_MF08",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 400,
  "content_id": null,
  "creator_id": {
    "id": "x"
  },
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 200,
  "content_id": "cc5827e8-3775-4fb9-90d2-e1a62cfeca33",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.3725,
  "model_score": 0.0287,
  "style_score": 0.75,
  "label": "We can't tell whether this was written by a person or with AI, so we haven't made a call. Nothing is wrong with your work. If you'd like someone to look at it, you can appeal.",
  "error": null,
  "verdict": ""
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 200,
  "content_id": "aaee95f0-4afa-490b-8337-26f6b62b7b13",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.3725,
  "model_score": 0.0287,
  "style_score": 0.75,
  "label": "We can't tell whether this was written by a person or with AI, so we haven't made a call. Nothing is wrong with your work. If you'd like someone to look at it, you can appeal.",
  "error": null,
  "verdict": ""
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 200,
  "content_id": "03f60e28-d963-43d8-afcb-053ecb671ef8",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.3725,
  "model_score": 0.0287,
  "style_score": 0.75,
  "label": "We can't tell whether this was written by a person or with AI, so we haven't made a call. Nothing is wrong with your work. If you'd like someone to look at it, you can appeal.",
  "error": null,
  "verdict": ""
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 200,
  "content_id": "10702dbc-997a-4d39-be12-ccfc4128dd33",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.3725,
  "model_score": 0.0287,
  "style_score": 0.75,
  "label": "We can't tell whether this was written by a person or with AI, so we haven't made a call. Nothing is wrong with your work. If you'd like someone to look at it, you can appeal.",
  "error": null,
  "verdict": ""
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 200,
  "content_id": "c656e97e-914f-495e-b437-6400f28f8579",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.3725,
  "model_score": 0.0287,
  "style_score": 0.75,
  "label": "We can't tell whether this was written by a person or with AI, so we haven't made a call. Nothing is wrong with your work. If you'd like someone to look at it, you can appeal.",
  "error": null,
  "verdict": ""
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```
