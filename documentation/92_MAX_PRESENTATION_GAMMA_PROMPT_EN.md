# Gamma Prompt — M1 Research Story For Max

Create a minimal, academic, English presentation for a one-to-one thesis-supervision meeting.

The presentation should explain the research process rather than advertise a finished result.
Show the initial failure, the methods tested, concrete examples, the diagnosis, the successful
intervention, the Relation V2 change, the controlled model-capacity comparison, the degeneration
control, and the decisions that remain open.

## Design

- 16:9 format;
- exactly 10 slides;
- clean white background, dark navy text, blue and teal accents;
- final slide may use a dark navy background;
- no stock photography, decorative AI imagery, gradients, mockups, or generic icons;
- one main claim per slide;
- large single-line titles;
- low text density and generous spacing;
- use examples and a few large numbers instead of dense result tables;
- no agenda slide and no “Thank you” slide;
- do not invent claims, metrics, citations, or experiments.

## Slide 1 — Title

Title:

“English factual acquisition before cross-lingual adaptation”

Subtitle:

“What failed, what worked, and what remains unresolved”

Footer:

“Umut Yeşildal · M1 research discussion · July 2026”

## Slide 2 — M1 is the validity condition for the thesis

Question:

“Can a fact learned in English remain accessible after Turkish adaptation—and can we separate
transfer from relearning?”

Show:

- M0: verify that synthetic facts are not already known;
- M1: acquire and robustly retrieve the facts in English;
- M2: Turkish adaptation without target-fact repetition; transfer condition;
- M3: repeat target facts in Turkish; relearning condition.

Takeaway:

“If M1 is weak, a later Turkish failure is not interpretable as evidence against transfer.”

## Slide 3 — The model stored facts without robust access

Use this concrete fact:

“Mada Granger → born_in → Istanbul”

Show three views:

- Exact-prefix: “Mada Granger was born in …” — often accessible.
- Held-out direct: “What is Mada Granger’s birthplace?” — usually failed.
- Held-out QA: “Question: Where was she born? Answer:” — usually failed.

Bottom takeaway:

“Early large-scale recipes reached at most about 5/500 robust successes, even when training loss
decreased.”

## Slide 4 — Training fixes improved optimization, not robust access

Show three method/example/result rows:

1. More CLM exposure
   - Example: repeat short facts for more epochs and use 2e-5, 5e-5, and 1e-4 in different
     historical recipes.
   - Result: loss fell; robust overlap remained around 2–5/500.

2. BIO + QA mixture
   - Example: a full biography says that Mada Granger was born in Istanbul, lives in Mugla,
     studied at a university, and works at a company; QA rows ask for individual relations.
   - Result: direct 8/500, QA 11/500, overlap 3/500.

3. Acquire → extract
   - Example: Stage A learns the biography; Stage B continues with
     “Where was Mada Granger born? → Istanbul”.
   - Result: direct 6/500, QA 6/500, overlap 2/500.

Takeaway:

“The model could predict seen answer tokens without learning prompt-robust
subject–relation–object access.”

## Slide 5 — Richer objectives did not solve prompt transfer

Left:

Candidate-ranking objective:

- train the correct object to outrank relation-specific alternatives;
- first pilot: 5/500 robust overlap;
- follow-up: 2/500.

Right:

Binding-mix redesign:

- example: ask for Mada Granger’s birthplace while using Mugla, the same subject’s residence, as
  a hard negative against Istanbul;
- direct 7/500, QA 11/500, robust overlap 3/500.

Bottom:

“Strategy shift: stop searching on the full problem. First prove acquisition for one fact, then
scale through 10 facts, 50 facts, and finally 500 facts.”

## Slide 6 — Direct supervision solved the missing prompt-format transfer

Concrete fact:

“Augusta Rodriquez → born_in → Van”

Training paraphrases:

- “Where was Augusta Rodriquez born? Van”
- “Which place is recorded as her birthplace? Van”

Held-out evaluation:

“What is the birthplace of Augusta Rodriquez?” → Van rank 1.

Acquisition ladder:

- 1 fact: exact, direct, and QA all rank 1;
- 10 facts: 10/10 robust;
- 50 facts: 48/50 robust.

Recipe:

“Per fact: 3 declarative + 2 QA + 2 scaffold-free direct rows; answer-only loss; evaluation
paraphrases remain unseen.”

## Slide 7 — Relation V2 addressed candidate collapse

V1 at 500 facts:

- 451 exact;
- 277 robust overlap;
- studied_at: 29/100 triple robust;
- works_at: 24/100 triple robust;
- errors concentrated on a few dominant proper-name candidates.

Relation V2:

- studied_at → field_of_study;
- works_at → works_in_industry;
- 500 exact;
- 329 robust overlap;
- +52 robust facts over V1.

Current relations:

“profession · born_in · lives_in · field_of_study · works_in_industry”

Clarify that V2 improved the problem but the 360M model still missed the precommitted overlap gate
by 21 facts.

## Slide 8 — Increasing model capacity closed most of the gap

Explain that data, objective, learning rate, epochs, effective batch, update budget, and evaluator
were fixed.

Show only:

- SmolLM2-360M: 329/500 robust overlap;
- SmolLM2-1.7B: 497/500 robust overlap;
- independent training/data-order replication: 499/500.

Small setup line:

“100 subjects · 500 facts · 3,500 rows · LR 1e-4 · 36 epochs · 252 updates · weight decay 0”

Bottom takeaway:

“This establishes a strong English acquisition condition for M2/M3; it is not the end of the
thesis.”

## Slide 9 — M1 retains general responses, but measurable drift remains

Perplexity:

- base: 15.924;
- M1 seed 42: 19.018;
- M1 seed 43: 18.681.

Callouts:

- +17–19% generic perplexity drift;
- 30/30 M1 continuations ended in EOS.

Preserved:

- 30/30 common-knowledge candidate ranking;
- meaningful general continuations;
- zero synthetic-name intrusion.

Conclusion:

“Short-answer and stopping-behavior drift—not broad fact-only collapse.”

## Slide 10 — We solved M1 acquisition—not the full research question

What we now know:

“Direct prompt coverage, Relation V2, and model capacity can produce robust English retrieval at
the 500-fact development scale.”

What remains uncertain:

“General-language retention, checkpoint selection, higher-scale retrieval, and the eventual M2/M3
transfer-versus-relearning comparison.”

What to discuss:

“Whether to proceed with the frozen M1 checkpoints, run a controlled learning-rate sensitivity
test first, and treat EOS supervision as a separate ablation.”

Final meeting question:

“Move into M2/M3 now, or first optimize the factual-retention versus general-capability
trade-off?”

## Accuracy Guardrails

- Do not describe the thesis or the complete research project as finished.
- The strong acquisition result applies to Relation V2, 500 facts, and SmolLM2-1.7B.
- The 2,500-fact exploratory result should not appear in the main presentation.
- Learning rates 2e-5, 5e-5, and 1e-4 were used in different historical recipes, not as a clean
  sweep on the final setup.
- The 2e-4 condition has not been run.
- V1 contained studied_at and works_at; V2 replaced them with field_of_study and
  works_in_industry.
- The general-capability conclusion is “measurable drift, but not broad degeneration.”
