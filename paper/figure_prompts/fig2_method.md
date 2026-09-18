# SPECTRUM — Figure 2: Pipeline Figure Design

## A. Scientific Ground Truth

### Three-second claim
SPECTRUM changes the generator temporarily using a soft transform derived from reference-loss gradients, then trains from the restored native checkpoint and evaluates a native merged model.

### Confirmed components and order
`CONFIRMED`: start round t from native checkpoint θ_t. Compute completion-masked reference cross-entropy. At native key/value projection outputs, collect g_{iu} gradients over all nonpadding token positions and form the uncentered gradient second moment C=(1/M)Σ_{i,u} g_{iu}g_{iu}ᵀ, where i indexes examples, u indexes included nonpadding positions, and M counts these example–position pairs. Normalize C̄=C/λ_max(C), construct T=[I+τ(I−C̄)]⁻¹ with τ=1, temporarily fold W′=TᵀW and b′=Tᵀb, generate one raw completion per training prompt, restore θ_t, train ordinary LoRA with all raw outputs and all-token loss, merge updates into native θ_{t+1}, then recompute C and T for the next round.

### Confirmed loops, branches, and training signals
`CONFIRMED`: a saved native-state branch initializes LoRA after restoration; generated raw completions provide the training data. The temporary transform is not the student initialization. The outer loop returns θ_{t+1} to the exact native-checkpoint input used for the next calibration. Native evaluation branches from the merged native checkpoint, with no spectral transform. Reference calibration uses completion-masked CE, while LoRA uses all-token loss; these two loss masks are not interchangeable. There is no prompt ensemble, output filtering, deployed inference adapter, or persistent hook. Ordinary LoRA is an optimization step and is merged.

### Exact notation and labels
θ_t, θ_{t+1}, g_{iu}, C, C̄, λ_max(C), T, τ=1, W′=TᵀW, b′=Tᵀb. Shortened labels: “Native K/V output gradients” means gradients at native key/value projection outputs; “Restore native” means restoration of the round's original checkpoint before LoRA; “Native evaluation” means evaluation of the merged native checkpoint.

### Unresolved items
`TO CONFIRM`: layer/module enumeration, second-moment storage precision, calibration/train set sizes, zero-second-moment fallback implementation, optimizer schedule. They are unnecessary for the high-level diagram and must not be invented. `ILLUSTRATIVE`: matrices, token strips, or eigenvalue glyphs used without observed values; never present them as measured spectra. No eigenvector is labeled as an algorithm and no weight SVD is substituted for gradient second moment.

## B. Three Candidate Visualizations

| Option | Topology | Visual center | Best at showing | Main risk |
|---|---|---|---|---|
| 1 | Dual-lane feedback loop | Soft-transform card between calibration and temporary generation | Native restoration and distinct data/state paths | Loop arrows can crowd the lower lane |
| 2 | Ordered stage triptych | Expanded transform inside generation stage | Three scientific phases: calibrate, generate, learn | A single chain could imply transformed student initialization |
| 3 | Checkpoint lifecycle with two branches | Native checkpoint spine | Temporary generator is separate from persistent checkpoint and evaluation | Branch geometry can resemble an ensemble |

**Recommendation:** Option 1 is the embedded figure: its separate state and raw-data paths make restoration and recurrence explicit with one dominant backbone.

## C. Option 1 — Dual-lane feedback loop

### Design rationale
Place calibration and generation above native learning, centered on the soft transform. Emphasize the saved native state and raw completion paths; compress module-level implementation.

