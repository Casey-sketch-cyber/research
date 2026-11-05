# Reviews

The reviewer (the human author working with Claude) writes one file per gate here:
`G1_review.md`, `G2_review.md`, `G3_review.md`, `G4_review.md`.

Format:

```
# Gate Gx review
Verdict: APPROVED | CHANGES_REQUESTED

1. [must] …
2. [should] …
```

Codex replies to every item in `reports/GATE_Gx_response.md` and continues only once the verdict is APPROVED or the human author says to proceed.
