# SOLUTIONS — Badge Log Analysis Answer Key

> **This is the answer key.** It is in the public repo because this lab is about *reasoning about output* — deciding what is a finding and what is a false positive — and you cannot reason about output you were not allowed to see. Hiding it would not make the lab harder; it would only make it unteachable.
>
> **Attempt all four tasks before you open this file.** Run your detections, write your results to `results_taskN.csv`, and form your own opinion on which hits are real. Then come here and check yourself. The most useful thing you can do in the debrief is argue with this file using evidence from your own run.

**The data:** 828 events, 45 badges, 5 doors, 15 school days (2026-09-29 through 2026-10-16). Four anomalies are planted, one per task. Benign twins are also planted deliberately, so the false-positive discussion has real material — the detections are *supposed* to return them.

**Important:** your hit counts will not match these exactly. The counts depend on your thresholds, and thresholds are a judgement call. What must match is the **planted events** and your reasoning about the noise around them.

---

## Task 1 — Shared badges

### The planted anomaly

| badge_id | door_a | ts_a | door_b | ts_b | gap_seconds |
|---|---|---|---|---|---|
| **B-0141** | MAIN-EAST (zone A) | 2026-10-06 02:40:12 | SERVER-RM (zone D) | 2026-10-06 02:43:00 | **168** |

- **Tuesday 2026-10-06, 02:40 — about 2:40 in the morning.**
- `TRAVEL_SECONDS = 240`. The gap is 168 seconds, so the badge was accepted at both ends of the building in under three minutes. A person cannot walk that in the time available, including badging, opening the door, and turning around.
- **This is a real finding.** One credential at two distant doors, overnight, in a window too short to traverse. It is either a shared badge (someone let a colleague in and handed the card over) or a cloned card. Both are reportable.

**What it does not establish:** *who* was at each reader. The log records credentials, not people. Two people, one card; one person, one card and a very fast walk; a cloned card and two different people — all three produce this same row. This is exactly the ambiguity the L14 correlation exercise resolves.

### The false positive you will also get

| badge_id | door_a | ts_a | door_b | ts_b | gap_seconds | Verdict |
|---|---|---|---|---|---|---|
| **B-0022** | MAIN-WEST (zone A) | 2026-10-07 16:03:00 | MAIN-EAST (zone A) | 2026-10-07 16:05:00 | **120** | **FALSE POSITIVE** |

- **Why it is a false positive, and this is the whole lesson of task 1:** `DOOR_ZONE["MAIN-WEST"] == DOOR_ZONE["MAIN-EAST"] == "A"`. The two main staff entrances are **next to each other** — same side of the building, same zone. The zone check is supposed to skip this pair, and it does.
- If your zone map is missing or wrong, this pair lands in your results and you will have a hit that looks exactly like a real one. **That is the bug the zone map exists to prevent**, and if you hit it, you have learned why the scaffolding was there.
- Even if it did land in your output, the correct call is still "not a finding" — a 2-minute gap between two doors on the same facade is a person who went out one door and in the other.

> **This is the false positive the debrief is asking for.** Name it, and explain that the *zone map* is what separates it from B-0141. It is the same shape, the same gap, the same badge pattern — the only difference is whether the two doors are far apart.

---

## Task 2 — Tailgating

Start here, because it is the case a straightforward detector catches.

### The easy planted anomaly (Burst 0 — start here)

**B-0011 / B-0019 / B-0026, Friday 2026-10-02, 11:47, ONE door in 28 seconds:**

| badge_id | door | timestamp | seconds from previous |
|---|---|---|---|
| B-0011 | LIB-ENTRY | 2026-10-02 11:47:20 | - |
| B-0019 | LIB-ENTRY | 2026-10-02 11:47:34 | 14 |
| B-0026 | LIB-ENTRY | 2026-10-02 11:47:48 | 14 |

