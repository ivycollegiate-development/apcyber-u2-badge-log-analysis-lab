"""
AP Cybersecurity — Unit 2, Lesson 13
Badge Log Analysis Lab

YOU DO NOT WRITE ANY CODE IN THIS FILE. The four detections are already
written. Your job is to RUN them and then defend the output.

Run in the terminal:   python3 badge_analysis.py
Run it in the terminal panel, not in a notebook, so you watch the four
results_*.csv files actually land on disk.

What the script does, in order:
  1. loads badge_log.csv and sorts it by timestamp
  2. runs four detection rules over the whole log
  3. prints the hits from each rule and saves them to results_task1-4.csv

Then the hard part starts: deciding which of those hits are real findings and
which are people going about their day.
"""

import pandas as pd

# ---------------------------------------------------------------- load + sort
# timestamp is a STRING until you tell pandas it is a timestamp.
# THE FILE IS NOT SORTED BY TIME, so we sort it here. Every windowing
# calculation below depends on this line.
log = pd.read_csv("badge_log.csv", parse_dates=["timestamp"])
log = log.sort_values("timestamp").reset_index(drop=True)

print(f"{len(log)} events, {log['badge_id'].nunique()} badges, "
      f"{log['door'].nunique()} doors")
print(log["result"].value_counts())
print(log["door"].value_counts())

# A `granted` event does not mean someone walked through. It means a CREDENTIAL
# was accepted. Keep that in mind when you read task 1's output.

# Rough door-to-door walk time across the building, in seconds. A credential seen
# at two doors further apart than this, inside a shorter window, is one of two
# things: a shared badge, or a person who moved fast. You have to tell them apart.
TRAVEL_SECONDS = 240

# Which doors are far apart from each other. "A" and "B" are next door;
# "A" and "D" are opposite ends of the building. This map is scaffolding —
# if you think it is wrong, argue about it, because you are arguing about the
# right thing.
DOOR_ZONE = {"MAIN-EAST": "A", "MAIN-WEST": "A", "LIB-ENTRY": "B",
             "SCI-ANNEX": "C", "SERVER-RM": "D"}


# ============================================================ TASK 1
def shared_badges(df, window_minutes=5):
    """
    SHARED BADGES — one credential at two doors that are far apart.

    QUESTION: Is any single badge_id appearing at two doors further apart than
    TRAVEL_SECONDS, within a window too short to walk between them?

    OUTPUT: one row per hit, with the columns
        badge_id, door_a, ts_a, door_b, ts_b, gap_seconds

    THE HARD PART: how many hits came back, and whether each one is really a
    second person. A `granted` does not mean a body moved. Decide which hits you
    are REPORTING and why the rest is noise. That decision is the task.
    """
    hits = []
    for badge, grp in df.groupby("badge_id"):
        rows = grp.sort_values("timestamp").to_dict("records")
        for i, a in enumerate(rows):
            for b in rows[i + 1:]:
                gap = (b["timestamp"] - a["timestamp"]).total_seconds()
                if gap > window_minutes * 60:
                    break            # rows are sorted: nothing later can fit
                if a["door"] == b["door"]:
                    continue          # same reader, not a second location
                if DOOR_ZONE[a["door"]] == DOOR_ZONE[b["door"]]:
                    continue          # zones are adjacent, so walkable
                if gap < TRAVEL_SECONDS:
                    hits.append({"badge_id": badge, "door_a": a["door"],
                                 "ts_a": a["timestamp"], "door_b": b["door"],
                                 "ts_b": b["timestamp"], "gap_seconds": int(gap)})
    return pd.DataFrame(hits, columns=["badge_id", "door_a", "ts_a",
                                       "door_b", "ts_b", "gap_seconds"])


