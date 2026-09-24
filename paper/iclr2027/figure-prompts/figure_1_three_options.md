# Figure 1 — Can increasing correctness conceal contraction within correct outputs?

## A. Evidence Inventory

**Question:** Can increasing correctness conceal contraction within correct outputs?

**Supported answer:** In the saved five-round MBPP run, Plain and SPECTRUM increase pass@1 while losing AST richness; SPECTRUM loses less.

**Fact lock:** {"plain":{"pass1_percent":[37.925,38.425,39.15,39.65,40.7875,41.3],"C16":[4.016,3.808,3.634,3.372,3.19,3.09],"Simpson":[0.84297,0.802178,0.781279,0.738599,0.707753,0.691991],"paired_D4_change":[-0.138258,-0.220248,-0.376093,-0.500308,-0.574162],"paired_D4_ci95":[[-0.207978,-0.068049],[-0.293476,-0.14518],[-0.452677,-0.298745],[-0.573634,-0.429593],[-0.653711,-0.498749]],"paired_D4_n":[245,246,240,244,241]},"spectral_soft":{"pass1_percent":[37.925,37.8375,38.3625,39.05,39.775,40.175],"C16":[4.016,3.848,3.768,3.662,3.588,3.606],"Simpson":[0.84297,0.822225,0.809408,0.773249,0.75196,0.765747],"paired_D4_change":[-0.099678,-0.139992,-0.221023,-0.3163,-0.315297],"paired_D4_ci95":[[-0.166006,-0.035438],[-0.211323,-0.069725],[-0.304755,-0.145722],[-0.391983,-0.243946],[-0.394451,-0.239572]],"paired_D4_n":[242,236,244,242,245]}}

**Missing/boundary:** Independent training seeds and intermediate 64-sample pools; no global semantic diversity measurement.

**Design skill:** `designing-experiment-figures`. **Production:** `programmatic-figure-spec`.

## B. Three candidate designs

| Option | Reading path | Main risk |
|---|---|---|
| 1 | Phase trajectory with conditional checks | Misreading local/conditional evidence as a global guarantee. |
| 2 | Longitudinal retention with aligned diagnostics | Misreading local/conditional evidence as a global guarantee. |
| 3 | Conditional retention as the focal evidence | Misreading local/conditional evidence as a global guarantee. |

**Recommendation:** Option 1, used in the supplied manuscript, gives the principal relationship the largest area and matches the available evidence.

## C. Option 1 — Phase trajectory with conditional checks

**Rationale:** Place pass@1 (%) on x and C16 on y in the left 58% panel. Connect rounds 0 through 5 in order and label their numbers. Put paired D4 change from initialization versus rounds 1--5, including CI bars, in the middle 21%; place Simpson diversity versus rounds 0--5 in the right 21%. A shared legend maps plain to Plain and spectral_soft to SPECTRUM. Label panels (a) Accuracy and breadth, (b) Equal correct draws, (c) Concentration. This prioritizes the accuracy/breadth separation.

### Standalone English production prompt (3094 characters)

```text
Create Figure 1 for an anonymous ICLR paper using programmatic-figure-spec. The immediate takeaway is: In the saved five-round MBPP run, Plain and SPECTRUM increase pass@1 while losing AST richness; SPECTRUM loses less. Place pass@1 (%) on x and C16 on y in the left 58% panel. Connect rounds 0 through 5 in order and label their numbers. Put paired D4 change from initialization versus rounds 1--5, including CI bars, in the middle 21%; place Simpson diversity versus rounds 0--5 in the right 21%. A shared legend maps plain to Plain and spectral_soft to SPECTRUM. Label panels (a) Accuracy and breadth, (b) Equal correct draws, (c) Concentration. This prioritizes the accuracy/breadth separation. Locked facts: All arrays below are saved measurements (six round-0--5 entries, or five round-1--5 paired changes). {"plain":{"pass1_percent":[37.925,38.425,39.15,39.65,40.7875,41.3],"C16":[4.016,3.808,3.634,3.372,3.19,3.09],"Simpson":[0.84297,0.802178,0.781279,0.738599,0.707753,0.691991],"paired_D4_change":[-0.138258,-0.220248,-0.376093,-0.500308,-0.574162],"paired_D4_ci95":[[-0.207978,-0.068049],[-0.293476,-0.14518],[-0.452677,-0.298745],[-0.573634,-0.429593],[-0.653711,-0.498749]],"paired_D4_n":[245,246,240,244,241]},"spectral_soft":{"pass1_percent":[37.925,37.8375,38.3625,39.05,39.775,40.175],"C16":[4.016,3.848,3.768,3.662,3.588,3.606],"Simpson":[0.84297,0.822225,0.809408,0.773249,0.75196,0.765747],"paired_D4_change":[-0.099678,-0.139992,-0.221023,-0.3163,-0.315297],"paired_D4_ci95":[[-0.166006,-0.035438],[-0.211323,-0.069725],[-0.304755,-0.145722],[-0.391983,-0.243946],[-0.394451,-0.239572]],"paired_D4_n":[242,236,244,242,245]}} Paired D4 intervals resample evaluation tasks 2,000 times; eligibility varies by contrast. Simpson uses tasks with at least two correct outputs. No uncertainty is plotted for phase or Simpson points. Use vector plotting/code, white background, black SPECTRUM circles/solid lines, gray Plain squares/dashed lines, and light-gray Initial-model diamonds/dotted lines. At 6.65-inch paper width, retain readable horizontal type (8 pt labels), thin rules, and no colored fills. Bars start at zero; point axes may be cropped only with explicit ticks. No gradients, 3D, invented observations, extra datasets, significance stars, fitted curves, or dual axes. Export PDF and 240-dpi PNG.  Exact method labels are Initial model, Plain, SPECTRUM where present. Caption: Five MBPP self-distillation rounds, 500 tasks and 16 samples per task. Native-student point estimates; paired D4 changes are relative to initialization on common eligible tasks, with archived pointwise 95% task-bootstrap intervals. One training seed. AST classes are structural proxies. Alt text: Accuracy rises as correct AST richness falls. SPECTRUM retains more richness and more dispersed correct outputs than Plain. Boundary: Independent training seeds and intermediate 64-sample pools; no global semantic diversity measurement. Preserve values, comparison sets, sample budgets, uncertainty meaning, eligibility, and selection rules; never turn unavailable evidence into plotted facts.
```