Three *different* badges, one reader, no badging out, 28 seconds total. Three
people, one door, too fast, and the third never badged. **This is tailgating as
your lesson defines it, and a same-door burst detector catches it on the first
try.** If your task-2 output is empty, you have a bug, not an empty dataset.

### The hard planted anomalies (two travel-speed bursts)

Both of these span four *different* doors, so a same-door burst detector returns
nothing for either. They are caught by the task-1 travel-speed logic. Work them
only after Burst 0 is working.

**Burst A — B-0203, Thursday 2026-10-08, 09:12, four doors in 27 seconds:**

| badge_id | door | timestamp | seconds from previous |
|---|---|---|---|
| B-0203 | MAIN-EAST | 2026-10-08 09:12:03 | — |
| B-0203 | LIB-ENTRY | 2026-10-08 09:12:14 | 11 |
| B-0203 | SCI-ANNEX | 2026-10-08 09:12:25 | 11 |
| B-0203 | MAIN-WEST | 2026-10-08 09:12:36 | 11 |

| door | start | end | events |
|---|---|---|---|
| *(see per-door rows below)* | | | |

> **Note on the shape of this one:** a strict same-door burst detector returns **four single-event bursts or nothing** for B-0203, because these are four *different* doors. The anomaly is a credential racking up four doors in 27 seconds — which is a travel-speed violation, not a same-reader tailgate. Your task-1 logic (with `TRAVEL_SECONDS`) catches this; a task-2 detector that groups by door will not. **If your task 2 output is empty, check whether that is because there is nothing there or because the rule is looking for the wrong shape.** Reporting "no tailgating found" when the shape of the rule cannot detect the planted event is a real analytical error, and it is one of the things to raise in the debrief.

**Burst B — B-0307, Tuesday 2026-10-13, 13:05, four events in 27 seconds:**

| badge_id | door | timestamp | seconds from previous |
|---|---|---|---|
| B-0307 | LIB-ENTRY | 2026-10-13 13:05:40 | — |
| B-0307 | SCI-ANNEX | 2026-10-13 13:05:49 | 9 |
| B-0307 | LIB-ENTRY | 2026-10-13 13:05:58 | 9 |
| B-0307 | MAIN-EAST | 2026-10-13 13:06:07 | 9 |

- LIB-ENTRY → SCI-ANNEX → LIB-ENTRY → MAIN-EAST in 27 seconds, at lunchtime on a Tuesday. **This is not a person.** There is no walk that does that. It is a badge being carried to make a record, or a reader stuck in a retry loop, or a genuine credential test.

**What a same-door burst detector *will* find** are pairs of genuine `granted` events seconds apart at the same reader — the tailgating pattern as the lesson defines it. Those are mostly two-person rushes at a staff door during the morning arrival wave, and they are **noise at volume**. A burst of 2 at a library door at 12:40 is a lunch queue.

### The benign twin: the staff meeting

| badge_id | door | timestamp |
|---|---|---|
| B-0031 | MAIN-EAST | 2026-10-09 16:30:00 |
| B-0038 | MAIN-EAST | 2026-10-09 16:30:11 |
| B-0043 | MAIN-EAST | 2026-10-09 16:30:22 |

- **Three different badges at one door in 22 seconds, 16:30 on a Friday.** To a
  same-door burst detector this looks *exactly* like Burst 0 — different badges,
  one door, under a minute, no badging out. It is not tailgating. It is three
  teachers leaving a staff meeting together, which is what people do at 16:30.
- **Why it is not a finding:** nothing in the log distinguishes it from Burst 0.
  Same shape, same columns, same threshold. The only things separating them live
  outside the data — the staff meeting calendar, the 16:30 slot, the fact that it
  is the last event of the day for all three badges. **This is the strongest
  argument in the lab for why a badge log alone is not a detection system.** A
  rule that catches Burst 0 will catch this forever, and someone will turn that
  rule off within a month.
