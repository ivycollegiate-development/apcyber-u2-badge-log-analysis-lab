# Correlation Evidence Packet — Template

Use this structure to reconstruct what happened from **four independent sources**. This is the version of the skill that shows up on the test: a badge log tells you a credential was accepted; a video tells you a person was somewhere; neither one alone tells you who.

**Fill in every section. An empty section is a finding** — "the visitor log has no entry for the 02:40 event" is information, and it is often the most important thing in the packet.

---

## 1. Case summary

| Field | Entry |
|---|---|
| **Case / incident ID** | |
| **Date and time of the event under investigation** | |
| **Location(s)** | |
| **Who raised it, and when** | |
| **Why it is being investigated** | *(one of: an alert fired, a report was filed, an audit found something, a review found something)* |

---

## 2. Sources collected

List every source you examined. **Every entry needs a provenance line** — where it came from, who exported it, and when. An evidence packet whose provenance is unrecorded is not evidence, it is a story.

| # | Source | System of record | Time range covered | Retrieved by / when | Integrity notes |
|---|---|---|---|---|---|
| 1 | Badge / access log | | | | *(retention window — was anything already overwritten?)* |
| 2 | Visitor log / sign-in sheet | | | | |
| 3 | Security patrol records | | | | |
| 4 | CCTV — camera ID, timestamp, footage reviewed | | | | *(retention window, any gaps, clock offset)* |
| 5 | *(any other: system logs, HR roster, key register, maintenance tickets)* | | | | |

> **Clock offsets matter.** Badge controllers, CCTV DVRs, and visitor systems drift. If two sources disagree by minutes, check for an offset before you conclude that two events are related. Record the offset you found, or record that you could not rule one out.

---

## 3. Timeline

One row per event. Chronological. **Sources are columns, not a merged story** — keep them separate, because the gaps between them are the point.

| # | Time (24h) | Source | Badge / person ID | Door / camera | What the source says | Notes & offset |
|---|---|---|---|---|---|---|
| 1 | | Badge log | | | | |
| 2 | | CCTV | | | | |
| 3 | | Visitor log | | | | |
| 4 | | Patrol record | | | | |

### Timeline gaps

List the intervals where **no source has coverage.** This is usually the most valuable section in the packet.

| Gap | Duration | Which sources are blind | What would have been needed |
|---|---|---|---|
| | | | |

---

## 4. Badge and credential analysis

| Field | Entry |
|---|---|
| **Credential(s) involved** | |
| **Assigned to** | *(name, role, department)* |
| **Access level / doors authorised** | |
| **Was the credential shared, cloned, or lent?** | |
| **How many distinct doors did it appear at?** | |
| **Was it used outside its normal hours or location?** | |
| **Prior denials or alerts on this credential** | |

---

## 5. Video correlation

| Camera | Location covered | Time range reviewed | What is visible | What is NOT visible (blind spot) |
|---|---|---|---|---|
| | | | | |

**One person, one credential?** State the ratio explicitly. A `granted` event with no corresponding body on camera is either a tailgate, a stuck door, or a person on a different camera's blind side — the video tells you which.

---

## 6. Corroboration

For each claim you are about to make, list the **independent** sources that support it. A claim supported by one source is an assertion, not a finding.

| Claim | Badge log | CCTV | Visitor log | Patrol | Other | **Corroborated?** |
|---|---|---|---|---|---|---|
| | ✔ | | | | | yes / no |
| | | ✔ | | | | yes / no |
| | | | ✔ | | | yes / no |

---

## 7. Findings

Each finding states: what happened, the evidence, the confidence, and what the evidence does **not** establish.

### Finding 1

- **What happened:**
- **Evidence:** *(source + specific timestamp + camera ID)*
- **Confidence:** high / medium / low — and why that level
- **Not established by this evidence:**
- **Alternative explanations considered and ruled out:** *(or "none ruled out")*

### Finding 2

- **What happened:**
- **Evidence:**
- **Confidence:**
- **Not established by this evidence:**
- **Alternative explanations considered and ruled out:**

---

## 8. The limitation

**State plainly what this packet cannot prove.**

A badge log records **credentials, not people.** It does not tell you who was holding the card, whether one person accounted for several events, or whether a `granted` event resulted in anyone entering at all. Video resolves this — where it exists. Where the video has a blind spot, the ambiguity is permanent, and saying so is a better analyst's move than picking the convenient answer.

> "The badge log shows credential B-0141 was accepted at MAIN-EAST at 02:40:12 and at SERVER-RM at 02:43:00 — 168 seconds apart, which is less than the four-minute end-to-end walk. Either the badge was shared or cloned, or the SERVER-RM reader time is offset from the MAIN-EAST reader time by at least three minutes. This packet cannot distinguish the two. **Recommendation: reconcile reader clock sync and re-examine.**"

---

## 9. Recommendations

| # | Recommendation | Fixes which finding | Cost / effort | Owner | Priority + justification |
|---|---|---|---|---|---|
| 1 | | | | | |

**Priority must be justified by likelihood and impact** — the same two axes as the risk matrix. "High priority" on its own is not a justification.

---

## 10. Open questions

What you could not resolve, and what it would take to resolve it.

| Question | What would answer it | Who to ask |
|---|---|---|
| | | |