**Caption:** Five MBPP self-distillation rounds, 500 tasks and 16 samples per task. Native-student point estimates; paired D4 changes are relative to initialization on common eligible tasks, with archived pointwise 95% task-bootstrap intervals. One training seed. AST classes are structural proxies.

**Alt text:** Accuracy rises as correct AST richness falls. SPECTRUM retains more richness and more dispersed correct outputs than Plain.

## D. Option 2 — Longitudinal retention with aligned diagnostics

**Rationale:** Use the left 55% for C16 against rounds 0--5. In the right 45%, stack three aligned strips for pass@1 (%), paired D4 changes with CI bars, and Simpson diversity. Each strip has its own labeled y-axis and shares round order. Show all initial and final values beside their respective points. This emphasizes accumulation across rounds; do not add a fitted decay rate.

### Standalone English production prompt (2981 characters)

```text
Create Figure 1 for an anonymous ICLR paper using programmatic-figure-spec. The immediate takeaway is: In the saved five-round MBPP run, Plain and SPECTRUM increase pass@1 while losing AST richness; SPECTRUM loses less. Use the left 55% for C16 against rounds 0--5. In the right 45%, stack three aligned strips for pass@1 (%), paired D4 changes with CI bars, and Simpson diversity. Each strip has its own labeled y-axis and shares round order. Show all initial and final values beside their respective points. This emphasizes accumulation across rounds; do not add a fitted decay rate. Locked facts: All arrays below are saved measurements (six round-0--5 entries, or five round-1--5 paired changes). {"plain":{"pass1_percent":[37.925,38.425,39.15,39.65,40.7875,41.3],"C16":[4.016,3.808,3.634,3.372,3.19,3.09],"Simpson":[0.84297,0.802178,0.781279,0.738599,0.707753,0.691991],"paired_D4_change":[-0.138258,-0.220248,-0.376093,-0.500308,-0.574162],"paired_D4_ci95":[[-0.207978,-0.068049],[-0.293476,-0.14518],[-0.452677,-0.298745],[-0.573634,-0.429593],[-0.653711,-0.498749]],"paired_D4_n":[245,246,240,244,241]},"spectral_soft":{"pass1_percent":[37.925,37.8375,38.3625,39.05,39.775,40.175],"C16":[4.016,3.848,3.768,3.662,3.588,3.606],"Simpson":[0.84297,0.822225,0.809408,0.773249,0.75196,0.765747],"paired_D4_change":[-0.099678,-0.139992,-0.221023,-0.3163,-0.315297],"paired_D4_ci95":[[-0.166006,-0.035438],[-0.211323,-0.069725],[-0.304755,-0.145722],[-0.391983,-0.243946],[-0.394451,-0.239572]],"paired_D4_n":[242,236,244,242,245]}} Paired D4 intervals resample evaluation tasks 2,000 times; eligibility varies by contrast. Simpson uses tasks with at least two correct outputs. No uncertainty is plotted for phase or Simpson points. Use vector plotting/code, white background, black SPECTRUM circles/solid lines, gray Plain squares/dashed lines, and light-gray Initial-model diamonds/dotted lines. At 6.65-inch paper width, retain readable horizontal type (8 pt labels), thin rules, and no colored fills. Bars start at zero; point axes may be cropped only with explicit ticks. No gradients, 3D, invented observations, extra datasets, significance stars, fitted curves, or dual axes. Export PDF and 240-dpi PNG.  Exact method labels are Initial model, Plain, SPECTRUM where present. Caption: Five MBPP self-distillation rounds, 500 tasks and 16 samples per task. Native-student point estimates; paired D4 changes are relative to initialization on common eligible tasks, with archived pointwise 95% task-bootstrap intervals. One training seed. AST classes are structural proxies. Alt text: Accuracy rises as correct AST richness falls. SPECTRUM retains more richness and more dispersed correct outputs than Plain. Boundary: Independent training seeds and intermediate 64-sample pools; no global semantic diversity measurement. Preserve values, comparison sets, sample budgets, uncertainty meaning, eligibility, and selection rules; never turn unavailable evidence into plotted facts.
```

