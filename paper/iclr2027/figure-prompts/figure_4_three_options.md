# Figure 4 — Can actual samples have equal estimated pass curves but unequal correct AST counts?

## A. Evidence Inventory

**Question:** Can actual samples have equal estimated pass curves but unequal correct AST counts?

**Supported answer:** The saved HumanEval/3 example is broader under SPECTRUM, while HumanEval/2 shows the reverse at the same number of correct samples.

**Fact lock:** MEASURED: 16 samples per method at round five. HumanEval/3: 16 correct under both; Plain AST counts [16], SPECTRUM [15,1]. HumanEval/2: 12 correct under both; Plain counts [1,1,1,1,1,1,1,1,1,1,1,1], SPECTRUM [2,1,1,1,1,1,1,1,1,1,1]. DERIVED: D4 on HumanEval/3 is 1 versus 1.25; on HumanEval/2 it is 4 versus 3.909091. Formula D_b=sum_j[1-comb(m-m_j,b)/comb(m,b)]. Classes are ranked separately, with no cross-model identity matching. Selection: for each sign of SPECTRUM-minus-Plain AST-count difference, choose lowest numerical HumanEval ID among tasks with equal correct counts >=4. Selection is sign-conditioned; no prevalence claim.

**Missing/boundary:** Program text was removed from the compact archive; do not invent code, algorithm names, prompt text, or semantic labels.

**Design skill:** `designing-experiment-figures`. **Production:** `programmatic-figure-spec`.

## B. Three candidate designs

| Option | Reading path | Main risk |
|---|---|---|
| 1 | Two frequency-rank panels | Misreading local/conditional evidence as a global guarantee. |
| 2 | Sample occupancy blocks | Misreading local/conditional evidence as a global guarantee. |
| 3 | Conditional rarefaction with observed-count evidence | Misreading local/conditional evidence as a global guarantee. |

**Recommendation:** Option 1, used in the supplied manuscript, gives the principal relationship the largest area and matches the available evidence.

## C. Option 1 — Two frequency-rank panels

**Rationale:** Canvas 6.65 by 2.35 inches. Allocate 58% to HumanEval/3 and 42% to HumanEval/2. In each panel, plot zero-baseline paired bars of counts against within-model frequency rank, with Plain gray and SPECTRUM black. Fill absent ranks with zero only for layout. Print Both: 16/16 correct or Both: 12/16 correct. Use y ranges 0--18 and 0--3 respectively and label them; different scales must be obvious.

### Standalone English production prompt (2571 characters)

```text
Create Figure 4 for an anonymous ICLR paper using programmatic-figure-spec. The immediate takeaway is: The saved HumanEval/3 example is broader under SPECTRUM, while HumanEval/2 shows the reverse at the same number of correct samples. Canvas 6.65 by 2.35 inches. Allocate 58% to HumanEval/3 and 42% to HumanEval/2. In each panel, plot zero-baseline paired bars of counts against within-model frequency rank, with Plain gray and SPECTRUM black. Fill absent ranks with zero only for layout. Print Both: 16/16 correct or Both: 12/16 correct. Use y ranges 0--18 and 0--3 respectively and label them; different scales must be obvious. Locked facts: MEASURED: 16 samples per method at round five. HumanEval/3: 16 correct under both; Plain AST counts [16], SPECTRUM [15,1]. HumanEval/2: 12 correct under both; Plain counts [1,1,1,1,1,1,1,1,1,1,1,1], SPECTRUM [2,1,1,1,1,1,1,1,1,1,1]. DERIVED: D4 on HumanEval/3 is 1 versus 1.25; on HumanEval/2 it is 4 versus 3.909091. Formula D_b=sum_j[1-comb(m-m_j,b)/comb(m,b)]. Classes are ranked separately, with no cross-model identity matching. Selection: for each sign of SPECTRUM-minus-Plain AST-count difference, choose lowest numerical HumanEval ID among tasks with equal correct counts >=4. Selection is sign-conditioned; no prevalence claim. Use vector plotting/code, white background, black SPECTRUM circles/solid lines, gray Plain squares/dashed lines, and light-gray Initial-model diamonds/dotted lines. At 6.65-inch paper width, retain readable horizontal type (8 pt labels), thin rules, and no colored fills. Bars start at zero; point axes may be cropped only with explicit ticks. No gradients, 3D, invented observations, extra datasets, significance stars, fitted curves, or dual axes. Export PDF and 240-dpi PNG.  Exact method labels are Initial model, Plain, SPECTRUM where present. Caption: Actual saved equal-correct-count examples, selected by the same lowest-ID rule for each sign. Frequency ranks are within-model, not aligned semantic classes. Both positive and negative examples are shown. These sample-level equalities do not establish equality of true success probabilities. Alt text: HumanEval/3 shows counts 16 versus 15+1 at equal success; HumanEval/2 shows fewer structures for SPECTRUM despite the same 12 correct outputs. Boundary: Program text was removed from the compact archive; do not invent code, algorithm names, prompt text, or semantic labels. Preserve values, comparison sets, sample budgets, uncertainty meaning, eligibility, and selection rules; never turn unavailable evidence into plotted facts.
```