### Standalone generation prompt
Draw Figure 2 as a precise, publication-ready vector diagram for an ICLR paper on white, about 7 × 2.72 inches. The three-second claim is that SPECTRUM uses a temporary gradient second-moment transform only to generate training data, then learns and evaluates in native coordinates. Title it “SPECTRUM: spectral control during data generation, then native learning”. Use an upper generation/calibration lane and a lower training/evaluation lane with a single return loop. In the upper lane read left to right: a small “Native” checkpoint card labeled θ_t; a “Reference calibration” card containing “Native K/V output gradients” and C=(1/M)Σ_{i,u} g_{iu}g_{iu}ᵀ; a larger central teal “Soft spectral transform” card containing C̄=C/λ_max(C), T=[I+τ(I−C̄)]⁻¹, τ=1; then a “Temporarily fold; generate” card containing W′=TᵀW, b′=Tᵀb and “1 raw completion / training prompt”. Under calibration print “Completion-masked reference CE; all nonpadding token positions in C”. Under the top lane put “Restore native”, labeled “θ_t before LoRA”; “Ordinary LoRA”, labeled “All raw outputs; all-token loss”; “Merge updates”, labeled “Native θ_{t+1}”; then a smaller white “Native evaluation” card, labeled “No spectral transform”. A solid saved-state arrow branches from θ_t directly to Restore native, then proceeds to LoRA and merge. A separate teal arrow labeled “raw completions” descends from generation into LoRA, never into the restored checkpoint. A restrained outer return loop goes from native θ_{t+1} precisely back to the θ_t input card, with text “Next round: recompute C and T from the merged native checkpoint”. Draw the evaluation branch as a dashed gray arrow from θ_{t+1}, distinct from solid training transitions; explain this style in the caption. Use teal only for the temporary spectral intervention and its data, charcoal for native state, pale gray stage fills, thin borders, gentle corners, no shadows. Minimum horizontal text is 7 points at final width; use 9.5-point title, 8-point headers, 8-point equations where possible. Required text is all quoted labels and equations above plus “GENERATION / CALIBRATION”, “TRAINING”, “EVALUATION”, and “saved state”. Do not draw weight SVD, persistent hooks, prompt ensembles, output filters, correctness selection, a deployed LoRA adapter, or an arrow from transformed generator weights into the student. Do not label eigenvectors as algorithms, fabricate spectra or performance numbers, add decorative neural-network icons, duplicate modules, or use tangled connectors. Preserve the exact confirmed order, saved-state branch, raw-completion branch, feedback destination, and training-versus-evaluation distinction.

### Caption draft
At each round SPECTRUM estimates gradient second moment at native K/V outputs under completion-masked reference CE, pooling all nonpadding token positions. A soft spectral transform is temporarily folded into projection weights to generate one raw completion per training prompt. The round's native checkpoint is restored before ordinary LoRA on all raw outputs with all-token loss; merged updates produce the next native checkpoint. The outer loop recomputes calibration each round. The dashed branch denotes native evaluation with no spectral transform; the saved-state arrow identifies the actual student initialization.

## D. Option 2 — Calibrate / Generate / Learn triptych

### Design rationale
Use three ordered stages with different internal structures: gradient aggregation, temporary weight transformation, and a restoration-plus-learning merge. Emphasize phases; compress the outer loop into a precise bottom connector.

### Standalone generation prompt
Create a full-width ICLR vector pipeline figure, 7 × 2.8 inches, white background, titled “SPECTRUM: calibrate, generate, restore and learn”. The complete narrative is temporary spectral shaping of synthetic data followed by native learning. Divide the canvas into three numbered semantic regions: “1 Reference calibration” occupying 28%, “2 Temporary generation” occupying 36%, and “3 Native learning” occupying 36%. Region 1 starts with concrete native state θ_t and abstract reference examples; labels specify “Completion-masked reference CE”, “Native K/V output gradients”, and “All nonpadding positions”. Aggregate g_{iu} into a small labeled second-moment matrix C=(1/M)Σ_{i,u} g_{iu}g_{iu}ᵀ; any unnumbered matrix squares are illustrative, not measurements. Region 2 contains the visual center, a teal formula block C̄=C/λ_max(C), T=[I+τ(I−C̄)]⁻¹, τ=1, followed by W′=TᵀW, b′=Tᵀb and a raw-output document labeled “1 raw completion / training prompt”. Region 3 begins with a visible state merge: a thin lower saved-state rail from θ_t reaches “Restore θ_t before LoRA”, while the generated document reaches “Ordinary LoRA” through a separate input arrow. Label LoRA “All raw outputs; all-token loss”, then “Merge → native θ_{t+1}”. Put a narrow “Native evaluation: no spectral transform” branch beside θ_{t+1}, using dashed gray arrows. A single thin loop from θ_{t+1} lands exactly on the initial θ_t card and is labeled “Recompute C and T each round”. The main path is left-to-right; the saved-state rail must never touch transformed W′, and generation data must never be shown as filtered. Use teal for the transform and its raw-data arrow, gray for native states, charcoal text, 8-point horizontal type and 10-point title, thin borders, no shadow, and at least 0.08-inch gutters. Required text is every quoted phrase and every equation in this prompt. Use a dashed line only for the evaluation branch, not to imply an imagined model. Do not add a fourth algorithmic stage, weight SVD, a prompt ensemble, hooks, correctness filtering, inference adapters, invented second-moment values, or semantic-algorithm labels. Preserve the confirmed three-stage order, native restoration branch, raw-data training input, precise checkpoint feedback, and distinction between calibration masking and LoRA loss.

