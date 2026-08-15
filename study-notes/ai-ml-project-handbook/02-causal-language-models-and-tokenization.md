# 02 — Causal Language Models and Tokenization

## 1. What a causal language model learns

A causal language model assigns a probability to the next token given the tokens that came before it:

\[
p_\theta(x_t \mid x_1,\ldots,x_{t-1}).
\]

For a token sequence \(x_{1:T}\), the chain rule gives

\[
p_\theta(x_{1:T})
=
\prod_{t=1}^{T}p_\theta(x_t\mid x_{<t}).
\]

Taking logarithms converts the product into a sum:

\[
\log p_\theta(x_{1:T})
=
\sum_{t=1}^{T}\log p_\theta(x_t\mid x_{<t}).
\]

Training usually minimizes average negative log-likelihood, equivalently token-level cross-entropy:

\[
\mathcal{L}_{\text{CLM}}
=
-\frac{1}{N}
\sum_{t \in \mathcal{V}}
\log p_\theta(x_t\mid x_{<t}),
\]

where \(\mathcal{V}\) is the set of positions with valid labels. Some positions can be excluded from the loss with an ignore label such as \(-100\).

The model is not directly told to “store a database row.” It is updated so that, in the contexts used for training, the correct next tokens become more probable.

## 2. Transformer computation in one pass

The project models are decoder-only Transformers. A simplified layer contains:

1. token and position representations;
2. causal self-attention;
3. a feed-forward network;
4. residual connections and normalization;
5. a final projection from hidden state to vocabulary logits.

For one attention head:

\[
Q=XW_Q,\qquad K=XW_K,\qquad V=XW_V,
\]

\[
\operatorname{Attention}(Q,K,V)
=
\operatorname{softmax}
\left(
\frac{QK^\top}{\sqrt{d_k}} + M
\right)V.
\]

The causal mask \(M\) makes future positions unavailable. At position \(t\), attention can use positions \(1,\ldots,t\), not \(t+1,\ldots,T\).

The final hidden vector \(h_t\) is mapped to one logit per vocabulary item:

\[
z_t = W_{\text{vocab}}h_t+b.
\]

Softmax converts logits to probabilities:

\[
p_\theta(v\mid x_{\leq t})
=
\frac{\exp z_{t,v}}
{\sum_{u\in \mathcal{V}_{\text{vocab}}}\exp z_{t,u}}.
\]

Only probability differences matter. Adding the same constant to every logit does not change the softmax.

