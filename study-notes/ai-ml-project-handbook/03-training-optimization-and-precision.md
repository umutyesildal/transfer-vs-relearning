# 03 — Training, Optimization, and Precision

## 1. One optimizer update

A simplified training update is:

1. encode a microbatch into token IDs and masks;
2. run the forward pass;
3. compute the masked causal-LM loss;
4. backpropagate gradients;
5. optionally accumulate gradients over more microbatches;
6. optionally unscale and clip gradients;
7. apply the optimizer update;
8. update the learning-rate schedule;
9. clear gradients;
10. record metrics and perhaps save a checkpoint.

For parameters \(\theta\), basic gradient descent is

\[
\theta_{t+1}
=
\theta_t-\eta_t\nabla_\theta\mathcal{L}_t,
\]

where \(\eta_t\) is the learning rate. Real training uses adaptive optimizers and many engineering safeguards, but the core remains: compute a gradient and move parameters.

## 2. Microbatch, gradient accumulation, and effective batch

A **microbatch** is the number of examples processed in one forward/backward pass on one device. If memory only fits \(b_\mu\) examples, gradients can be accumulated for \(K\) microsteps before the optimizer update.

For one device:

\[
B_{\text{effective}}=b_\mu K.
\]

With \(D\) synchronized data-parallel devices:

\[
B_{\text{effective}}=b_\mu K D.
\]

The OLMo BF16 dose/Pareto run used:

- microbatch \(b_\mu=5\);
- gradient accumulation \(K=100\);
- one GPU;

so

\[
B_{\text{effective}}=5\times100\times1=500
\]

training rows per optimizer update.

This decomposition was operationally crucial. The effective batch stayed 500 even when memory experiments changed the microbatch/accumulation pair. However, equal effective batch does not guarantee bitwise-identical training:

- dropout masks occur per microbatch;
- floating-point summation order changes;
- gradient clipping may be applied at different moments;
- variable sequence lengths change token counts;
- batch-dependent layers, if present, behave differently.

For decoder-only Transformers without batch normalization, accumulation is usually a reasonable way to preserve the intended batch, but the exact implementation still belongs in the manifest.

## 3. Update, step, epoch, and exposure

These terms are often confused:

- **microstep:** one forward/backward pass;
- **optimizer update:** one parameter update after accumulation;
- **epoch:** one traversal of the example dataset under its sampler;
- **exposure:** one presentation of an example or fact;
- **checkpoint step:** a saved optimizer-update index.

If a dataset has 500 rows and the effective batch is 500, one optimizer update consumes one dataset-sized batch. With 252 updates, the nominal exposure count is 252 presentations per row if sampling is perfectly aligned, but actual exposure depends on shuffling, replacement, packing, and the epoch implementation.

The project’s dose grid \(42,84,126,168,210,252\) is an optimizer-update grid. It corresponds to increasing training dose without changing the recipe.

## 4. Adam and AdamW

Adam maintains exponential moving averages of gradients and squared gradients:

\[
m_t=\beta_1m_{t-1}+(1-\beta_1)g_t,
\]

\[
v_t=\beta_2v_{t-1}+(1-\beta_2)g_t^2.
\]

After bias correction:

\[
\hat m_t=\frac{m_t}{1-\beta_1^t},\qquad
\hat v_t=\frac{v_t}{1-\beta_2^t}.
\]

An Adam-like update is

\[
\theta_{t+1}
=
\theta_t
-\eta_t
\frac{\hat m_t}{\sqrt{\hat v_t}+\epsilon}.
\]

AdamW decouples weight decay from the adaptive gradient:

\[
\theta_{t+1}
=
(1-\eta_t\lambda)\theta_t
-\eta_t
\frac{\hat m_t}{\sqrt{\hat v_t}+\epsilon},
\]

