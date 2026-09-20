# SPECTRUM literature and terminology audit (20 September 2026)

This note supports the revised manuscript. It distinguishes verified prior results from the manuscript's own mathematical observations. It is not a claim that a search can establish exhaustive absence of prior work.

## Recommended contribution positioning

The strongest supportable claim is **longitudinal preservation of the distribution within correct solutions under self-generated-data learning**, with a recalibrated, continuously weighted generation operator and ordinary student inference. Repeated generation and retraining already exist; accuracy–diversity trade-offs already exist; occupancy/rarefaction estimators already exist. Their combination in the precise experimental setting, the proximal generation operator, and the correct-conditioned longitudinal measurements should carry the contribution.

Suggested contributions:

1. **Diagnose an overlooked endpoint of iterative self-distillation.** Separate task correctness from the distribution over correct implementations, and characterize their diverging trajectories across repeated self-distillation. Present the factorization as an explanatory proposition, not a newly discovered probability law.
2. **Formalize Looped Self-Distillation as a modular experimental and learning framework.** Re-estimate a generation rule from the current student, sample a fresh corpus, update a single student, and repeat. Existing sample-then-SFT generators can instantiate the interface. This is not a claim to have invented iterative self-training, and direct RL is not automatically an instance of SFT.
3. **Introduce SPECTRUM as its diversity-preserving instantiation.** Derive the proximal spectral operator and evaluate the resulting standard-inference students. Existing results support better correct-implementation richness and retention against the measured Plain and projection controls; superiority to UA-RL, other datasets, or other models awaits the marked experiments.

## What the nearest papers actually do

| Work | Verified protocol | Implication for our narrative |
|---|---|---|
| SSD, Zhang et al. (2026) | A frozen starting model generates one corpus, followed by SFT; training iterations are gradient steps, not repeated corpus refreshes. It explicitly analyzes precision versus exploration, useful token forks, and conditional head entropy. | Cite as a direct raw self-distillation baseline. Say its reported procedure evaluates a distillation stage; do not say it ignores diversity. Our endpoint is implementation richness among correct outputs across repeated stages. |
| SPD, Hao et al. (2026) | Algorithm 1 extracts a gradient-derived KV subspace, generates one completion per prompt with projection hooks, removes hooks, and performs LoRA SFT. Its five epochs are not five regenerated-data rounds. | Keep out of the abstract/motivation if desired. Cite the relationship where spectral calibration or the projection design is documented. A locally implemented projection ablation is not automatically an exact published-method reproduction. |
| UA-RL, Hu et al. (2026) | Online GRPO-style policy optimization; strategy-cluster size reweights normalized advantages. It evaluates high-level correct-strategy coverage with human reference methods. | This is a diversity-aware RL comparator, not a self-distillation method. It already establishes the importance of diversity within correct solutions. |
| STaR, Zelikman et al. (2022) | Repeated rationale generation, answer-conditioned rationalization, and correct-rationale fine-tuning. Arithmetic runs 16 outer iterations; GSM8K reports 36 iterations without rationalization and 10 additional iterations with rationalization. | Generic repeated self-training is not new. |
| ReST, Gulcehre et al. (2023) | Alternates outer Grow steps and inner Improve steps; data are sampled from the latest policy, combined with original data, ranked/filtered, and reused for offline updates. It evaluates a second Grow step. | Data-generation/update loops are established and can involve data accumulation. |
| ReST-EM, Singh et al. (2024) | Repeated generation and binary-reward filtering; each M-step restarts from the base model. Three math rounds and two code rounds are plotted. Later rounds regress on APPS/HumanEval; the paper contrasts three rounds with a larger single-round corpus. | Do not claim first longitudinal self-training study or first later-round degradation. Our evolving warm-started student, raw-corpus learning, generator re-estimation, and within-correct richness endpoint are specific differences. |
| SD-Zero, He et al. (2026) | Distills reward-conditioned self-revision into a generator. Section 3.4 synchronizes the teacher after one epoch and reports gains in a second phase. | Even explicitly iterative self-distillation exists by 2026. Use a narrower framework claim. |

