# M0 Seven-Lane Recovery — Exact Execution Authorization

Date: 2026-08-20  
Status: `AUTHORIZED_SINGLE_WAVE`

## Bound frozen identities

- Contract SHA-256: `1ee7c8d9d1da092cd1e4a64dbffa4594e041ebf2b4d56eb62f345a6aaa8c25c4`
- Pre-authorization config SHA-256: `4a603719dd43a65dd9b36a36786407993afe84cf8d1d48f6245656d235c6bfeb`
- Frozen implementation commit: `07cbaa6d55f0713a08bae8a1c3c9cbe2df5e8942`

## User authorization

The user explicitly authorized:

> Contract SHA-256 `1ee7c8d9d1da092cd1e4a64dbffa4594e041ebf2b4d56eb62f345a6aaa8c25c4`
> and config SHA-256 `4a603719dd43a65dd9b36a36786407993afe84cf8d1d48f6245656d235c6bfeb`
> are bound to one seven-lane M0 recovery wave; perform HU fast-forward, preflight and the
> 11-job DAG submission.

## Exact opened scope

This authorization opens exactly once:

1. publish and preservation-checked fast-forward of the authorized implementation;
2. one fail-closed HU preflight;
3. one fresh recovery namespace;
4. seven frozen GPU recovery lanes;
5. three model finalizers and one family finalizer;
6. read-only monitoring and preservation of the outputs.

It does not authorize rescoring the 17 complete source lanes, route or metric changes, automatic
retry, a second recovery wave, normalization, scientific interpretation, M1/M2 work, network
retrieval, corpus work, cleanup, deletion, HU-home writes or foreign-process intervention.
