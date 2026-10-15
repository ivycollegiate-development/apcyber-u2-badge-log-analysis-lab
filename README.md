# apcyber-u2-badge-log-analysis-lab — Badge Log Analysis Lab

AP Cybersecurity Unit 2, Lesson 13. A synthetic badge access log and a working detection script.

**You do not write any code in this lab.** Four detection rules are already written. You run them over three weeks of access events, and then you do the hard part: decide which of the hits are findings and which are people going about their day.

**834 badge events, 60 badges, 5 doors, 15 school days (2026-09-29 → 2026-10-15).** The data is `badge_log.csv`. The script is `badge_analysis.py`.

## Your job

1. **Fork** this repo to your account.
2. Open it in VS Code — a Codespace from the repo page, or on the class server at `vscode.ivycollegiate.org` (log in with your school account). `git pull` first, always.
3. Run the script in the **terminal panel**, not a notebook, so you watch the four CSVs land on disk:

   ```
   python3 badge_analysis.py
   ```

   The server has Python 3.11 with **pandas** preinstalled. Do not edit the script.
4. The four detections run, print their hits, and write **`results_task1.csv`** … **`results_task4.csv`**.
5. Commit all four files. They are the graded deliverable.
6. Then read your own output. This is the actual assignment.

## The schema

```
timestamp, badge_id, door, result
2026-09-29T07:41:12, B-1042, MAIN-EAST, granted
```

- `result` is `granted` or `denied`
- `door` is one of `MAIN-EAST`, `MAIN-WEST`, `LIB-ENTRY`, `SCI-ANNEX`, `SERVER-RM`
- Timestamps are ISO local, 24-hour, no timezone

**Three things to notice about this data before you trust any output:**

1. **The file is not sorted by time.** The script sorts it on load. If you ever write your own analysis on this log, that is the first line you need.
2. `timestamp` is a string until you tell pandas it is a timestamp.
3. A `granted` event does not mean someone walked through. It means a **credential** was accepted. That distinction is the whole of task 1.

## The four detections

| Task | Detection | Output file | Rows it returns |
|---|---|---|---|
| 1 | **Shared badges** — one credential at two doors far enough apart that the gap between them is too short to walk | `results_task1.csv` | 29 |
| 2 | **Tailgating** — bursts of `granted` events within 15 seconds of each other at the same reader | `results_task2.csv` | 8 |
| 3 | **Failed then success** — a `denied` event followed by a `granted` event on the same badge, with the count of denials that came first | `results_task3.csv` | 29 |
| 4 | **After-hours access** — anything outside 07:00–18:00 on a weekday, and anything at all on a weekend | `results_task4.csv` | 13 |

The thresholds are visible in the script and they are **judgement calls, not facts**: `TRAVEL_SECONDS = 240` for task 1, `gap_seconds=15` for task 2. If you think a threshold is wrong, say so with evidence — that argument is worth more than the output.

`DOOR_ZONE` is the key idea for task 1: a shared badge means the *same credential* at *two places far apart*, so you need a notion of which doors are far apart. Two doors on the same facade should never fire the rule — the zone map is what stops them.

**A rule that finds something is not the same as a rule that found the right thing.** Task 2 is the clear example: the rule is looking at one reader at a time, so anything spanning four *different* doors in half a minute is invisible to it. Watch for that shape in your own output and say so in the debrief.

## The real skill is subtraction

**Every one of these detections has a benign twin in the data.** A guard on a patrol sweep. A janitor. A teacher who badged into the annex on the way to the gym, then out the far door because it is closer to the car park. Three people leaving a staff meeting together.

Your job is not to report every hit. Your job is to decide which hits you are reporting, and to say why the rest is noise. In task 3 the rule returns 29 rows and **one** of them is worth acting on — the difference is a single column (`prior_denials`). In task 4 the rule returns 13 rows and two are candidates. Finding the difference between those rows is the assignment; the rules are just what gets you the list.

**How do you avoid alert fatigue?** Baseline first — what does normal look like for *this* door, *this* badge, *this* hour? Then thresholds that key on **deviation** rather than on absolute events — the guard's punctuality is what makes him benign; a credential that is *not* punctual is not. Then a hard volume budget: if a rule fires more than a handful of times a week, it is a **report**, not an **alert**, and a report can wait until morning.

**The honest limitation:** all four detections read a log, and **a log records credentials, not people.** Every finding you write up is a statement about a card.

## What you hand in

1. The four `results_taskN.csv` files, committed.
2. How many hits each detection produced, and which one produced the most *useful* output.
3. **A specific false positive from your own output**, named by badge, door, and timestamp, with a sentence on why it is not a finding.

## Files

| File | What it is |
|---|---|
| `badge_log.csv` | The data. Do not edit it. |
| `badge_analysis.py` | The four detection rules. Read it. Do not edit it. |
| `evidence_packet_template.md` | The structure for the L14 correlation exercise, where you reconstruct a timeline from four sources. Read it before Monday. |

## The gate

- All four `results_taskN.csv` files exist and are committed.
- Each contains what its task says it should — not just a bare count.
- Task 1 shows the gap in seconds; task 2 shows the events per burst; task 3 shows the count of prior denials; task 4 shows badge, door, and timestamp.
- You can name a specific false positive from your own output and explain why it is not a finding.