Primary sources: [SSD §2–4](https://arxiv.org/html/2604.01193v2), [SPD Algorithm 1 and Appendix A](https://arxiv.org/html/2605.22675v1), [UA-RL §3–4](https://arxiv.org/html/2601.08763v2), [STaR](https://arxiv.org/pdf/2203.14465), [ReST](https://arxiv.org/pdf/2308.08998), [ReST-EM](https://arxiv.org/pdf/2312.06585), [SD-Zero §3.4](https://arxiv.org/html/2604.12002v2).

## Has anyone discussed correctness versus diversity among correct solutions?

**Yes, the broad distinction is already explicit.** UA-RL optimizes rare correct strategies and its `cover@n` is recall against canonical human solution methods. DARLING learns semantic partitions and jointly optimizes quality and diversity. Dynamic Stability of LLM-Generated Code analyzes algorithmic and runtime variation among functionally correct programs. These are sufficient to rule out a broad first-discovery claim. [UA-RL](https://aclanthology.org/2026.findings-acl.1982/), [DARLING](https://arxiv.org/abs/2509.02534), [Dynamic Stability](https://arxiv.org/abs/2511.07463).

The exact elementary decomposition remains useful in our paper:

- For a fixed prompt x, let a = P(correct | x), and q_j = P(class j | correct, x).
- Then P(correct and class j | x) = a q_j.
- Under independent sampling from a fixed policy, pass@k = 1 − (1 − a)^k, whereas expected correct-class richness is Σ_j [1 − (1 − a q_j)^k].
- Therefore two policies can agree on **all** per-prompt pass@k values and have different correct-class distributions and richness. Matching only aggregate benchmark pass@1 does not imply matching aggregate pass@k, because the per-prompt a values can differ.
- Sampling b times from the correct-conditioned distribution gives Σ_j [1 − (1 − q_j)^b], which removes success probability from the population target. Finite-sample eligibility and cohort matching still need to be reported.

Recommended wording: “We make this distinction explicit through a correctness-conditioned factorization and use it to study what repeated self-distillation preserves.” Avoid “we are the first to show correctness and diversity differ.” This search did not verify an identical earlier formulation, but absence from these papers is not proof of novelty of the factorization.

## Conventional metric names

`C_k` and `D_b` are notation, not established community-wide metric names. Their finite-pool estimator is a classical occupancy/rarefaction calculation. Hurlbert's expected-species-number formula is exactly the hypergeometric structure used here. [Hurlbert (1971)](https://esajournals.onlinelibrary.wiley.com/doi/10.2307/1934145).

| Recommended table label | Definition | Avoid |
|---|---|---|
| pass@k | Probability of at least one verified success in k samples | Calling it a direct measure of implementation diversity |
| Correct AST richness @k | Expected number of distinct correct normalized AST classes in k total samples | Rebranding it as canonical `cover@k`; UA-RL uses that for reference recall |
| Correct-conditioned AST richness @b | Rarefied richness of b correct samples, among eligible tasks | Claiming the eligible cohort is automatically identical between methods |
| Richness retention (%) | Ratio to initial-model richness at the same sampling budget | Calling it survival of the same AST identities |
| Eligible tasks | Number of tasks with at least b correct samples | Omitting denominator changes |

“Correct-solution coverage” is understandable narrative language, but “richness” is more precise in tables because the metric counts classes rather than measuring probability mass or recall against an exhaustive reference set. AST classes are structural equivalence classes, not validated semantic strategies.

## Why looped transformers and recursive model collapse differ

Universal Transformers and recurrent-depth language models repeat a neural block during one forward computation. They increase inference computation through hidden-state recurrence with fixed deployed weights. Our loop changes the training corpus and model parameters across learning rounds. These are different recurrence axes; cite briefly in related work or an appendix, rather than building the main motivation around a naming similarity. [Universal Transformers](https://arxiv.org/abs/1807.03819), [Recurrent Depth](https://arxiv.org/abs/2502.05171).

Recursive model-collapse research studies fidelity to an original data distribution as generations of synthetic data feed subsequent training. Shumailov et al. identify loss of distribution tails. Gerstgrasser et al. contrast replacement with retaining original data and accumulating later synthetic generations, showing accumulation can prevent collapse under their settings. Our target is the conditional distribution among outputs that already satisfy a task checker, potentially contracting while task accuracy improves. Fixed-size fresh-corpus learning and accumulated-data learning are different data policies; SPECTRUM does not refute accumulation, and accumulation is a complementary control. [Recursive collapse](https://arxiv.org/abs/2305.17493), [Accumulation](https://arxiv.org/abs/2404.01413).

Calling our setting “iterative self-improvement” or “a controlled model–data feedback loop” is precise. Stronger claims of recursive self-improvement of the learning algorithm itself require additional evidence. The current intervention is re-estimated; the update algorithm is fixed.

## UA-RL implementation status and faithful adaptation

The author-linked public repository is [zhiyuanhubj/Uniqueness-Aware-RL](https://github.com/zhiyuanhubj/Uniqueness-Aware-RL). Verified HEAD by `git ls-remote` on 20 September 2026:

`cfa7c8d1673c50388e80bc5e0aa0ff5fd1147428`

It contains only a README and no runnable training implementation. The ACL paper points to software on its submission page; public runnable code was not verified there. A local implementation must be labeled an independent implementation or coding adaptation.

Paper-faithful essentials: form a group-normalized reward advantage, cluster all group rollouts with an LLM judge, multiply the advantage by inverse cluster frequency to exponent alpha, and optimize using the GRPO objective. Weighting includes negative advantages. Replacing the judge with AST fingerprints changes the strategy partition; label this “UA-RL (AST adaptation)” rather than a faithful exact reproduction. The original uses a larger same-family judge, eight rollouts, learning rate 5e−7, temperature 1.0, and KL coefficient .001. [UA-RL methodology](https://arxiv.org/html/2601.08763v2).

## Recommended ready-to-use related-work paragraph

“Iterative self-training already alternates self-generation with parameter updates, including STaR, ReST, and ReST-EM; recent self-distillation also refreshes the supervising policy. Our focus is the distribution retained within correct solutions across this feedback loop. Diversity-aware reinforcement learning, including DARLING and UA-RL, explicitly rewards varied high-quality or correct outputs. We instead modify the generation operator used to construct the next training corpus and evaluate the resulting student without the intervention. This separates the question of producing a varied rollout set from whether that variation survives subsequent learning.”

This paragraph should be adapted to the final method details. Keep citations to relevant prior mechanisms even if the projection control is presented only as an ablation. Repositioning a baseline does not remove the need to credit related work.