Primary background: Vaswani et al., [Attention Is All You Need](https://arxiv.org/abs/1706.03762).

## 3. Teacher forcing and the one-token shift

During training and likelihood evaluation, the complete target sequence is available. The model receives the input tokens but is scored for predicting each next token:

| Position | Input available | Label |
|---|---|---|
| 1 | token 1 | token 2 |
| 2 | tokens 1–2 | token 3 |
| \(t\) | tokens \(1\ldots t\) | token \(t+1\) |

This is **teacher forcing**. It is efficient because all positions can be processed in parallel under the causal mask.

Generation is different. The model predicts one next token, appends it, and then conditions on its own output. An early wrong token can change all later contexts. Therefore:

- teacher-forced likelihood can show that the correct answer is locally probable;
- free generation tests whether the model actually enters and remains on the correct trajectory;
- the two measurements can disagree without either one being “wrong.”

## 4. Full-sequence loss versus answer-only loss

Suppose a training example is:

> Question: What is Arin Solak's profession? Answer: marine biologist

With full-sequence loss, every token after the first contributes:

\[
\mathcal{L}_{\text{full}}
=
-\sum_{t=2}^{T}\log p_\theta(x_t\mid x_{<t}).
\]

The model is trained on the prompt template as well as the answer. If the prompt is long and the answer short, most supervised positions may be boilerplate rather than factual content.

With answer-only loss, prompt labels are masked:

\[
\ell_t=
\begin{cases}
x_t, & t\in \text{answer positions},\\
-100, & \text{otherwise}.
\end{cases}
\]

PyTorch cross-entropy ignores positions with the configured ignore index. See the official [CrossEntropyLoss documentation](https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html).

Advantages of answer-only loss:

- gradient budget focuses on the factual object;
- changing prompt length does not change the number of supervised prompt tokens;
- boilerplate memorization is reduced;
- comparisons across prompt forms become easier to interpret.

It does not automatically create robust semantics. If the answer is supervised under only one surface form, the model can still learn a narrow prompt-answer association.

## 5. EOS supervision

The end-of-sequence token, EOS, says “the answer ends here.” If EOS is supervised after the answer, the objective contains

\[
-\log p_\theta(\text{EOS}\mid \text{prompt},\text{answer}).
\]

This teaches termination, but it can also change the balance of gradients. In short synthetic answers, EOS is one of only a few supervised positions. If the scientific outcome is the answer string rather than termination behavior, EOS supervision may consume disproportionate capacity or encourage brittle stopping.

The project’s drift ablation compared answer-only training with and without EOS supervision. The selected lower-drift recipe used EOS masking: the EOS label was set to \(-100\). This was an empirical choice, not a universal rule. Other applications may need explicit termination learning.

Important separation:

- **EOS as an input token** can still be present in the sequence.
- **EOS as a supervised target** can be ignored.
- **PAD** is a different concept and should not silently be treated as EOS unless the model and evaluation explicitly define that convention.

## 6. What a tokenizer does

A tokenizer maps raw text to integer token IDs:

\[
\text{text}
\xrightarrow{\text{normalization}}
\text{normalized text}
\xrightarrow{\text{segmentation}}
(s_1,\ldots,s_k)
\xrightarrow{\text{vocabulary}}
(id_1,\ldots,id_k).
\]

The inverse decoder maps IDs back to text, though the round trip may depend on normalization and special-token handling.

Modern language models commonly use subword or byte-aware tokenizers because a fixed word vocabulary cannot cover arbitrary names, morphology, spelling variants, code, and multiple languages. SentencePiece is one influential model-independent subword framework: Kudo and Richardson, [SentencePiece](https://arxiv.org/abs/1808.06226).

The tokenizer is part of the model. An embedding matrix row \(E_j\) corresponds to token ID \(j\). Loading weights with a different ID-to-token mapping can turn every embedding into the wrong symbol even when tensor shapes match.

## 7. Tokenizer fertility

**Fertility** is the average number of tokens required for a linguistic unit, often a word:

\[
\operatorname{fertility}
=
\frac{\text{number of produced tokens}}
{\text{number of words or reference units}}.
\]

Higher fertility is not automatically bad, but it has costs:

- fewer words fit into a fixed token context;
- the model needs more autoregressive steps to produce the same text;
- a word-level fact may require a longer token sequence;
- token-level PPL becomes harder to compare across languages or tokenizers;
- training token budgets correspond to different amounts of human-readable text.

Turkish is morphologically productive. A root can take multiple suffixes, so a tokenizer trained primarily on English may segment Turkish words into many pieces. Tokenizer fertility must therefore be measured on representative Turkish text rather than inferred from vocabulary size.

For direct evidence on Turkish tokenization effects, see Toraman et al., [Impact of Tokenization on Language Models: An Analysis for Turkish](https://arxiv.org/abs/2204.08832).

## 8. Exact answers are token sequences

An answer such as “marine biologist” may tokenize as one token, two tokens, or many tokens. Candidate probability is a sequence probability:

\[
\log p_\theta(y_{1:m}\mid q)
=
\sum_{j=1}^{m}
\log p_\theta(y_j\mid q,y_{<j}).
\]

This creates a length issue. Raw summed log-likelihood tends to penalize longer candidates because it adds more non-positive log-probabilities. Possible scoring rules include:

- total log-likelihood;
- mean log-likelihood per answer token;
- length-penalized log-likelihood;
- probability of a canonical prefix;
- constrained candidate ranking over matched candidates.

The correct rule depends on the claim and must be frozen before seeing outcomes. If candidates have systematically different token lengths by relation or language, an unfrozen scoring rule can create artificial performance differences.

## 9. Padding and attention masks

Batches require equal tensor lengths. Short sequences are padded to a common length:

\[
[x_1,\ldots,x_T]
\rightarrow
[x_1,\ldots,x_T,\text{PAD},\ldots,\text{PAD}].
\]

Two masks have different jobs:

- the **attention mask** prevents the model from treating padded positions as real context;
- the **label mask** prevents padding or prompt tokens from contributing to the loss.

A typical valid setup has:

\[
\text{attention\_mask}_t =
\begin{cases}
1,&\text{real token}\\
0,&\text{padding}
\end{cases}
\]

and

\[
\text{label}_t =
\begin{cases}
\text{target ID},&\text{supervised token}\\
-100,&\text{ignored token}.
\end{cases}
\]

Confusing these masks can yield finite losses while training on the wrong objective.

## 10. Why PAD provenance mattered for Pythia

The project encountered a useful tokenizer lesson. A pinned Pythia weight revision was initially paired with a malformed tokenizer construction that behaved like a two-token vocabulary and produced empty probe encodings. That is not a small quality issue; it destroys the mapping between text and model inputs.

A later official-tokenizer repair then stopped because the tokenizer constructor supplied its own PAD default, conflicting with the frozen expected PAD behavior. The final valid repair explicitly set PAD to null, preserved the exact official tokenizer source identity, and passed save/reload, offset, embedding-compatibility, and probe-encoding gates.

The theory lesson is:

\[
\text{valid model state}
\neq
\text{weight tensors alone}.
\]

A valid state is closer to:

\[
\text{weights}
+\text{architecture config}
+\text{tokenizer files and semantics}
+\text{special-token IDs}
+\text{runtime interpretation}.
\]

## 11. Truncation and block construction

Models have finite sequence limits. Training pipelines may:

- truncate each example;
- pad each example;
- concatenate examples into a token stream;
- pack multiple examples into fixed-length blocks;
- insert boundary or EOS tokens;
- drop or pad the final remainder.

These choices alter what contexts the model sees. Suppose a block size is 128 tokens:

- an answer truncated after token 127 receives incomplete supervision;
- two concatenated facts may attend across their boundary unless isolated;
- padding to 128 wastes computation but preserves example isolation;
- packing increases utilization but introduces neighboring-text context.

The project’s reports freeze block size, padding and construction because “same number of rows” does not imply “same number of trained tokens” or “same contexts.”

## 12. Token budget versus example budget

An epoch is one pass over examples, but examples can have different token lengths. Two arms with 10,000 examples are not dose-matched if one contains twice as many supervised tokens.

Useful counts include:

- raw examples;
- encoded tokens;
- non-padding tokens;
- supervised label tokens;
- optimizer updates;
- examples per optimizer update;
- tokens per optimizer update;
- total token presentations, including repeated epochs.

For cross-lingual experiments, tokenization fertility means that matching raw word counts may still yield different token counts. The treatment contract must specify what “matched budget” means.

## 13. Token-level probability and free generation

Suppose the correct first answer token has probability 0.40, while two alternatives have 0.35 and 0.20. The correct token wins greedy decoding, but the margin is small:

\[
\text{margin}=0.40-0.35=0.05.
\]

If the correct multi-token answer begins with probability 0.40 and later tokens each have probability 0.9, its sequence probability might still be reasonable. But an early alternative can send generation to an entirely different completion.

This motivates several complementary probes:

- **top-1 candidate ranking:** which predefined answer has highest sequence score?
- **teacher-forced NLL:** how probable is the correct sequence?
- **margin:** how far is the correct candidate above its strongest competitor?
- **exact-prefix generation:** does unconstrained or greedy generation begin with the canonical answer?
- **EOS/degeneration tests:** does generation stop and remain coherent?

## 14. Common mistakes

### “The tokenizer is just preprocessing”

False. It defines the model’s discrete input/output coordinate system.

### “One token equals one word”

Usually false. Token boundaries depend on vocabulary, normalization, whitespace rules, bytes, and language.

### “Lower token PPL always means a better cross-model language model”

False. Token PPL is tokenizer-dependent. Cross-tokenizer comparisons need a shared normalization such as word PPL, byte PPL, or bits per byte.

### “If the training loss is finite, the data path is valid”

False. Padding, target masks, answer boundaries, and tokenizer IDs can all be wrong while producing finite values.

## 15. Chapter summary

- A causal LM predicts each next token and is trained by token-level negative log-likelihood.
- Teacher forcing and free generation test different behaviors.
- Answer-only loss masks prompt positions; EOS supervision can also be masked.
- The tokenizer is part of model identity, not incidental preprocessing.
- Fertility affects context capacity, compute, and metric comparability.
- PAD, attention masks, label masks, truncation, and block construction change the actual objective.
- Exact factual answers are token sequences, so length and scoring rules matter.