**Caption:** Actual saved equal-correct-count examples, selected by the same lowest-ID rule for each sign. Frequency ranks are within-model, not aligned semantic classes. Both positive and negative examples are shown. These sample-level equalities do not establish equality of true success probabilities.

**Alt text:** HumanEval/3 shows counts 16 versus 15+1 at equal success; HumanEval/2 shows fewer structures for SPECTRUM despite the same 12 correct outputs.

## D. Option 2 — Sample occupancy blocks

**Rationale:** Canvas 6.65 by 2.8 inches. Use an upper 55% HumanEval/3 panel with two method lanes of 16 correct-sample tiles, grouped by AST frequency class. In the lower 45% show the 12 correct tiles for HumanEval/2 and a separate four-failed-draw block for each method. Assign local class labels j1,j2,... within each model, never aligned semantic labels. Print class counts and exact D4 beside lanes. Group borders and text distinguish classes without relying on color.

### Standalone English production prompt (2635 characters)

```text
Create Figure 4 for an anonymous ICLR paper using programmatic-figure-spec. The immediate takeaway is: The saved HumanEval/3 example is broader under SPECTRUM, while HumanEval/2 shows the reverse at the same number of correct samples. Canvas 6.65 by 2.8 inches. Use an upper 55% HumanEval/3 panel with two method lanes of 16 correct-sample tiles, grouped by AST frequency class. In the lower 45% show the 12 correct tiles for HumanEval/2 and a separate four-failed-draw block for each method. Assign local class labels j1,j2,... within each model, never aligned semantic labels. Print class counts and exact D4 beside lanes. Group borders and text distinguish classes without relying on color. Locked facts: MEASURED: 16 samples per method at round five. HumanEval/3: 16 correct under both; Plain AST counts [16], SPECTRUM [15,1]. HumanEval/2: 12 correct under both; Plain counts [1,1,1,1,1,1,1,1,1,1,1,1], SPECTRUM [2,1,1,1,1,1,1,1,1,1,1]. DERIVED: D4 on HumanEval/3 is 1 versus 1.25; on HumanEval/2 it is 4 versus 3.909091. Formula D_b=sum_j[1-comb(m-m_j,b)/comb(m,b)]. Classes are ranked separately, with no cross-model identity matching. Selection: for each sign of SPECTRUM-minus-Plain AST-count difference, choose lowest numerical HumanEval ID among tasks with equal correct counts >=4. Selection is sign-conditioned; no prevalence claim. Use vector plotting/code, white background, black SPECTRUM circles/solid lines, gray Plain squares/dashed lines, and light-gray Initial-model diamonds/dotted lines. At 6.65-inch paper width, retain readable horizontal type (8 pt labels), thin rules, and no colored fills. Bars start at zero; point axes may be cropped only with explicit ticks. No gradients, 3D, invented observations, extra datasets, significance stars, fitted curves, or dual axes. Export PDF and 240-dpi PNG.  Exact method labels are Initial model, Plain, SPECTRUM where present. Caption: Actual saved equal-correct-count examples, selected by the same lowest-ID rule for each sign. Frequency ranks are within-model, not aligned semantic classes. Both positive and negative examples are shown. These sample-level equalities do not establish equality of true success probabilities. Alt text: HumanEval/3 shows counts 16 versus 15+1 at equal success; HumanEval/2 shows fewer structures for SPECTRUM despite the same 12 correct outputs. Boundary: Program text was removed from the compact archive; do not invent code, algorithm names, prompt text, or semantic labels. Preserve values, comparison sets, sample budgets, uncertainty meaning, eligibility, and selection rules; never turn unavailable evidence into plotted facts.
```

