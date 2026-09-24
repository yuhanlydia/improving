# Figure 2 — How does fixed calibration information change each round without selecting generated samples?

## A. Scientific Ground Truth

**Question:** How does fixed calibration information change each round without selecting generated samples?

**Supported answer:** The anchor is fixed; K/V geometry is re-estimated on the evolving model, then temporarily folded for generation and removed before single-LoRA SFT.

**Fact lock:** CONFIRMED: native student theta_t; fixed reference anchor A={(x_i,y_i*)}; reference-completion mean NLL with prompt targets masked; all nonpadding K/V-output gradients; normalized second moment Cbar_t=C_t/lambda_max(C_t); T_t=[I+tau(I-Cbar_t)]^{-1}; temporary pre-RoPE K/V weight folding; all raw synthetic records D_t; restore native theta_t; one LoRA SFT on all nonpadding causal targets; merge theta_(t+1); recompute geometry next round; native final inference. Reference data are reused external supervision. No newly labeled anchor data, rollout grading, strategy assignment, sample rejection, adapter pool, or reward update.

**Missing/boundary:** No unresolved pipeline component is drawn. No semantic-diversity guarantee follows from local full rank.

**Design skill:** `designing-pipeline-figures`. **Production:** `vector-diagram-spec`.

## B. Three candidate designs

| Option | Reading path | Main risk |
|---|---|---|
| 1 | Two-lane learning loop | Misreading local/conditional evidence as a global guarantee. |
| 2 | Circular recurrence around the fixed anchor | Misreading local/conditional evidence as a global guarantee. |
| 3 | One transition expanded between successive students | Misreading local/conditional evidence as a global guarantee. |

**Recommendation:** Option 1, used in the supplied manuscript, gives the principal relationship the largest area and matches the available evidence.

## C. Option 1 — Two-lane learning loop

**Rationale:** Canvas 6.65 by 2.9 inches. Top lane: Fixed reference anchor -> Re-estimate K/V geometry -> Proximal spectral gain. Bottom lane: Current student theta_t -> Temporary K/V folding / Generate all raw samples -> Restore native weights / Single-LoRA SFT -> theta_(t+1). Draw a dashed current-student input to geometry, a solid gain input to temporary generation, and one bottom return arrow from theta_(t+1) to current student. The loop occupies 75% of usable area. Label the reference edge Reused each round and the data edge D_t. Do not let an arrow cross text.

### Standalone English production prompt (2683 characters)

```text
Create Figure 2 for an anonymous ICLR paper using vector-diagram-spec. The immediate takeaway is: The anchor is fixed; K/V geometry is re-estimated on the evolving model, then temporarily folded for generation and removed before single-LoRA SFT. Canvas 6.65 by 2.9 inches. Top lane: Fixed reference anchor -> Re-estimate K/V geometry -> Proximal spectral gain. Bottom lane: Current student theta_t -> Temporary K/V folding / Generate all raw samples -> Restore native weights / Single-LoRA SFT -> theta_(t+1). Draw a dashed current-student input to geometry, a solid gain input to temporary generation, and one bottom return arrow from theta_(t+1) to current student. The loop occupies 75% of usable area. Label the reference edge Reused each round and the data edge D_t. Do not let an arrow cross text. Locked facts: CONFIRMED: native student theta_t; fixed reference anchor A={(x_i,y_i*)}; reference-completion mean NLL with prompt targets masked; all nonpadding K/V-output gradients; normalized second moment Cbar_t=C_t/lambda_max(C_t); T_t=[I+tau(I-Cbar_t)]^{-1}; temporary pre-RoPE K/V weight folding; all raw synthetic records D_t; restore native theta_t; one LoRA SFT on all nonpadding causal targets; merge theta_(t+1); recompute geometry next round; native final inference. Reference data are reused external supervision. No newly labeled anchor data, rollout grading, strategy assignment, sample rejection, adapter pool, or reward update. Use an editable vector diagram, white background, black text, thin gray borders, and light-gray fills only for persistent information and the temporary generation module. Minimum label size 8 pt at paper width. Keep all text horizontal and connectors clear. Export PDF and PNG. Prohibit reward models, verification gates, strategy labels, model ensembles, adapter pools, extra losses, numerical result claims, or semantic guarantees not specified here.  Exact method labels are Initial model, Plain, SPECTRUM where present. Caption: SPECTRUM within Looped Self-Distillation. The fixed reference anchor calibrates changing native-student geometry; a temporary proximal K/V transform produces raw training data. Restoring weights and merging one LoRA yields the next student. Final inference uses no transform. Alt text: A fixed anchor guides per-round geometry; the model generates all raw samples, learns through one LoRA, and returns as the next native student. Boundary: No unresolved pipeline component is drawn. No semantic-diversity guarantee follows from local full rank. Preserve values, comparison sets, sample budgets, uncertainty meaning, eligibility, and selection rules; never turn unavailable evidence into plotted facts.
```