- **A third same-door burst exists and is also noise:** B-1009 / B-1023 / B-1019
  at MAIN-WEST, 2026-10-13 07:47–07:48, 45 seconds. Morning arrival wave. Do not
  report it.

### The benign twin: the guard patrol sweep

| badge_id | door | timestamp |
|---|---|---|
| B-0100 | MAIN-EAST | 2026-10-15 22:00:00 |
| B-0100 | MAIN-WEST | 2026-10-15 22:07:00 |
| B-0100 | LIB-ENTRY | 2026-10-15 22:14:00 |
| B-0100 | SCI-ANNEX | 2026-10-15 22:21:00 |

- **B-0100 is the security guard on the 22:00–06:00 shift**, doing a patrol walk. Every seven minutes, four doors, in order, overnight. This is the textbook benign twin: it looks exactly like a shared badge and a four-door burst, and it is a person doing their job.
- **Why it is not a finding:** the *regularity* gives it away. Seven-minute intervals, same door order, same badge. A credential test is not punctual. **This is your first lesson in baselining — a rule that fires on absolute events will catch the guard forever; a rule that fires on deviation will not.**
- The 7-minute spacing is *above* a 10-second tailgate threshold, so a correctly-tuned task-2 rule will not fire on it — but a loose threshold will, and the guard is why the threshold matters.

---

## Task 3 — Failed then success

### The planted anomaly

| badge_id | door | granted_at | prior_denials |
|---|---|---|---|
| **B-0087** | SERVER-RM | 2026-10-01 23:21:30 | **3** |

Full sequence, all at SERVER-RM, all Thursday evening:

| timestamp | result |
|---|---|
| 2026-10-01 23:15:00 | denied |
| 2026-10-01 23:17:00 | denied |
| 2026-10-01 23:19:00 | denied |
| 2026-10-01 23:21:30 | **granted** |

- **Three denials, two minutes apart, then a success two and a half minutes after the last one.** B-0087 is not authorised for the basement server room, and whoever held it kept trying.
- **This is a real finding, and the count is what makes it one.** One denial then a success is a fat-fingered door code — it happens to everybody, every week, and it is exactly the event that gets a rule switched off. Three denials in a row is somebody working out whether the card works.
- Note the **door is constant**: they did not move on after being denied, they stayed at the server room. Combined with the 23:21 hour, that is a probe at an unattended asset.

### The false positives

The background denials in the log (2–5 per day, scattered across `DOORS[:4]`, random badges) will all appear here. Every one of them will eventually be followed by that badge's next `granted` event somewhere, often within the 5-minute window.

- **These are single denials with `prior_denials = 1`.** That is a fumble, not a probe.
- **A `prior_denials = 1` row is not a finding.** A rule that reports every failed-then-success pair will fire several times a week and be muted by the end of the month.
- **The rule that works:** report `prior_denials >= 3`, or report a denied → granted transition **at the same door the denials occurred at**, or both. B-0087 is the only row that survives either filter.

> **The generalisable lesson:** the naive implementation of "denied then granted" is a high-volume, low-value alert. The *count* and the *door consistency* are what turn it into a signal. This is the concrete version of "key on deviation, not on absolute events."

---

## Task 4 — After-hours access

The 07:00–18:00 weekday filter returns the entire overnight population: the guard patrol, the cleaners, and the two planted events. **The code is three lines. The subtraction is the task.**

### The planted anomalies

| badge_id | door | timestamp | Note |
|---|---|---|---|
| **B-0125** | LIB-ENTRY | 2026-10-09 22:48:00 | Friday night, 10:48 p.m. |
| **B-0192** | MAIN-EAST | 2026-10-14 04:33:00 | **Wednesday, 4:33 a.m.** |

