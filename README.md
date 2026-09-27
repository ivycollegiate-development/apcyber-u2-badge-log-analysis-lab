# apcyber-u2-badge-log-analysis-lab — Badge Log Analysis Lab

AP Cybersecurity Unit 2, Lesson 13. This repo holds a synthetic badge access log and a starter script for writing four detection rules against it.

**~500 badge events, 5 doors, 3 weeks.** The file is `badge_log.csv`. The starter is `badge_analysis.py`.

## Your job

1. **Fork** this repo to your account.
2. Open `badge_analysis.py` in VS Code — in Codespaces, or on the class server at `vscode.ivycollegiate.org` (log in with your school account). `git pull` first, always.
3. Read the schema at the top of the script, then run it in the **terminal panel**, not a notebook: `python3 badge_analysis.py`. The server has Python 3.11 with **pandas** preinstalled. Use pandas.
4. Work the four tasks. Each one is a function with a `# TODO` body and a comment block explaining the question it answers and the output it must produce.
5. Save your results to **`results_task1.csv`** … **`results_task4.csv`** in this repo.

## The schema

```
timestamp, badge_id, door, result
2026-09-29T07:41:12, B-1042, MAIN-EAST, granted
```

- `result` is `granted` or `denied`
- `door` is one of `MAIN-EAST`, `MAIN-WEST`, `LIB-ENTRY`, `SCI-ANNEX`, `SERVER-RM`
- Timestamps are ISO local, 24-hour, no timezone

**Three things that break a first script:**

1. **The file is not sorted by time.** Sort it first, or every windowing calculation is wrong. This is the bug that costs the most time in this lab.
2. `timestamp` is a string until you tell pandas it is a timestamp. Everything downstream depends on it.
3. A `granted` event does not mean someone walked through. It means a **credential** was accepted. Keep that assumption in mind for task 1.

## The four detections

| Task | Detection | Output file |
|---|---|---|
| 1 | **Shared badges** — one credential used at two doors that are far apart, inside a window too short to walk between them | `results_task1.csv` |
| 2 | **Tailgating** — successive `granted` events within seconds of each other at the same reader, one credential. Each pair is a credential plus an unlogged person | `results_task2.csv` |
| 3 | **Failed then success** — a `denied` event followed within 5 minutes by a `granted` event **on the same badge**. The count of denials is what separates one fumble from a systematic attempt | `results_task3.csv` |
| 4 | **After-hours access** — anything outside 07:00–18:00 on a weekday, and anything on a weekend | `results_task4.csv` |

`DOOR_ZONE` in the starter is the key idea for task 1: a shared badge means the *same credential* at *two places*, so you need a notion of which doors are far apart. Supplying the zone map is a scaffolding decision — a group that argues about it is arguing about the right thing.

## The real skill is subtraction

You are not hunting for a single event. You are writing **detection rules** — the kind an automated monitoring system would run at scale. If you cannot express the check in code, nobody downstream can run it either.

**Every one of these detections has a benign twin in the data.** A guard doing a patrol sweep. A janitor. A teacher who badged into the annex on the way to the gym. A person who badged out at the far door because it is closer to the car park. Your job is not to report every hit — your job is to decide which hits you are reporting, and to say why the rest is noise.

**How do you avoid alert fatigue?** Baseline first — what does normal look like for *this* door, *this* badge, *this* hour? Then set thresholds that key on **deviation** rather than on absolute events, then impose a hard volume budget. If a rule fires more than a handful of times a week, it is a **report**, not an **alert** — and a report can wait until morning while an alert cannot. And the alert at 3 AM is worthless if there is nobody to receive it.

**The honest limitation:** all four detections read a log, and **a log records credentials, not people.**

## Debrief

Report how many hits each of your four detections produced, and which single detection produced the most *useful* output. Then be ready for:

- **What would a false positive look like here?** Name a specific one from your own results.
- **How do you avoid alert fatigue?**

## Files

| File | What it is |
|---|---|
| `badge_log.csv` | The data. Do not edit it. |
| `badge_analysis.py` | Starter script. Complete the four TODOs. |
| `SOLUTIONS.md` | **The answer key.** Expected findings for all four tasks, with badge IDs, doors, and timestamps — plus the benign twins and why each is a false positive. It is in this public repo because the lab is about *reasoning about output*, not about hiding it. **Attempt all four tasks before you open it.** |
| `evidence_packet_template.md` | The structure for the L14 correlation exercise, where you reconstruct a timeline from four sources. Read it before Monday. |

## The gate

- All four `results_taskN.csv` files exist and are committed.
- Each contains what its task comment says it should — not just a bare count.
- Task 1's output shows the gap in seconds; task 2's shows the events per burst; task 3's shows the count of prior denials; task 4's shows badge, door, and timestamp.
- You can name a specific false positive from your own output and explain why it is not a finding.