**Caption:** SPECTRUM within Looped Self-Distillation. The fixed reference anchor calibrates changing native-student geometry; a temporary proximal K/V transform produces raw training data. Restoring weights and merging one LoRA yields the next student. Final inference uses no transform.

**Alt text:** A fixed anchor guides per-round geometry; the model generates all raw samples, learns through one LoRA, and returns as the next native student.

## D. Option 2 — Circular recurrence around the fixed anchor

**Rationale:** Canvas 6.65 by 3.3 inches. Put the persistent anchor in a small central outlined box (20% of area), and a clockwise ring occupying 80%: Current student -> Geometry -> Gain -> Raw generation -> Restore + single-LoRA SFT -> Next student. A radial dashed line from anchor ends at geometry only. Mark the return state theta_(t+1) to theta_t for the next round. Put the gain equation beside the gain node, not across connectors. No arrows from evaluation to the learning loop.

### Standalone English production prompt (2597 characters)

```text
Create Figure 2 for an anonymous ICLR paper using vector-diagram-spec. The immediate takeaway is: The anchor is fixed; K/V geometry is re-estimated on the evolving model, then temporarily folded for generation and removed before single-LoRA SFT. Canvas 6.65 by 3.3 inches. Put the persistent anchor in a small central outlined box (20% of area), and a clockwise ring occupying 80%: Current student -> Geometry -> Gain -> Raw generation -> Restore + single-LoRA SFT -> Next student. A radial dashed line from anchor ends at geometry only. Mark the return state theta_(t+1) to theta_t for the next round. Put the gain equation beside the gain node, not across connectors. No arrows from evaluation to the learning loop. Locked facts: CONFIRMED: native student theta_t; fixed reference anchor A={(x_i,y_i*)}; reference-completion mean NLL with prompt targets masked; all nonpadding K/V-output gradients; normalized second moment Cbar_t=C_t/lambda_max(C_t); T_t=[I+tau(I-Cbar_t)]^{-1}; temporary pre-RoPE K/V weight folding; all raw synthetic records D_t; restore native theta_t; one LoRA SFT on all nonpadding causal targets; merge theta_(t+1); recompute geometry next round; native final inference. Reference data are reused external supervision. No newly labeled anchor data, rollout grading, strategy assignment, sample rejection, adapter pool, or reward update. Use an editable vector diagram, white background, black text, thin gray borders, and light-gray fills only for persistent information and the temporary generation module. Minimum label size 8 pt at paper width. Keep all text horizontal and connectors clear. Export PDF and PNG. Prohibit reward models, verification gates, strategy labels, model ensembles, adapter pools, extra losses, numerical result claims, or semantic guarantees not specified here.  Exact method labels are Initial model, Plain, SPECTRUM where present. Caption: SPECTRUM within Looped Self-Distillation. The fixed reference anchor calibrates changing native-student geometry; a temporary proximal K/V transform produces raw training data. Restoring weights and merging one LoRA yields the next student. Final inference uses no transform. Alt text: A fixed anchor guides per-round geometry; the model generates all raw samples, learns through one LoRA, and returns as the next native student. Boundary: No unresolved pipeline component is drawn. No semantic-diversity guarantee follows from local full rank. Preserve values, comparison sets, sample budgets, uncertainty meaning, eligibility, and selection rules; never turn unavailable evidence into plotted facts.
```