- **B-0125** is a single late-evening library entry, just under 5 hours after close. Suspicious but weak on its own — students study late, and a library badge at 22:48 is not a crime.
- **B-0192 is the interesting one.** A main staff entrance at **04:33 on a Wednesday morning** is a long way from any legitimate schedule. B-0192 does not appear anywhere in the guard pattern (B-0100) and is not a cleaner badge.
- **Neither of these is proven.** B-0192 could be an employee on a shift pattern nobody documented, a keyholder doing an early building check, or a badge that was handed to someone who should not have had it. Your candidate list is a *candidate list*, and saying "this is a candidate list" rather than "this person is an intruder" is the professionally correct framing.

### The benign population you must subtract

| badge_id | Who | Why it is benign |
|---|---|---|
| **B-0100** | Security guard, 22:00–06:00 rotation | Patrol sweep, four doors, 7-minute intervals, every night of the week. 30 events. By far the largest block in your after-hours output. |
| **B-0044** | Janitor | LIB-ENTRY, 2026-10-12 23:10:00. Cleaning staff work overnight when the building is empty. |
| **B-0087** | *(the task-3 credential)* | Its after-hours event is already the more serious finding; do not double-count it as two separate anomalies. |
| **~40 other badges** | Employees with unlogged early or late schedules | The log contains legitimate events between 05:00 and 07:45 and after 18:00 from random badges. There is no shift roster in this dataset, so **you cannot subtract these from evidence alone** — the honest move is to name them as a known population that needs an HR roster to resolve, and to say so in your write-up. |

### What the subtraction should leave

**Two candidate rows: B-0125 and B-0192.** B-0192 is the one worth a follow-up.

**If your subtraction leaves 200+ rows, you did not subtract the guard.** B-0100 is a third of the overnight population and it should be obvious once you look — same badge, same seven-minute cadence, same door order. If you never grouped by badge before filtering by time, that is the habit to fix.

> **The honest limitation of task 4:** there is no roster in this dataset. "Legitimate overnight staff" is an assumption you are importing from outside the data. A real analyst would join this table to the badge-holder roster and the shift schedule, and would get a much shorter list. Saying "I subtracted the guard and the janitor, and the remaining 40 early-morning events cannot be resolved without a shift roster" is a stronger analysis than pretending you resolved them.

---

## Cross-task summary

| Task | Planted finding | Benign twin in the data | Distinguishing signal |
|---|---|---|---|
| 1 — Shared badges | B-0141, MAIN-EAST → SERVER-RM, 168s, 02:40 | B-0022, MAIN-WEST → MAIN-EAST, 120s | Door zone (A/A vs A/D). Same shape, different distance. |
| 2 — Tailgating | B-0307, 4 doors in 27s; B-0203, 4 doors in 27s | B-0100 guard patrol, 4 doors on exact 7-min intervals | Regularity and interval. A probe is not punctual. |
| 3 — Failed → success | B-0087, 3 denials at SERVER-RM then granted | ~3/day background denials, all `prior_denials = 1` | The **count**, and same-door consistency. |
| 4 — After-hours | B-0192 (04:33), B-0125 (22:48) | B-0100 guard (30 events), B-0044 janitor, ~40 unlogged staff | Know your baseline population. Subtract it explicitly. |

## Debrief answers

**What would a false positive look like here?** Name a specific one from your own results. The four in this dataset are the guard patrol sweep, the janitor's single overnight entry, the two-door MAIN-EAST/MAIN-WEST walk by one person, and the background single-denial fumbles. All four are in the data specifically so this conversation has real material.

**How do you avoid alert fatigue?** Baseline first — what does normal look like for *this* door, *this* badge, *this* hour. Then thresholds that key on **deviation** rather than absolute events (the guard's regularity is what makes it benign; a burst at an irregular cadence is not). Then a **hard volume budget**: if a rule fires more than a handful of times a week, it is a **report**, not an **alert** — and a report can wait until morning while an alert cannot. And the alert at 3 AM is worthless if there is nobody to receive it.

**The limitation that runs under all four tasks:** a log records **credentials, not people.** Every finding above is a statement about a card, not about a human. That gap gets resolved — or made permanent — by correlating with video, which is the next exercise.
