# Email to Max: M1 Completion Update

**Subject:** Thesis Update: M1 Acquisition Gate Successfully Passed

Dear Max,

I wanted to share a very encouraging update from the thesis implementation.

As a brief reminder of how we arrived here, the M1 stage was considerably more difficult than we
initially expected. In the earliest experiments, the model showed almost no robust acquisition:
one of our first reliable evaluations produced only **5/500 facts** that were correct across the
relevant prompt conditions. Increasing training intensity and trying richer biography and QA
mixtures improved the training loss, but did not consistently solve retrieval under held-out
English prompts. This made it clear that a lower loss or correct completion in the training format
was not sufficient evidence that a fact had become robustly accessible.

We also identified a data-design problem in the original relation set. The `studied_at` and
`works_at` relations contained many proper-name-heavy objects, and the model repeatedly collapsed
toward a few frequent candidates such as particular universities or companies. We therefore
introduced Relation V2, replacing these relations with `field_of_study` and
`works_in_industry`, while retaining the scientifically important `born_in` and `lives_in`
relations. The assignments were made independent and balanced so that the model could not answer
correctly by exploiting correlations between profession, location, field, and industry.

This redesign gave us a much cleaner diagnostic result with SmolLM2-360M. The model achieved
**500/500 exact-prefix accuracy**, showing that all 500 facts had been stored, but only **329/500
robust overlap** across the two held-out prompt formats. In a subsequent exploratory 2,500-fact
run, exact storage remained at 99.92%, while robust overlap fell to 38.32%. These experiments were
important because they separated two issues that we had previously treated as one: storing a fact
and retrieving the correct subject-relation-object binding under a new prompt.

We have now successfully completed the M1 English factual-acquisition stage for the Relation V2
500-fact setting using SmolLM2-1.7B. Until now, our main difficulty was that the smaller 360M model
could store the facts in the exact training format but could not retrieve them reliably under new
English question formulations. Its exact score was 500/500, while the robust overlap across two
held-out prompt formats remained at 329/500.

To test whether this was primarily a capacity limitation, we repeated the experiment with
SmolLM2-1.7B while keeping the dataset, objective, learning rate, number of epochs, effective batch
size, optimizer-step budget, evaluator, and precommitted success criteria unchanged.

The result was a substantial improvement:

| Run | Exact | Direct | QA | Robust overlap |
|---|---:|---:|---:|---:|
| Seed 42, checkpoint 200 | 500/500 | 499/500 | 498/500 | 497/500 |
| Seed 43, checkpoint 75 | 500/500 | 500/500 | 499/500 | 499/500 |

The robust overlap therefore increased from **65.8% with the 360M model to 99.4% and 99.8% with
the 1.7B model**. Both runs passed the M1 gate by a large margin.

We also verified that the second result was based on a genuinely different training order rather
than a deterministic reproduction of the first run. The two selected checkpoints have been
frozen as model-only artifacts and recorded with manifests and SHA-256 hashes.

Scientifically, this suggests that the earlier bottleneck was not a fundamental failure of the
synthetic data or the answer-only acquisition objective. The 360M model could store the facts, but
had insufficient capacity to access the learned subject-relation-object bindings robustly across
different prompts. The 1.7B model almost completely resolved this retrieval problem under the
same experimental conditions.

I would therefore consider M1 complete specifically for the **Relation V2, 500-fact,
SmolLM2-1.7B condition**. This does not yet demonstrate cross-lingual transfer, but it gives us a
reliable English acquisition baseline from which to begin the actual M2/M3 comparison:

- M2: generic Turkish adaptation without exposing the target facts in Turkish;
- M3: a controlled Turkish repetition/relearning condition;
- comparison of English retention and Turkish access across both branches.

After a long sequence of negative and diagnostic experiments, it is genuinely exciting to have a
result this clear. More importantly, the earlier failures helped us identify the actual bottleneck
and make the present result methodologically interpretable.

I would be very interested in your view on whether we should proceed directly with the canonical
seed-42 checkpoint 200 for the first M2/M3 pilot, while keeping seed 43 as the replication arm.

Best regards,  
Umut