where \(\lambda\) is the weight-decay coefficient. The distinction matters because ordinary L2 regularization inside Adam is transformed by the adaptive denominator, whereas decoupled decay is applied directly to parameters. Primary reference: Loshchilov and Hutter, [Decoupled Weight Decay Regularization](https://arxiv.org/abs/1711.05101).

## 5. Why optimizer state consumes so much memory

For each trainable parameter, AdamW commonly stores:

- the parameter value;
- its gradient;
- first moment \(m\);
- second moment \(v\);
- sometimes an FP32 master parameter;
- temporary tensors used by fused or foreach operations.

For \(P\) parameters, a rough lower-level memory model is

\[
M
\approx
P(b_\theta+b_g+b_m+b_v+b_{\text{master}})
+M_{\text{activations}}
+M_{\text{temporary}}
+M_{\text{allocator overhead}}.
\]

For a 1.484-billion-parameter model:

- one 16-bit tensor alone is roughly \(1.484\times10^9\times2\) bytes, about 2.97 GB decimal;
- two optimizer moments at 16 bits add about 5.94 GB;
- gradients add about 2.97 GB;
- activations and temporary operations add more;
- FP32 moments or master weights double relevant components.

This explains why a model can fit for inference but fail during the first AdamW update. The optimizer peak, not the forward pass, can be the true memory bottleneck.

## 6. The optimizer-smoke concept

The project uses a pre-training optimizer smoke test:

- load the exact model;
- create the exact optimizer;
- run representative forward/backward computation;
- execute the optimizer path;
- observe peak allocation and numerical validity;
- stop before scientific training.

This separates “the model loads” from “the actual recipe fits.” It also prevents an expensive job from failing after partial scientific updates.

The OLMo FP16 attempts illustrate temporary-memory failure. Even after switching from multi-tensor to single-tensor AdamW, the update failed near a \(\sqrt{v}\) temporary because only hundreds of MiB remained. Disabling foreach changed the implementation path but did not eliminate the underlying peak.

## 7. Learning rate and schedule

The learning rate controls update scale. Too small:

- new facts may not be acquired;
- convergence can be slow;
- early checkpoints may look unchanged.

Too large:

- optimization can become unstable;
- generic capabilities can drift;
- exact factual mappings may strengthen while prompt robustness or fluency deteriorates.

A warmup schedule starts with a smaller learning rate:

\[
\eta_t=
\eta_{\max}\frac{t}{T_{\text{warmup}}}
\quad\text{for }t\leq T_{\text{warmup}}.
\]

After warmup, the project may use a constant rate or another frozen schedule. “Learning rate \(5\times10^{-5}\)” is incomplete unless schedule, warmup, batch, optimizer, and update count are also known.

The M1 drift ablation tested \(2\times10^{-5},5\times10^{-5},10^{-4},2\times10^{-4}\). Higher rates could improve direct factual acquisition while worsening generic retention. The chosen \(5\times10^{-5}\), answer-only, EOS-masked recipe was a Pareto compromise, not the numerically strongest score on every metric.

## 8. What floating-point precision means

A floating-point number has sign, exponent, and significand fields. Precision formats trade:

- representable range;
- spacing between neighboring values;
- storage;
- memory bandwidth;
- hardware throughput.

Approximate format comparison:

| Format | Bits | Exponent bits | Fraction bits | Main property |
|---|---:|---:|---:|---|
| FP32 | 32 | 8 | 23 | wide range and relatively fine precision |
| FP16 | 16 | 5 | 10 | finer significand than BF16 but much narrower range |
| BF16 | 16 | 8 | 7 | FP32-like range but coarser precision |

BF16 preserves FP32’s exponent width, which makes overflow and underflow less common than FP16 in deep-learning workloads. It is not “more precise” than FP16 in the everyday sense: BF16 has fewer fraction bits. It has **more range** and **less significand precision**.

Primary references:

- Micikevicius et al., [Mixed Precision Training](https://arxiv.org/abs/1710.03740)
- Kalamkar et al., [A Study of BFLOAT16 for Deep Learning Training](https://arxiv.org/abs/1905.12322)

## 9. FP16: why loss scaling exists

Backpropagation can produce very small gradients. FP16’s narrow exponent range may round them to zero:

\[
g = 10^{-8}
\quad\Rightarrow\quad
\operatorname{FP16}(g)\approx 0
\]

in susceptible operations.

Loss scaling multiplies the loss:

\[
\mathcal{L}'=S\mathcal{L},
\]

so gradients become

\[
\nabla\mathcal{L}'=S\nabla\mathcal{L}.
\]

Before the optimizer update, gradients are divided by \(S\). Dynamic GradScaler logic increases the scale when training is stable and reduces it after overflow.

The key is that scaling changes numerical representation, not the intended mathematical update:

\[
\frac{1}{S}\nabla(S\mathcal{L})=\nabla\mathcal{L}.
\]

PyTorch’s official [Automatic Mixed Precision documentation](https://docs.pytorch.org/docs/stable/amp.html) explains autocast and gradient scaling.

## 10. Autocast is not “everything becomes FP16”

Automatic mixed precision chooses dtypes per operation. Some matrix multiplications may run in a 16-bit format, while numerically sensitive reductions or accumulations run in FP32. Model parameters, gradients, optimizer moments, and outputs can each have different dtypes.

Therefore a manifest should not merely state “used FP16.” It should distinguish:

- parameter dtype;
- autocast dtype;
- gradient dtype;
- optimizer-state dtype;
- loss-scaler enabled/disabled;
- master-weight dtype if any;
- fused/foreach optimizer path;
- hardware and software versions.

## 11. Native FP16 versus AMP with FP32 parameters

These are different configurations:

### Common AMP pattern

- parameters stored in FP32;
- selected forward operations autocast to FP16;
- gradients scaled;
- optimizer updates FP32 parameters.

### Native FP16 parameter pattern

- parameters themselves are FP16;
- gradients may also be FP16;
- optimizer state may be FP16 or FP32;
- standard GradScaler assumptions may no longer hold.

The Pythia RTX3090 relocation failed before scientific training because the configuration attempted to unscale native FP16 gradients using a path that guards against this unsupported combination. The later valid configuration used BF16 parameters and gradients with no GradScaler.

The lesson is not “GradScaler is bad.” It is that the precision topology must match the framework’s optimizer and scaler semantics.

## 12. Why BF16 solved one class of problem

In the valid Pythia run:

- model parameters were BF16;
- gradients were BF16;
- AdamW moment tensors were BF16;
- scalar optimizer step was FP32;
- GradScaler was disabled.

This passed the frozen runtime and optimizer-state assertions. The resulting scientific result was valid even though it failed the retention gate.

BF16 reduced FP16 range problems, but it did not guarantee scientific quality. Numerical validity and model retention are different layers:

\[
\text{finite valid training}
\not\Rightarrow
\text{acceptable model behavior}.
\]

## 13. Hardware compatibility

GPU model names are not enough. Relevant properties include:

- compute capability;
- supported kernel architectures;
- BF16 or FP16 hardware support;
- total and currently free VRAM;
- foreign processes;
- driver, CUDA, and PyTorch build compatibility.

The OLMo V100 path initially failed because the existing PyTorch/CUDA environment did not include kernels for compute capability SM70. A compatible scratch-only environment was then validated before training. This was a runtime compatibility failure, not a model failure.

An RTX3090 and a V100 may both advertise mixed-precision support while differing in:

- native BF16 support;
- Tensor Core behavior;
- memory capacity;
- compiler targets;
- throughput and kernel availability.

## 14. Gradient clipping

Global-norm clipping rescales gradients if their norm exceeds \(c\):

\[
g'
=
\begin{cases}
g,&\|g\|_2\leq c,\\
c\frac{g}{\|g\|_2},&\|g\|_2>c.
\end{cases}
\]

With loss scaling, gradients normally need to be unscaled before clipping; otherwise the clipping threshold is applied to the artificially enlarged values. The exact order is part of the recipe.

Clipping prevents extreme updates but does not correct a systematically excessive learning rate or a bad dataset.

## 15. Gradient checkpointing

Activations from the forward pass are needed for backpropagation. Storing all of them can dominate memory. Gradient checkpointing stores only selected activations and recomputes the missing ones during backward.

Trade-off:

\[
\text{less activation memory}
\quad\leftrightarrow\quad
\text{more computation}.
\]

Primary reference: Chen et al., [Training Deep Nets with Sublinear Memory Cost](https://arxiv.org/abs/1604.06174).

This technique changes operational feasibility, not the intended loss. It can still affect runtime, nondeterminism, and exact floating-point paths.

## 16. Full-weight training versus LoRA

Full-weight training updates all selected model parameters. LoRA freezes a weight matrix \(W\) and learns a low-rank update:

\[
W'=W+\Delta W,\qquad
\Delta W=BA,
\]

with rank \(r\ll \min(d_{\text{in}},d_{\text{out}})\).

Advantages:

- fewer trainable parameters;
- smaller optimizer state;
- easier artifact storage;
- potentially less broad parameter drift.

Limitations:

- low rank constrains the update subspace;
- results depend on target modules and rank;
- an adapter is not equivalent to full-weight continued pretraining;
- retention benefits are empirical, not automatic.

Primary reference: Hu et al., [LoRA](https://arxiv.org/abs/2106.09685).

For a causal study, changing full-weight training to LoRA is a scientific intervention, not merely an engineering optimization. It needs its own contract and matched comparison.

## 17. Checkpoints and what they contain

A model-only checkpoint contains enough to run inference if config and tokenizer are available. A resumable training checkpoint may also contain:

- optimizer moments;
- learning-rate scheduler state;
- gradient scaler state;
- RNG states;
- sampler position;
- update and epoch counters.

Model-only retention freezes are much smaller, but cannot perfectly resume training. The artifact policy must match the future scientific need.

## 18. Worked dose example

The OLMo dose study evaluated checkpoints at updates:

\[
42,84,126,168,210,252.
\]

Every checkpoint reached 100% cheap exact acquisition, but PPL ratios ranged roughly from 1.385 to 1.429, all above the frozen maximum 1.25. Therefore:

- factual acquisition was already strong by update 42;
- additional dose did not create a retention-passing point;
- the hard suite stayed closed under the evaluation cascade;
- the run was a valid scientific negative.

The conclusion is not “OLMo cannot learn facts.” It is “under this frozen recipe and tested dose range, no checkpoint met the joint acquisition-retention gate.”

## 19. Chapter summary

- Effective batch is microbatch × accumulation × number of synchronized devices.
- AdamW stores substantial per-parameter state and can peak during the first optimizer update.
- Learning rate and dose govern a stability–plasticity trade-off.
- FP16 has a narrow numerical range and often needs loss scaling.
- BF16 has FP32-like range but fewer fraction bits; it often runs without GradScaler.
- “Mixed precision” must be expanded into parameter, gradient, optimizer-state, autocast, and scaler dtypes.
- Hardware/runtime failures are NOT-RUN evidence; a valid run that fails retention is a scientific negative.
- Checkpoint trajectories expose whether an earlier Pareto-valid state exists.