### Caption draft
Three phases of a SPECTRUM round: reference gradients define a full-rank soft transform; temporarily folded weights generate raw completions; the restored native checkpoint is updated by ordinary LoRA and merged. The saved-state rail makes restoration explicit. Evaluation uses the native merged model, and the next round recomputes calibration from that model. Matrix glyphs, if included, are illustrative.

## E. Option 3 — Native checkpoint lifecycle with a temporary branch

### Design rationale
Organize around the persistent object, the native checkpoint. Place the temporary generator on a side branch and training on the continuing spine. Emphasize the difference between temporary and lasting state; compress chronological stage boundaries.

### Standalone generation prompt
Design alternate Figure 2 as a vector ICLR diagram, 7 × 3.0 inches, on white, with a dominant vertical native-checkpoint spine in the left-middle and a single large temporary-generation branch to its right. Title “SPECTRUM: a temporary generator, a native checkpoint”. The spine reads downward θ_t → “Restore θ_t” → “Ordinary LoRA” → “Merge: native θ_{t+1}”; its solid gray state arrows show that transformed weights do not initialize LoRA. On the right, branch once from θ_t into “Reference calibration”: “Completion-masked reference CE”, “Native K/V output gradients”, “All nonpadding token positions”, C=(1/M)Σ_{i,u} g_{iu}g_{iu}ᵀ. Below that, put the largest teal center card “Soft spectral transform”, with C̄=C/λ_max(C), T=[I+τ(I−C̄)]⁻¹, τ=1. Continue downward to “Temporarily fold” with W′=TᵀW and b′=Tᵀb, then “Generate: 1 raw completion / training prompt”. One solid teal arrow labeled “All raw outputs” leaves this branch and joins only the LoRA box on the native spine; label its loss “All-token loss”. The generator branch terminates there: it is a temporary state, not a second persistent model or an ensemble. From θ_{t+1}, send a dashed gray branch left to “Native evaluation” and “No spectral transform”; send one outer return arrow to the initial θ_t card, labeled “Next round: recompute C and T”. Use native-state rectangles with gray borders, a pale teal temporary-region container, teal intervention formulas and data arrows, charcoal text, 8-point minimum horizontal labels, 10-point title, and generous whitespace around joins. Required text comprises the exact title, checkpoint symbols, formulas, and every quoted module or arrow label. Explicitly prohibit imaginary output filtering, prompt ensembles, correctness gates, a transformed student initializer, a persistent adapter at evaluation, weight SVD, semantic algorithm eigenvectors, invented numerical spectra, decorative brains, and crossing arrows. Preserve the exact scientific dependency graph, precise checkpoint recurrence, raw-output flow, restored native training state, and separate native evaluation branch.

### Caption draft
The native checkpoint persists through a SPECTRUM round, while reference calibration and temporarily transformed generation form a data-producing side branch. All generated outputs train ordinary LoRA only after restoration of the round's native checkpoint. Merged updates yield θ_{t+1} for evaluation and the next calibration round. The dashed branch is evaluation, not another training or inference adapter.

## F. Cross-option fidelity checklist

- Exactly three distinct macro-compositions preserve one identical method.
- The uncentered second moment is from native K/V output gradients, never a weight SVD.
- All nonpadding calibration positions and the completion-masked reference loss are both explicit.
- T=[I+τ(I−C̄)]⁻¹, τ=1, and both weight and bias folds remain exact.
- The restored round checkpoint initializes LoRA; all raw outputs and all-token loss are retained.
- No correctness filter, prompt ensemble, deployed adapter, hook, or algorithm/eigenvector equivalence is introduced.
- The loop returns to the native checkpoint used for calibration; evaluation has no transform.
- No example glyph can be mistaken for measured data; no unnecessary unresolved implementation is invented.
