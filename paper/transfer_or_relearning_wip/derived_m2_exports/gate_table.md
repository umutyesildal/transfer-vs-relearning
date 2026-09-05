# M2 gate table

Input manifest SHA-256: `8cd18cd458b8261205721e93f09310fe67dc0c133f5daa772de4a36688d61ad9`

| Model | Criterion | Pass |
|---|---|:---:|
| OLMo | M2-A EN-to-EN drop ≤ 0.05 | true |
| OLMo | M2-A OSCAR BPB delta ≤ −0.07400058 | true |
| OLMo | M2-A WikiText BPB delta ≤ 0.32192809 | true |
| OLMo | Relearning 95% CI lower bound > 0 | false |
| OLMo | Relearning point gain ≥ 0.05 | false |
| OLMo | All frozen primary gates pass | false |
| Qwen | M2-A EN-to-EN drop ≤ 0.05 | true |
| Qwen | M2-A OSCAR BPB delta ≤ −0.07400058 | true |
| Qwen | M2-A WikiText BPB delta ≤ 0.32192809 | true |
| Qwen | Relearning 95% CI lower bound > 0 | true |
| Qwen | Relearning point gain ≥ 0.05 | false |
| Qwen | All frozen primary gates pass | false |
| SmolLM | M2-A EN-to-EN drop ≤ 0.05 | false |
| SmolLM | M2-A OSCAR BPB delta ≤ −0.07400058 | true |
| SmolLM | M2-A WikiText BPB delta ≤ 0.32192809 | true |
| SmolLM | Relearning 95% CI lower bound > 0 | false |
| SmolLM | Relearning point gain ≥ 0.05 | false |
| SmolLM | All frozen primary gates pass | false |

All three `all_primary_gates_pass` values are false.
