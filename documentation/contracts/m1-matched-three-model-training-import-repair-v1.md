# M1 matched training import-path repair v1

**Status:** frozen, unexecuted, unauthorized

The first authorized M1 DAG used jobs `475832` → `475833_[0-2]` → `475834`. Preflight passed,
but all three training tasks stopped before model load because the installed HU package shadowed
the checkout and lacked `transfer_vs_relearning.pipeline`. No model, tokenizer, optimizer,
training update, checkpoint or binding output was created. The audit recorded all three models as
missing. Root `/vol/tmp2/yesildau/m1_matched_three_model_v1` and its flat logs remain immutable.

This correction changes only two operational bindings:

1. every Slurm job exports `PYTHONPATH=$SLURM_SUBMIT_DIR/src`;
2. runtime-derived training output roots live under the fresh root
   `/vol/tmp2/yesildau/m1_matched_three_model_retry_v1`.

The three source configs, models, dataset, seed, objective, LR, precision, effective batch, 36
epochs, 252 updates, snapshot policy, A10080 array topology and afterany audit are unchanged. The
companion config binds all corrected implementation hashes. There is no automatic retry; one new
exact SHA-bound authorization is required for push, HU fast-forward and one retry DAG.