**Caption:** Actual saved equal-correct-count examples, selected by the same lowest-ID rule for each sign. Frequency ranks are within-model, not aligned semantic classes. Both positive and negative examples are shown. These sample-level equalities do not establish equality of true success probabilities.

**Alt text:** HumanEval/3 shows counts 16 versus 15+1 at equal success; HumanEval/2 shows fewer structures for SPECTRUM despite the same 12 correct outputs.

## E. Option 3 — Conditional rarefaction with observed-count evidence

**Rationale:** Canvas 6.65 by 2.8 inches. Use 55% for two clearly separated per-task D_b curves for integer b=1,2,3,4 computed exactly from the supplied class counts. Put the measured class-count vectors in a 45% adjacent table with correct counts and task IDs. All curves are DERIVED rarefaction of the existing samples, not new model runs. Mark the opposite signs at b=4 without generalizing their frequency.

### Standalone English production prompt (2572 characters)

```text
Create Figure 4 for an anonymous ICLR paper using programmatic-figure-spec. The immediate takeaway is: The saved HumanEval/3 example is broader under SPECTRUM, while HumanEval/2 shows the reverse at the same number of correct samples. Canvas 6.65 by 2.8 inches. Use 55% for two clearly separated per-task D_b curves for integer b=1,2,3,4 computed exactly from the supplied class counts. Put the measured class-count vectors in a 45% adjacent table with correct counts and task IDs. All curves are DERIVED rarefaction of the existing samples, not new model runs. Mark the opposite signs at b=4 without generalizing their frequency. Locked facts: MEASURED: 16 samples per method at round five. HumanEval/3: 16 correct under both; Plain AST counts [16], SPECTRUM [15,1]. HumanEval/2: 12 correct under both; Plain counts [1,1,1,1,1,1,1,1,1,1,1,1], SPECTRUM [2,1,1,1,1,1,1,1,1,1,1]. DERIVED: D4 on HumanEval/3 is 1 versus 1.25; on HumanEval/2 it is 4 versus 3.909091. Formula D_b=sum_j[1-comb(m-m_j,b)/comb(m,b)]. Classes are ranked separately, with no cross-model identity matching. Selection: for each sign of SPECTRUM-minus-Plain AST-count difference, choose lowest numerical HumanEval ID among tasks with equal correct counts >=4. Selection is sign-conditioned; no prevalence claim. Use vector plotting/code, white background, black SPECTRUM circles/solid lines, gray Plain squares/dashed lines, and light-gray Initial-model diamonds/dotted lines. At 6.65-inch paper width, retain readable horizontal type (8 pt labels), thin rules, and no colored fills. Bars start at zero; point axes may be cropped only with explicit ticks. No gradients, 3D, invented observations, extra datasets, significance stars, fitted curves, or dual axes. Export PDF and 240-dpi PNG.  Exact method labels are Initial model, Plain, SPECTRUM where present. Caption: Actual saved equal-correct-count examples, selected by the same lowest-ID rule for each sign. Frequency ranks are within-model, not aligned semantic classes. Both positive and negative examples are shown. These sample-level equalities do not establish equality of true success probabilities. Alt text: HumanEval/3 shows counts 16 versus 15+1 at equal success; HumanEval/2 shows fewer structures for SPECTRUM despite the same 12 correct outputs. Boundary: Program text was removed from the compact archive; do not invent code, algorithm names, prompt text, or semantic labels. Preserve values, comparison sets, sample budgets, uncertainty meaning, eligibility, and selection rules; never turn unavailable evidence into plotted facts.
```

**Caption:** Actual saved equal-correct-count examples, selected by the same lowest-ID rule for each sign. Frequency ranks are within-model, not aligned semantic classes. Both positive and negative examples are shown. These sample-level equalities do not establish equality of true success probabilities.

**Alt text:** HumanEval/3 shows counts 16 versus 15+1 at equal success; HumanEval/2 shows fewer structures for SPECTRUM despite the same 12 correct outputs.

## F. Fidelity and QA

- Exactly three designs encode the same facts; layout changes do not change evidence.
- Quantitative marks come from saved measurements or explicitly defined calculations.
- One dominant scientific panel owns at least half the usable canvas.
- Preserve single-seed scope, pairing, eligibility, and missing information.
- Check legibility, clipping, arrow/text collisions, units, and grayscale reproduction at final paper width.
