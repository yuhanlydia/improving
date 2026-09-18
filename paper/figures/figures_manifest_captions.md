# SPECTRUM figure manifest and caption drafts

Three figures are produced as vector PDF with embedded TrueType fonts, plus 240-dpi PNG previews. Source script: `support/make_figures.py`. All deliverables use the final paper name SPECTRUM. No formal experimental result was generated or simulated. Figures 4–6 are future-data prompt specifications only and have no rendered charts.

| Paper figure | Vector file | Preview | Size (inches) | Evidence status | Prompt document |
|---|---|---|---|---|---|
| 1 | fig1_observation.pdf | fig1_observation.png | 7 × 2.25 | Measured pilot arm means | figure_prompts/fig1_observation.md |
| 2 | fig2_method.pdf | fig2_method.png | 7 × 2.72 | Confirmed method dependency graph | figure_prompts/fig2_method.md |
| 3 | fig3_gain.pdf | fig3_gain.png | 7 × 2.20 | Analytic function, no empirical spectra | figure_prompts/fig3_gain.md |
| Future 4 | Not rendered | Not rendered | To be chosen after data | Formal results missing | figure_prompts/fig4_formal.md |
| Future 5 | Not rendered | Not rendered | To be chosen after data | Mechanism measurements missing | figure_prompts/fig5_mechanism.md |
| Future 6 | Not rendered | Not rendered | To be chosen after data | Retention trajectories missing | figure_prompts/fig6_retention.md |

## Figure 1 caption

**Correctness ranking need not determine correct-code diversity ranking.** Exploratory final-checkpoint pilot with Qwen2.5-Coder-1.5B-Instruct after one self-distillation cycle (64 held-out MBPP tasks, 64 samples per task, seed 42). SSD has the highest reported pass@1, while SPECTRUM has the highest expected AST coverage in four correct draws. Dots are reported per-arm means; no per-arm confidence intervals are supplied. Coverage eligibility may differ across arms. The separately reported paired SPECTRUM−SSD coverage difference is +0.0312 (pointwise 95% CI [0.0095, 0.0550]), and the paired pass@1 difference is −0.244 percentage points ([−0.854, 0.342]); the paired coverage effect need not equal a difference of the displayed means. This first-fence extraction sensitivity analysis was post hoc, used local execution, and did not apply multiple-comparison correction. AST coverage is an implementation proxy, not semantic algorithm coverage.

Source: [immutable pilot report](https://github.com/yuhanlydia/improving/blob/d8a50903de671cdb7e5c23a28ff43de1c32c16b5/results/pilot_seed42_codecentric/README.md). The exact source arm “Spectral-soft” is displayed as SPECTRUM; “SPD-hard” retains its source label. The rounded means are Plain/SSD/SPD-hard/SPECTRUM pass@1 = 36.82/36.89/36.87/36.65%, D4AST = 3.393/3.391/3.409/3.422.

## Figure 2 caption

**SPECTRUM separates temporary spectral generation from native learning.** Reference-loss gradients at native K/V outputs form the uncentered gradient second moment C=(1/M)Σ_{i,u} g_{iu}g_{iu}ᵀ, pooling all nonpadding token positions while the reference cross-entropy is completion-masked. The soft transform T=[I+τ(I−C̄)]⁻¹, C̄=C/λ_max(C), is temporarily folded into weights and biases to generate one raw completion per training prompt. The original native checkpoint θ_t is restored before ordinary LoRA on all raw outputs with all-token loss. Merged updates produce native θ_{t+1} for evaluation and for recomputing C and T next round. Solid arrows denote training state or data flow; the dashed branch denotes native evaluation without a spectral transform.

## Figure 3 caption

**Analytic soft gain attenuates continuously without removing directions.** The gain on a second-moment eigen-direction is s_τ(μ)=1/[1+τ(1−μ)], where μ=λ/λ_max∈[0,1]. For finite τ≥0 every gain is positive, and at the default τ=1 gains lie in [1/2,1]. Larger normalized second-moment eigenvalues receive larger gains. Curves are deterministic formula evaluations, not measured model spectra, experimental τ-ablation outcomes, or evidence that eigenvectors correspond to algorithms.

## Visual verification

The PNG previews were visually inspected at readable resolution. The observation plot uses dots and explicit expanded axes instead of truncated bars; no unsupported per-arm uncertainty is shown. The method figure returns its loop to the exact native calibration checkpoint and sends raw completions separately to LoRA. The gain plot is labeled analytic and contains no measured-spectrum or arbitrary hard-threshold curve. Headline/body spacing was revised after the first inspection.

Final notation QA: all checkpoint labels use θ_t and θ_{t+1}; the calibration sum uses example–position indices i,u and denominator M; normalized eigenvalues use μ=λ/λ_max. All three PDFs were regenerated at their original dimensions and the modified calibration and gain labels were visually inspected.
