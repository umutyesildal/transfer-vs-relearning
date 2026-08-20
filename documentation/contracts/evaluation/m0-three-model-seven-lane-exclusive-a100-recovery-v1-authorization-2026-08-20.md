# Exclusive-A100 M0 Recovery — Exact Execution Authorization

Date: 2026-08-20  
Status: `AUTHORIZED_SINGLE_WAVE`

## Bound identities

- Contract SHA-256: `41215ef7be2ad18ea9c8f52581870955431ba7ff5ba8af20633650452c0dca01`
- Pre-authorization config SHA-256: `9632b5274cda8012432aeb7837d4cb33ab7e2992354ede615eaf1f22eee9d689`
- Frozen implementation commit: `112a2c5482525d0f541b646cf232e6c94e7deb7b`

## User authorization

The user explicitly authorized one exclusive-A100 M0 recovery wave bound to the exact contract and
config identities above, including push/HU fast-forward, final preflight and one five-job DAG.

## Opened scope

The authorization opens exactly once:

1. publication and preservation-checked HU fast-forward;
2. one fail-closed final preflight;
3. one fresh isolation namespace;
4. one exclusive three-A100 sequential controller for the seven missing lanes;
5. three model finalizers and one family finalizer;
6. read-only monitoring and preservation.

It does not authorize rescoring the 17 complete lanes, modifying either prior recovery root,
lowering memory gates, automatic resubmission, a second wave, normalization, M1/M2, corpus/network
work, cleanup, deletion, HU-home writes or foreign-process intervention.