# ============================================================ TASK 2
def tailgating(df, gap_seconds=15):
    """
    TAILGATING — rapid successive entries on one credential.

    QUESTION: At a single reader, are there bursts of `granted` events within
    a few seconds of each other?

    OUTPUT: one row per burst, with the columns
        door, start, end, events
    `events` is the count in the burst.

    THE HARD PART: each extra event in a burst is one credential plus one person
    who did not badge. Bursts of 3+ at SERVER-RM or a staff entrance are the ones
    worth reading out. A burst of 2 at the library door at lunch is staffing.

    Note the filter to result == "granted" FIRST — a denied event followed
    immediately by a granted one is task 3's pattern, not a tailgate.
    """
    hits = []
    for door, grp in df[df["result"] == "granted"].groupby("door"):
        rows = grp.sort_values("timestamp").to_dict("records")
        burst = [rows[0]] if rows else []
        for prev, cur in zip(rows, rows[1:]):
            if (cur["timestamp"] - prev["timestamp"]).total_seconds() <= gap_seconds:
                burst.append(cur)
            else:
                if len(burst) > 1:
                    hits.append({"door": door, "start": burst[0]["timestamp"],
                                 "end": burst[-1]["timestamp"],
                                 "events": len(burst)})
                burst = [cur]
        if len(burst) > 1:
            hits.append({"door": door, "start": burst[0]["timestamp"],
                         "end": burst[-1]["timestamp"], "events": len(burst)})
    return pd.DataFrame(hits, columns=["door", "start", "end", "events"])


# ============================================================ TASK 3
def failed_then_success(df):
    """
    FAILED THEN SUCCESS — credential probing.

    QUESTION: Does a `denied` event get followed by a `granted` event ON THE
    SAME BADGE — and how many denials came first?

    OUTPUT: one row per hit, with the columns
        badge_id, door, granted_at, prior_denials

    THE HARD PART: `prior_denials` is the whole point. One denial followed by a
    success is somebody fat-fingering a door code, and it happens to everyone
    every week. Three or four denials in a row followed by a success is somebody
    working out which badge works where. The count separates a fumble from a
    systematic attempt; a rule that ignores the count will fire forever.

    Note the door too: a person denied at one door and then badged successfully
    somewhere else has told you something the count alone does not.
    """
    hits = []
    for badge, grp in df.groupby("badge_id"):
        rows = grp.sort_values("timestamp").to_dict("records")
        denies = 0
        for r in rows:
            if r["result"] == "denied":
                denies += 1
            else:
                if denies:
                    hits.append({"badge_id": badge, "door": r["door"],
                                 "granted_at": r["timestamp"],
                                 "prior_denials": denies})
                denies = 0
    return pd.DataFrame(hits, columns=["badge_id", "door", "granted_at",
                                       "prior_denials"])


# ============================================================ TASK 4
def after_hours(df, start="07:00", end="18:00"):
    """
    AFTER-HOURS ACCESS — outside staffed hours.

    QUESTION: What is accessed outside 07:00-18:00 on a weekday, or at all
    on a weekend?

    OUTPUT: badge_id, door, timestamp for each event.

    THE HARD PART: this rule is trivial to code and is where the actual analyst
    skill lives. The list you get includes the legitimate overnight population —
    cleaners, the security guard on the 22:00-06:00 shift, staff with known early
    or late schedules. SUBTRACT the known-benign population and report what is
    left. The code is four lines; the judgement of who is known-benign and who is
    not is the task.

    Do the subtraction visibly — a second script, a copy of the de-noised CSV, or
    your commit message — so the debrief can talk about it.
    """
    ts = df["timestamp"]
    mins = ts.dt.hour * 60 + ts.dt.minute
    lo = int(start[:2]) * 60 + int(start[3:])
    hi = int(end[:2]) * 60 + int(end[3:])
    weekend = ts.dt.dayofweek >= 5
    return df[weekend | (mins < lo) | (mins > hi)][["badge_id", "door", "timestamp"]]


# ---------------------------------------------------------------- main
if __name__ == "__main__":
    print("\n=== TASK 1: shared badges ===")
    t1 = shared_badges(log)
    print(t1)
    t1.to_csv("results_task1.csv", index=False)

    print("\n=== TASK 2: tailgating ===")
    t2 = tailgating(log)
    print(t2)
    t2.to_csv("results_task2.csv", index=False)

    print("\n=== TASK 3: failed then success ===")
    t3 = failed_then_success(log)
    print(t3)
    t3.to_csv("results_task3.csv", index=False)

    print("\n=== TASK 4: after-hours access ===")
    t4 = after_hours(log)
    print(t4)
    t4.to_csv("results_task4.csv", index=False)

    print("\nDone. Now the real work: which of these are findings, and which "
          "are people going about their day? Name a specific false positive "
          "from your own output.")
