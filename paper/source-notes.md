# Source notes for SPECTRUM

Checked 15 September 2026. The bibliography contains 15 references, with authors and titles checked against primary paper pages. ACL and NeurIPS entries use official proceedings; preprints remain arXiv entries. Existing empirical material is the 64-problem MBPP pilot with seed 42.

## Positioning

**Suggested contribution sentence:** “We study whether a continuous spectral filter on gradient-informed K/V activations can retain a broader set of correct implementations through raw-output self-distillation.”

SPD is the immediate methodological predecessor: it gathers gradients of a correctness-aligned calibration loss with respect to K/V activations, retains the leading right-singular vectors, applies their orthogonal projectors during generation, then removes the hooks before training on raw completions. Its calibration set contains prompt–answer pairs. The present construction keeps that pipeline and replaces the rank cutoff with a continuous gain at every eigenvalue. Cite SPD where introducing the pipeline and the hard-projector baseline. [SPD, Sections 3.2–3.3](https://arxiv.org/html/2605.22675v1).

For the specified method, write the statistic as an **uncentered gradient second moment**,

\[
C=M^{-1}\sum_t g_tg_t^\top,\qquad \bar C=C/\lambda_{\max}(C),\qquad T_\tau=[I+\tau(I-\bar C)]^{-1}.
\]

The intervention filters activations using gradient-derived geometry; it does not filter the optimizer's parameter gradients. For nonzero positive-semidefinite C and finite nonnegative tau, the eigenvalue gain is \(1/[1+\tau(1-\lambda_i/\lambda_{\max})]\). This gives nonzero gains in every direction, including the nullspace. The operator is the proximal map of the quadratic penalty \(\tfrac{\tau}{2}z^\top(I-\bar C)z\), following standard proximal-operator theory. These are properties of the stated construction; diversity among generated programs is an empirical quantity. [Parikh and Boyd](https://web.stanford.edu/~boyd/papers/prox_algs.html).

Soft spectral control is established in activation steering: conceptors provide soft projections, and SEA uses covariance-based spectral representation edits for alignment. The distinctive research question here combines a gradient-derived K/V filter, the specified complementary quadratic penalty, raw-output distillation, and measurement of diversity *within correct code*. [Conceptors](https://arxiv.org/abs/2410.16314), [SEA](https://proceedings.neurips.cc/paper_files/paper/2024/hash/684c59d614fe6ae74a3be8c3ef07e061-Abstract-Conference.html).

The natural narrative is: self-distillation changes which solutions the model supplies to itself; a rank cutoff removes low-energy activation directions; a smooth filter lets their influence vary continuously; the experiment tracks correctness and the range of correct implementations before and after distillation. The interpretation that weaker gradient directions carry alternative valid implementations is a mechanism hypothesis to examine with the pilot and later experiments.

## Reference map

| BibTeX key | Verified source and role |
|---|---|
| `hao2026spd` | [Hao et al., 2026](https://arxiv.org/abs/2605.22675). Closest pipeline and hard K/V projection comparison; arXiv preprint. |
| `zhang2026ssd` | [Zhang et al., 2026](https://arxiv.org/abs/2604.01193). Raw code samples followed by supervised fine-tuning; decoding governs the precision–exploration tradeoff. Version 2 is dated 24 June 2026; arXiv preprint. |
| `hu2026rewardingrare` | [Hu et al., 2026](https://arxiv.org/abs/2601.08763). Rewards rare correct strategy clusters with an LLM judge. Evaluation covers mathematics, physics, and medical reasoning; use for the strategy-diversity motivation. arXiv preprint. |
| `shumailov2024collapse` | [Shumailov et al., Nature 2024](https://www.nature.com/articles/s41586-024-07566-y). Recursive synthetic-data training can lose low-probability events. Supports tracking what self-training retains over generations. |
| `gerstgrasser2024accumulating` | [Gerstgrasser et al., 2024](https://arxiv.org/abs/2404.01413). Retaining original data while accumulating generations changes collapse behavior. Keep the comparison specific to replacement versus accumulation. |
| `wang2023selfinstruct` | [Wang et al., ACL 2023](https://aclanthology.org/2023.acl-long.754/). Early instruction bootstrapping with generated instructions, inputs, and outputs, including filtering. Historical synthetic-supervision context. |
| `hu2022lora` | [Hu et al., ICLR 2022](https://openreview.net/forum?id=nZeVKeeFYf9), [arXiv version](https://arxiv.org/abs/2106.09685). Parameter-efficient adaptation used for the distillation stage. |
| `liu2023evalplus` | [Liu et al., NeurIPS 2023](https://proceedings.neurips.cc/paper_files/paper/2023/hash/43e9d647ccd3e4b7b5baab53f0368686-Abstract-Conference.html). Strengthened tests expose incorrect programs missed by original benchmark tests; motivates the correctness gate used in diversity analysis. |
| `austin2021mbpp` | [Austin et al., 2021](https://arxiv.org/abs/2108.07732). Original MBPP source, describing 974 Python programming tasks; arXiv preprint. |
| `chen2021humaneval` | [Chen et al., 2021](https://arxiv.org/abs/2107.03374). HumanEval and execution-based code generation assessment, including repeated sampling and pass@k; arXiv preprint. |
| `hui2024qwen25coder` | [Hui et al., 2024](https://arxiv.org/abs/2409.12186). Qwen2.5-Coder model-family source; the revised report lists 0.5B through 32B models; arXiv preprint. |
| `parikh2014proximal` | [Parikh and Boyd, 2014](https://web.stanford.edu/~boyd/papers/prox_algs.html). Standard proximal-map background for the quadratic resolvent. |
| `mobahi2020selfdistillation` | [Mobahi et al., NeurIPS 2020](https://proceedings.neurips.cc/paper/2020/hash/2288f691b58edecadcc9a8691762b4fd-Abstract.html). Hilbert-space analysis shows repeated self-distillation progressively restricts the usable basis functions; a conceptual connection to spectral regularization under that model's assumptions. |
| `qiu2024sea` | [Qiu et al., NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/684c59d614fe6ae74a3be8c3ef07e061-Abstract-Conference.html). Covariance-based spectral activation editing for truthfulness and bias. |
| `postmus2024conceptors` | [Postmus and Abreu, 2024](https://arxiv.org/abs/2410.16314). Soft projection matrices for activation steering, including Boolean composition. Presented at the MINT workshop at NeurIPS 2024; cited as arXiv, not NeurIPS main proceedings. Version 4 fixes a sign in Equation 10. |

LiveCodeBench is omitted because it is not part of the specified pilot; it can be added when a concrete evaluation plan uses it. No benchmark score from the cited papers should be copied into a SPECTRUM results table.

## Naming check

The final working name is **SPECTRUM: Preserving Correct-Code Diversity in Self-Distillation**. This is an editorial naming choice, with a narrow collision search rather than a uniqueness claim.

Previously considered names have nearby uses:

- **SCOPE:** [Spectral Concentration by Distributionally Robust Joint Covariance-Precision Estimation](https://arxiv.org/abs/2511.14146), and [Self-Play via Co-Evolving Policies for Open-Ended Tasks](https://arxiv.org/abs/2605.31433).
- **PRISM:** [Dynamic and Flexible Benchmarking of LLMs Code Generation with Monte Carlo Tree Search](https://arxiv.org/abs/2504.05500), and [A Unified Framework for Post-Training LLMs Without Verifiable Rewards](https://arxiv.org/abs/2601.04700).
- **SPECTRA:** [SpecTra: Enhancing the Code Translation Ability of Language Models by Generating Multi-Modal Specifications](https://arxiv.org/abs/2405.18574), and [Spectra: Rethinking Optimizers for LLMs Under Spectral Anisotropy](https://arxiv.org/abs/2602.11185).

## Metadata decisions

Gerstgrasser et al. has an [OpenReview record](https://openreview.net/forum?id=5B2K4LRgmz), but this session could directly inspect only the arXiv record, so the bibliography retains that verified version. LoRA's ICLR 2022 status was visible in the indexed official OpenReview record. Proximal Algorithms uses 2014 as on the author-maintained publication page; page numbers are omitted because the accessible author PDF and later citation metadata use different pagination. The Nature article has a [2025 author correction](https://www.nature.com/articles/s41586-025-08905-3), which should be consulted before quoting a precise formal result.
