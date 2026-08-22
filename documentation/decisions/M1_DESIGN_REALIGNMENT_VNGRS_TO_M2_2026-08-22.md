# M1/M2 corpus realignment — vngrs belongs to the Turkish sibling arms

**Date:** 2026-08-22
**Status:** current user correction; preparation only; no execution authorized

## Correction

The earlier same-day preparation memo recorded `vngrs-ai/vngrs-web-corpus` as the M1 primary
Turkish corpus. The user has now clarified that this was intended for M2. That earlier memo is
preserved as historical evidence and is superseded for the current plan; it is not deleted or
rewritten.

The current state design is:

```text
M0  = pretrained base model
M1  = M0 + English synthetic factual adaptation
M2-A = same frozen M1 checkpoint + fact-free Turkish vngrs adaptation
M2-B = same frozen M1 checkpoint + matched Turkish vngrs adaptation
       + controlled Turkish factual re-exposure
```

`vngrs` is therefore an M2-A/M2-B shared input and must not be a prerequisite for M1 training or
M1 evaluation. The two M2 siblings must use the same frozen vngrs release, document-disjoint
splits, token/update budget and checkpoint grid; their only intended data difference is controlled
Turkish factual re-exposure in M2-B. `trwiki-20260601` remains the cross-domain control.

## Consequences for the one-command M1 evaluator

The M1 controller now requires a hash-closed synthetic-fact dataset manifest, M1 training manifest
and M1 checkpoint manifest. It still inherits the full eval-v2 metric bundle, the pinned M0
TurBLiMP route and the mandatory 500-probe exact-prefix supplement. It does not require a vngrs
manifest and cannot materialize or score vngrs.

After M1 checkpoint selection, a separate M2 corpus/recipe contract will bind vngrs and open the
parallel M2-A/M2-B sibling wave. No M2 contract or corpus materialization is created by this
correction.