**Caption:** Five MBPP self-distillation rounds, 500 tasks and 16 samples per task. Native-student point estimates; paired D4 changes are relative to initialization on common eligible tasks, with archived pointwise 95% task-bootstrap intervals. One training seed. AST classes are structural proxies.

**Alt text:** Accuracy rises as correct AST richness falls. SPECTRUM retains more richness and more dispersed correct outputs than Plain.

## E. Option 3 — Conditional retention as the focal evidence

**Rationale:** Use the upper 55% for paired D4 change from initialization against rounds 1--5 with exact CI bars and zero reference. Below it, use 30% for the measured pass@1-versus-C16 trajectories and 15% for Simpson-versus-round. Keep each plot independent; no linking axes with arrows implying causality. This emphasizes the within-correct result while retaining every source series.

### Standalone English production prompt (2988 characters)

```text
Create Figure 1 for an anonymous ICLR paper using programmatic-figure-spec. The immediate takeaway is: In the saved five-round MBPP run, Plain and SPECTRUM increase pass@1 while losing AST richness; SPECTRUM loses less. Use the upper 55% for paired D4 change from initialization against rounds 1--5 with exact CI bars and zero reference. Below it, use 30% for the measured pass@1-versus-C16 trajectories and 15% for Simpson-versus-round. Keep each plot independent; no linking axes with arrows implying causality. This emphasizes the within-correct result while retaining every source series. Locked facts: All arrays below are saved measurements (six round-0--5 entries, or five round-1--5 paired changes). {"plain":{"pass1_percent":[37.925,38.425,39.15,39.65,40.7875,41.3],"C16":[4.016,3.808,3.634,3.372,3.19,3.09],"Simpson":[0.84297,0.802178,0.781279,0.738599,0.707753,0.691991],"paired_D4_change":[-0.138258,-0.220248,-0.376093,-0.500308,-0.574162],"paired_D4_ci95":[[-0.207978,-0.068049],[-0.293476,-0.14518],[-0.452677,-0.298745],[-0.573634,-0.429593],[-0.653711,-0.498749]],"paired_D4_n":[245,246,240,244,241]},"spectral_soft":{"pass1_percent":[37.925,37.8375,38.3625,39.05,39.775,40.175],"C16":[4.016,3.848,3.768,3.662,3.588,3.606],"Simpson":[0.84297,0.822225,0.809408,0.773249,0.75196,0.765747],"paired_D4_change":[-0.099678,-0.139992,-0.221023,-0.3163,-0.315297],"paired_D4_ci95":[[-0.166006,-0.035438],[-0.211323,-0.069725],[-0.304755,-0.145722],[-0.391983,-0.243946],[-0.394451,-0.239572]],"paired_D4_n":[242,236,244,242,245]}} Paired D4 intervals resample evaluation tasks 2,000 times; eligibility varies by contrast. Simpson uses tasks with at least two correct outputs. No uncertainty is plotted for phase or Simpson points. Use vector plotting/code, white background, black SPECTRUM circles/solid lines, gray Plain squares/dashed lines, and light-gray Initial-model diamonds/dotted lines. At 6.65-inch paper width, retain readable horizontal type (8 pt labels), thin rules, and no colored fills. Bars start at zero; point axes may be cropped only with explicit ticks. No gradients, 3D, invented observations, extra datasets, significance stars, fitted curves, or dual axes. Export PDF and 240-dpi PNG.  Exact method labels are Initial model, Plain, SPECTRUM where present. Caption: Five MBPP self-distillation rounds, 500 tasks and 16 samples per task. Native-student point estimates; paired D4 changes are relative to initialization on common eligible tasks, with archived pointwise 95% task-bootstrap intervals. One training seed. AST classes are structural proxies. Alt text: Accuracy rises as correct AST richness falls. SPECTRUM retains more richness and more dispersed correct outputs than Plain. Boundary: Independent training seeds and intermediate 64-sample pools; no global semantic diversity measurement. Preserve values, comparison sets, sample budgets, uncertainty meaning, eligibility, and selection rules; never turn unavailable evidence into plotted facts.
```

**Caption:** Five MBPP self-distillation rounds, 500 tasks and 16 samples per task. Native-student point estimates; paired D4 changes are relative to initialization on common eligible tasks, with archived pointwise 95% task-bootstrap intervals. One training seed. AST classes are structural proxies.

**Alt text:** Accuracy rises as correct AST richness falls. SPECTRUM retains more richness and more dispersed correct outputs than Plain.

## F. Fidelity and QA

- Exactly three designs encode the same facts; layout changes do not change evidence.
- Quantitative marks come from saved measurements or explicitly defined calculations.
- One dominant scientific panel owns at least half the usable canvas.
- Preserve single-seed scope, pairing, eligibility, and missing information.
- Check legibility, clipping, arrow/text collisions, units, and grayscale reproduction at final paper width.
