# Backend reasoning review

Read this alongside the actual files in backend/app/ai/ and app/schema.sql. The answers below describe implemented behavior, not future plans.

## A five-minute rehearsal

1. **0:00-0:45:** Explain the flow: stable deposit event -> staff registration -> deterministic search -> public claim -> human staff decision. Explain that Wokwi/UI team acceptance is pending.
2. **0:45-1:45:** Parse `navy Milton flask` into blue/milton/bottle. Name the three supplied fields and explain why the browser displays server reasons instead of recomputing scores.
3. **1:45-2:45:** Derive the 90-point example below, then change the denominator when mark is omitted. Say why a perfect score cannot prove ownership.
4. **2:45-3:30:** Trace BFS from bottle with the queue below. Explain why sibling categories get no category points.
5. **3:30-4:15:** Explain the unique event reference, one-approved-claim index and approval transaction. A duplicate transport event is different from a competing claim.
6. **4:15-5:00:** Show one measured result and one retained failure. Explain the database-plus-photo recovery test and the remaining team gate.

## Work these out before reading the answers

**Q: Query bottle/blue/milton/library/star; item bottle/blue/milton/canteen/star. Score?**

Matched weights 40+25+15+0+10=90, denominator 100, score 90, coverage 5/5. With no mark supplied: 80/90*100=88.89, coverage 4/5. With only category supplied: 40/40*100=100, coverage 1/5.

**Q: What exactly is in the BFS queue?**

Start [bottle]. Pop bottle -> [personalitems]. Pop personalitems -> [campusitem, umbrella, keys]. All three are at depth 2, so each is popped without further expansion. Visited nodes are bottle:0, personalitems:1, campusitem:2, umbrella:2, keys:2. These distances do not directly add score points.

**Q: Does broaden=true always search siblings?**

No. It does so only when a supplied category has no eligible exact-category items after availability/exclusion filtering. It does not retry broadening just because exact-category scores are below 50.

**Q: Why is this AI if no model is trained?**

It represents knowledge explicitly and applies authored interpretation rules, graph search and heuristic ranking. No data-driven learning, embeddings or photograph classification is claimed.

**Q: What does purple bottle teach us?**

Unknown purple contributes nothing. Bottle still supplies positive evidence, so non-purple bottles can be returned. The frozen evaluation records this false positive. Do not call the measured top-1 rate general accuracy.

**Q: Can two people win the same item?**

The write transaction, available-status condition and partial unique index prevent two approved claims. The second approval returns 409. A high match score cannot bypass staff authentication or the decision.

**Q: What does append-only audit mean here?**

Application/schema updates and deletes are rejected by triggers. Someone with control of the database file/schema is outside that guarantee. Do not claim forensic tamper-proof storage.

**Q: What would you show if asked for live hardware?**

Only genuine recorded evidence after the simulation checks. The current replay and loopback tests use synthetic events; do not present them as live hardware.

## Review checklist

Run the B04/B06 exercises on synthetic records, then B07 recovery. Explain the score and BFS without reading this page. Record the date and any questions you could not answer; rehearsal results are tracked separately from automated checks.
