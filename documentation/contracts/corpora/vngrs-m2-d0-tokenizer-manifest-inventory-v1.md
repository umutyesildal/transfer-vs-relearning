# vngrs M2 D0 tokenizer manifest-only inventory v1

**Status:** `FROZEN / UNEXECUTED`  
**Execution authorized:** no  
**Created:** 2026-08-27

## Purpose

Close the remaining tokenizer asset-file identities for the OLMo, Qwen and SmolLM M1 epoch-036
parents using only six already-preserved compact manifests. This is a read-only evidence pass. It
does not inspect corpus bytes, load tokenizer assets or model weights, and does not run M2.

## Exact inputs

The companion config freezes exactly three snapshot manifests and three model manifests, including
their already-recorded SHA-256 values. No directory traversal, glob, `find`, `du`, or recursive
inventory is permitted. A path/hash mismatch stops the pass before its payload is accepted.

The only allowed remote file operations are:

- `stat` on the six exact files;
- `sha256sum` on the six exact files;
- bounded byte reads of those same six compact JSON files after size/hash verification.

Each file is limited to 1 MiB and the combined returned payload to 6 MiB. Raw payloads may be
transported as base64 through the reviewed `ssh-client/scripts/hu_ssh_expect` route. Credentials,
environment values and signed URLs must never appear in output.

## Derivation

For each model, the locally committed manifest-only extractor must:

1. reverify the raw snapshot/model-manifest payload SHA-256;
2. require the model and tokenizer source paths to equal the exact epoch-036 snapshot root;
3. accept only the frozen tokenizer filename allowlist;
4. require `tokenizer.json` and `tokenizer_config.json`;
5. derive a canonical ordered tokenizer asset registry and its SHA-256;
6. report zero tokenizer asset files and zero model-weight files opened.

Missing assets, malformed rows, unexpected nested paths, duplicate paths, wrong sizes/hashes or
root drift are `BLOCKED`; they are never inferred or replaced.

## Outputs

HU writes are exactly zero. If separately authorized and successful, one compact local JSON result
may be created at:

`artifacts/corpora/vngrs_m2_d0/tokenizer_manifest_inventory_v1.json`

It contains only paths, byte counts, hashes, statuses and contract/config/code bindings. It must
not contain manifest raw bytes, tokenizer contents, model contents, credentials or excerpts.

## Prohibitions

- no HU or local source-root write, output-root creation, cache, temporary file or log on HU;
- no model/tokenizer asset open beyond the six exact manifest files;
- no model load, tokenizer load, inference, scoring, GPU, Slurm, training or evaluation;
- no vngrs/trwiki access, download, public HTTP, corpus materialization or row read;
- no Git push/pull/fetch, checkout mutation, branch publication or HU repo synchronization;
- no cleanup, deletion, move, chmod, retry, alternate path or expanded inventory;
- no claim that D0 is qualified, frozen for materialization, or ready to train.

## Execution boundary

Preparation and local testing of this contract do not authorize HU/SSH. One later user instruction
must quote the exact final contract SHA-256 and authorize this single six-file read-only pass.