**Caption:** SPECTRUM within Looped Self-Distillation. The fixed reference anchor calibrates changing native-student geometry; a temporary proximal K/V transform produces raw training data. Restoring weights and merging one LoRA yields the next student. Final inference uses no transform.

**Alt text:** A fixed anchor guides per-round geometry; the model generates all raw samples, learns through one LoRA, and returns as the next native student.

## E. Option 3 — One transition expanded between successive students

**Rationale:** Canvas 6.65 by 3.0 inches. Place theta_t and theta_(t+1) at left and right; let their expanded middle transition occupy 65%. Above the transition, fixed anchor + current theta_t feed geometry then the exact proximal-gain equation. Beneath, temporary generator -> complete raw corpus D_t -> restored-weight single-LoRA learning. Draw a single outer feedback line from the right student to the left state labeled Repeat with same anchor. Put a separate small right-side label Native inference attached only to the new student.

### Standalone English production prompt (2650 characters)

```text
Create Figure 2 for an anonymous ICLR paper using vector-diagram-spec. The immediate takeaway is: The anchor is fixed; K/V geometry is re-estimated on the evolving model, then temporarily folded for generation and removed before single-LoRA SFT. Canvas 6.65 by 3.0 inches. Place theta_t and theta_(t+1) at left and right; let their expanded middle transition occupy 65%. Above the transition, fixed anchor + current theta_t feed geometry then the exact proximal-gain equation. Beneath, temporary generator -> complete raw corpus D_t -> restored-weight single-LoRA learning. Draw a single outer feedback line from the right student to the left state labeled Repeat with same anchor. Put a separate small right-side label Native inference attached only to the new student. Locked facts: CONFIRMED: native student theta_t; fixed reference anchor A={(x_i,y_i*)}; reference-completion mean NLL with prompt targets masked; all nonpadding K/V-output gradients; normalized second moment Cbar_t=C_t/lambda_max(C_t); T_t=[I+tau(I-Cbar_t)]^{-1}; temporary pre-RoPE K/V weight folding; all raw synthetic records D_t; restore native theta_t; one LoRA SFT on all nonpadding causal targets; merge theta_(t+1); recompute geometry next round; native final inference. Reference data are reused external supervision. No newly labeled anchor data, rollout grading, strategy assignment, sample rejection, adapter pool, or reward update. Use an editable vector diagram, white background, black text, thin gray borders, and light-gray fills only for persistent information and the temporary generation module. Minimum label size 8 pt at paper width. Keep all text horizontal and connectors clear. Export PDF and PNG. Prohibit reward models, verification gates, strategy labels, model ensembles, adapter pools, extra losses, numerical result claims, or semantic guarantees not specified here.  Exact method labels are Initial model, Plain, SPECTRUM where present. Caption: SPECTRUM within Looped Self-Distillation. The fixed reference anchor calibrates changing native-student geometry; a temporary proximal K/V transform produces raw training data. Restoring weights and merging one LoRA yields the next student. Final inference uses no transform. Alt text: A fixed anchor guides per-round geometry; the model generates all raw samples, learns through one LoRA, and returns as the next native student. Boundary: No unresolved pipeline component is drawn. No semantic-diversity guarantee follows from local full rank. Preserve values, comparison sets, sample budgets, uncertainty meaning, eligibility, and selection rules; never turn unavailable evidence into plotted facts.
```

**Caption:** SPECTRUM within Looped Self-Distillation. The fixed reference anchor calibrates changing native-student geometry; a temporary proximal K/V transform produces raw training data. Restoring weights and merging one LoRA yields the next student. Final inference uses no transform.

**Alt text:** A fixed anchor guides per-round geometry; the model generates all raw samples, learns through one LoRA, and returns as the next native student.

## F. Fidelity and QA

- Exactly three designs encode the same facts; layout changes do not change evidence.
- Quantitative marks come from saved measurements or explicitly defined calculations.
- One dominant scientific panel owns at least half the usable canvas.
- Preserve single-seed scope, pairing, eligibility, and missing information.
- Check legibility, clipping, arrow/text collisions, units, and grayscale reproduction at final paper width.
