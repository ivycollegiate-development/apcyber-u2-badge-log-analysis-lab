"""
AP Cybersecurity — Unit 2, Lesson 13
Badge Log Analysis Lab

You are writing DETECTION RULES, not looking for one event. Anything you can
express here, an automated monitoring system can run at scale.

Run in the terminal:   python3 badge_analysis.py
Do not run this in a notebook — you want to see it fail and fix it.
"""

import pandas as pd

# ---------------------------------------------------------------- load + sort
# timestamp is a STRING until you tell pandas it is a timestamp.
# THE FILE IS NOT SORTED BY TIME. Sort it first or every windowing calculation
# below is wrong. This is the bug that costs the most time in this lab.
log = pd.read_csv("badge_log.csv", parse_dates=["timestamp"])
log = log.sort_values("timestamp").reset_index(drop=True)

print(f"{len(log)} events, {log['badge_id'].nunique()} badges, "
      f"{log['door'].nunique()} doors")
print(log["result"].value_counts())
print(log["door"].value_counts())

# A `granted` event does not mean someone walked through. It means a CREDENTIAL
# was accepted. Keep that in mind for task 1.

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

    WHAT TO OUTPUT: one row per hit, with the columns
        badge_id, door_a, ts_a, door_b, ts_b, gap_seconds

    WHAT TO THINK ABOUT: how many hits come back. Most groups get a handful.
    Some of them are legitimately a person who walked — a route where two doors
    are close, or a long walk done quickly. A `granted` does not mean a body
    moved. Decide which hits you are REPORTING and why the rest is noise.
    That decision is the task; the loop is not.

    Write to: results_task1.csv
    """
    # TODO: group by badge_id, sort each group by timestamp, and compare every
    # pair of consecutive events in a window. Skip pairs at the same door, and
    # skip pairs whose DOOR_ZONE values are equal (too close together to matter).
    # Flag any remaining pair whose gap is under TRAVEL_SECONDS.
    #
    # Hint: for consecutive-event gaps only, you can vectorise with
    #   df.groupby("badge_id")["timestamp"].diff().dt.total_seconds()
    # and then look up the row that produced each diff. The nested-loop version
    # in the lesson notes is clearer if you are stuck.
    hits = []
    return pd.DataFrame(hits, columns=["badge_id", "door_a", "ts_a",
                                       "door_b", "ts_b", "gap_seconds"])


# ============================================================ TASK 2
def tailgating(df, gap_seconds=10):
    """
    TAILGATING — rapid successive entries on one credential.

    QUESTION: At a single reader, are there bursts of `granted` events within
    a few seconds of each other?

    WHAT TO OUTPUT: one row per burst, with the columns
        door, start, end, events
    `events` is the count in the burst.

    WHAT TO THINK ABOUT: each pair of events in a burst is one credential plus
    one person who did not badge. Bursts of 3+ at SERVER-RM or a staff entrance
    are the ones worth reading out. A burst of 2 at a library door in the middle
    of a lunch period is a coincidence of staffing.

    Filter to result == "granted" FIRST — a denied event followed immediately by
    a granted one is task 3's pattern, not a tailgate.

    Write to: results_task2.csv
    """
    # TODO: for each door, walk the granted events in timestamp order and track
    # a running burst. If the gap from the previous event is <= gap_seconds, the
    # burst continues; otherwise close the burst and start a new one.
    # Emit any burst with more than one event.
    hits = []
    return pd.DataFrame(hits, columns=["door", "start", "end", "events"])


# ============================================================ TASK 3
def failed_then_success(df, window_minutes=5):
    """
    FAILED THEN SUCCESS — credential probing.

    QUESTION: Does a `denied` event get followed within 5 minutes by a `granted`
    event ON THE SAME BADGE?

    WHAT TO OUTPUT: one row per hit, with the columns
        badge_id, door, granted_at, prior_denials

    WHAT TO THINK ABOUT: `prior_denials` is the whole point. One denial followed
    by a success is somebody fat-fingering a door code, and it happens to everyone
    every week. Three or four denials in a row followed by a success is somebody
    working out which badge works where. The count is what separates a fumble
    from a systematic attempt, so a rule that ignores the count will fire forever.

    Note the door too: a person who is denied at one door and then badged
    successfully somewhere else has told you something the count alone does not.

    Write to: results_task3.csv
    """
    # TODO: group by badge_id, sort by timestamp, and keep a running count of
    # denials since the last success. On a `granted` with a non-zero count,
    # record the hit and reset the counter.
    hits = []
    return pd.DataFrame(hits, columns=["badge_id", "door", "granted_at",
                                       "prior_denials"])


# ============================================================ TASK 4
def after_hours(df, start="07:00", end="18:00"):
    """
    AFTER-HOURS ACCESS — outside staffed hours.

    QUESTION: What is accessed outside 07:00-18:00 on a weekday, or at all
    on a weekend?

    WHAT TO OUTPUT: badge_id, door, timestamp for each event.

    WHAT TO THINK ABOUT: this one is trivial to code and is where the actual
    analyst skill lives. You now have a candidate list that includes the
    legitimate overnight population: cleaners, the security guard on the
    22:00-06:00 shift, staff with known early or late schedules.
    SUBTRACT the known-benign population and report what is left. The code is
    three lines; the judgement of who is known-benign and who is not is the task.

    Build your before/after subtraction visible in the output or in your commit
    message, so the debrief can talk about it.

    Write to: results_task4.csv
    """
    # TODO: convert timestamp to minutes-since-midnight, then keep rows that are
    # before `start` or after `end`. Weekends (dayofweek >= 5) are all candidates.
    #   mins = df["timestamp"].dt.hour * 60 + df["timestamp"].dt.minute
    # Then filter out the known-benign population and save what remains.
    out = df.copy()
    return out[["badge_id", "door", "timestamp"]]


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

    print("\nDone. Now: which of these are real findings, and which are "
          "benign? Name a specific false positive from your own output.")
