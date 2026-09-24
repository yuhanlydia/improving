#!/usr/bin/env python3
"""Write standalone English production prompts, three designs per figure."""
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
D=json.loads((HERE/'source-data/rewrite_sources.json').read_text())
A=json.loads((HERE/'source-data/derived_analysis.json').read_text())
OUT=HERE/'figure-prompts';OUT.mkdir(exist_ok=True)
def compact(v):
 if isinstance(v,float): return round(v,6)
 if isinstance(v,dict):return {k:compact(x) for k,x in v.items()}
 if isinstance(v,list):return [compact(x) for x in v]
 return v

def series(m):
 rows=[D['mbpp16']['base/evaluation']]+[D['mbpp16'][f'{m}/round_{r}/evaluation'] for r in range(1,6)]
 z={'pass1_percent':[r['pass_at_1']['mean']*100 for r in rows],
 'C16':[r['implementation_coverage_at_k']['16']['mean'] for r in rows],
 'Simpson':[r['implementation_simpson_diversity']['mean'] for r in rows]}
 c=[D['mbpp16_comparisons'][f'{m}/round_{r}/evaluation - base/evaluation']['implementation_proxy']['correct_matched_coverage'] for r in range(1,6)]
 z['paired_D4_change']=[r['mean'] for r in c];z['paired_D4_ci95']=[r['ci95'] for r in c];z['paired_D4_n']=[r['eligible_tasks'] for r in c]
 return z
f1=json.dumps(compact({m:series(m) for m in ['plain','spectral_soft']}),separators=(',',':'))
f3d={}
for m in ['base','plain','spectral_soft']:
 row=D['mbpp64'][m];f3d[m]={'Ck':[row['implementation_coverage_at_k'][str(k)]['mean'] for k in [1,4,8,16,64]],'passk_percent':[100*row['pass_at_k'][str(k)]['mean'] for k in [1,4,8,16,64]]}
pair=D['mbpp64_comparisons']['spectral_soft_minus_plain']['correct_matched_coverage_at_budgets']
f3d['paired_D']={b:{k:pair[b][k] for k in ['mean','ci95','eligible_tasks']} for b in ['4','8','16']}
f3=json.dumps(compact(f3d),separators=(',',':'))
style='Use vector plotting/code, white background, black SPECTRUM circles/solid lines, gray Plain squares/dashed lines, and light-gray Initial-model diamonds/dotted lines. At 6.65-inch paper width, retain readable horizontal type (8 pt labels), thin rules, and no colored fills. Bars start at zero; point axes may be cropped only with explicit ticks. No gradients, 3D, invented observations, extra datasets, significance stars, fitted curves, or dual axes. Export PDF and 240-dpi PNG. '
finish='Preserve values, comparison sets, sample budgets, uncertainty meaning, eligibility, and selection rules; never turn unavailable evidence into plotted facts.'
items={}
items[1]={
 'question':'Can increasing correctness conceal contraction within correct outputs?',
 'answer':'In the saved five-round MBPP run, Plain and SPECTRUM increase pass@1 while losing AST richness; SPECTRUM loses less.',
 'type':'programmatic-figure-spec','skill':'designing-experiment-figures',
 'facts':f1,
 'missing':'Independent training seeds and intermediate 64-sample pools; no global semantic diversity measurement.',
 'caption':'Five MBPP self-distillation rounds, 500 tasks and 16 samples per task. Native-student point estimates; paired D4 changes are relative to initialization on common eligible tasks, with archived pointwise 95% task-bootstrap intervals. One training seed. AST classes are structural proxies.',
 'alt':'Accuracy rises as correct AST richness falls. SPECTRUM retains more richness and more dispersed correct outputs than Plain.',
 'layouts':[
 ('Phase trajectory with conditional checks','Place pass@1 (%) on x and C16 on y in the left 58% panel. Connect rounds 0 through 5 in order and label their numbers. Put paired D4 change from initialization versus rounds 1--5, including CI bars, in the middle 21%; place Simpson diversity versus rounds 0--5 in the right 21%. A shared legend maps plain to Plain and spectral_soft to SPECTRUM. Label panels (a) Accuracy and breadth, (b) Equal correct draws, (c) Concentration. This prioritizes the accuracy/breadth separation.'),
 ('Longitudinal retention with aligned diagnostics','Use the left 55% for C16 against rounds 0--5. In the right 45%, stack three aligned strips for pass@1 (%), paired D4 changes with CI bars, and Simpson diversity. Each strip has its own labeled y-axis and shares round order. Show all initial and final values beside their respective points. This emphasizes accumulation across rounds; do not add a fitted decay rate.'),
 ('Conditional retention as the focal evidence','Use the upper 55% for paired D4 change from initialization against rounds 1--5 with exact CI bars and zero reference. Below it, use 30% for the measured pass@1-versus-C16 trajectories and 15% for Simpson-versus-round. Keep each plot independent; no linking axes with arrows implying causality. This emphasizes the within-correct result while retaining every source series.')]
}
items[2]={
 'question':'How does fixed calibration information change each round without selecting generated samples?',
 'answer':'The anchor is fixed; K/V geometry is re-estimated on the evolving model, then temporarily folded for generation and removed before single-LoRA SFT.',
 'type':'vector-diagram-spec','skill':'designing-pipeline-figures',
 'facts':'CONFIRMED: native student theta_t; fixed reference anchor A={(x_i,y_i*)}; reference-completion mean NLL with prompt targets masked; all nonpadding K/V-output gradients; normalized second moment Cbar_t=C_t/lambda_max(C_t); T_t=[I+tau(I-Cbar_t)]^{-1}; temporary pre-RoPE K/V weight folding; all raw synthetic records D_t; restore native theta_t; one LoRA SFT on all nonpadding causal targets; merge theta_(t+1); recompute geometry next round; native final inference. Reference data are reused external supervision. No newly labeled anchor data, rollout grading, strategy assignment, sample rejection, adapter pool, or reward update.',
 'missing':'No unresolved pipeline component is drawn. No semantic-diversity guarantee follows from local full rank.',
 'caption':'SPECTRUM within Looped Self-Distillation. The fixed reference anchor calibrates changing native-student geometry; a temporary proximal K/V transform produces raw training data. Restoring weights and merging one LoRA yields the next student. Final inference uses no transform.',
 'alt':'A fixed anchor guides per-round geometry; the model generates all raw samples, learns through one LoRA, and returns as the next native student.',
 'layouts':[
 ('Two-lane learning loop','Canvas 6.65 by 2.9 inches. Top lane: Fixed reference anchor -> Re-estimate K/V geometry -> Proximal spectral gain. Bottom lane: Current student theta_t -> Temporary K/V folding / Generate all raw samples -> Restore native weights / Single-LoRA SFT -> theta_(t+1). Draw a dashed current-student input to geometry, a solid gain input to temporary generation, and one bottom return arrow from theta_(t+1) to current student. The loop occupies 75% of usable area. Label the reference edge Reused each round and the data edge D_t. Do not let an arrow cross text.'),
 ('Circular recurrence around the fixed anchor','Canvas 6.65 by 3.3 inches. Put the persistent anchor in a small central outlined box (20% of area), and a clockwise ring occupying 80%: Current student -> Geometry -> Gain -> Raw generation -> Restore + single-LoRA SFT -> Next student. A radial dashed line from anchor ends at geometry only. Mark the return state theta_(t+1) to theta_t for the next round. Put the gain equation beside the gain node, not across connectors. No arrows from evaluation to the learning loop.'),
 ('One transition expanded between successive students','Canvas 6.65 by 3.0 inches. Place theta_t and theta_(t+1) at left and right; let their expanded middle transition occupy 65%. Above the transition, fixed anchor + current theta_t feed geometry then the exact proximal-gain equation. Beneath, temporary generator -> complete raw corpus D_t -> restored-weight single-LoRA learning. Draw a single outer feedback line from the right student to the left state labeled Repeat with same anchor. Put a separate small right-side label Native inference attached only to the new student.')]
}
items[3]={
 'question':'Does a broader learned distribution help at larger total and correct-sample budgets?',
 'answer':'SPECTRUM gains correct richness over Plain at displayed k>1 and retains positive paired richness gains at b=4,8,16; its pass@1 is lower.',
 'type':'programmatic-figure-spec','skill':'designing-experiment-figures','facts':f3,
 'missing':'No measured k=32 value or new generations; no seed uncertainty or scaling-law fit.',
 'caption':'The same final 64-sample pools on 500 MBPP tasks give Ck and pass@k for k=1,4,8,16,64. Paired SPECTRUM-minus-Plain Db contrasts use common eligible tasks at b=4,8,16 and archived 95% task-bootstrap intervals. One training seed.',
 'alt':'SPECTRUM yields more correct structures than Plain as total budget increases, with positive richness gains when correct-sample counts are matched.',
 'layouts':[
 ('Budget curves and matched-correct effects','Use a 6.65 by 2.5-inch canvas. Allocate 56% to Ck curves versus k; 23% to pass@k (%) versus k; 21% to paired Delta Db versus b with CI bars and a zero line. Total budgets are [1,4,8,16,64], with base-2 log x axes and explicit ticks. Correct budgets are [4,8,16] categorical. Label (a) Correct AST richness, (b) Task success, (c) Matched-correct gain. Use separate y scales and give the paired n values 316,296,254 in the caption.'),
 ('Exact-value budget matrix with an effect strip','Use a 6.65 by 3-inch canvas. In the left 60%, draw a native vector matrix with three method rows and five k columns, each cell displaying exact Ck values to three decimals and a zero-origin proportional horizontal mark. Label the raw budget columns 1,4,8,16,64. The right 40% contains pass@k curves above and paired Delta Db intervals below. Preserve the lower SPECTRUM k=1 entry; do not use winner coloring or turn the matrix into a significance heatmap.'),
 ('Paired-budget comparisons with a conditional footer','Use a 6.65 by 3.1-inch canvas. Top-left 55%: for each k, place three method points on the common Ck axis in separate budget rows, with a thin gray within-row connector only. Upper-right 25%: the same budget rows with pass@k (%) points on an independent axis. Bottom 20%: paired Delta Db and CI bars for b=4,8,16. This emphasizes the crossover at k=1 and the growing absolute richness contrast without asserting a fitted law.')]
}
items[4]={
 'question':'Can actual samples have equal estimated pass curves but unequal correct AST counts?',
 'answer':'The saved HumanEval/3 example is broader under SPECTRUM, while HumanEval/2 shows the reverse at the same number of correct samples.',
 'type':'programmatic-figure-spec','skill':'designing-experiment-figures',
 'facts':'MEASURED: 16 samples per method at round five. HumanEval/3: 16 correct under both; Plain AST counts [16], SPECTRUM [15,1]. HumanEval/2: 12 correct under both; Plain counts [1,1,1,1,1,1,1,1,1,1,1,1], SPECTRUM [2,1,1,1,1,1,1,1,1,1,1]. DERIVED: D4 on HumanEval/3 is 1 versus 1.25; on HumanEval/2 it is 4 versus 3.909091. Formula D_b=sum_j[1-comb(m-m_j,b)/comb(m,b)]. Classes are ranked separately, with no cross-model identity matching. Selection: for each sign of SPECTRUM-minus-Plain AST-count difference, choose lowest numerical HumanEval ID among tasks with equal correct counts >=4. Selection is sign-conditioned; no prevalence claim.',
 'missing':'Program text was removed from the compact archive; do not invent code, algorithm names, prompt text, or semantic labels.',
 'caption':'Actual saved equal-correct-count examples, selected by the same lowest-ID rule for each sign. Frequency ranks are within-model, not aligned semantic classes. Both positive and negative examples are shown. These sample-level equalities do not establish equality of true success probabilities.',
 'alt':'HumanEval/3 shows counts 16 versus 15+1 at equal success; HumanEval/2 shows fewer structures for SPECTRUM despite the same 12 correct outputs.',
 'layouts':[
 ('Two frequency-rank panels','Canvas 6.65 by 2.35 inches. Allocate 58% to HumanEval/3 and 42% to HumanEval/2. In each panel, plot zero-baseline paired bars of counts against within-model frequency rank, with Plain gray and SPECTRUM black. Fill absent ranks with zero only for layout. Print Both: 16/16 correct or Both: 12/16 correct. Use y ranges 0--18 and 0--3 respectively and label them; different scales must be obvious.'),
 ('Sample occupancy blocks','Canvas 6.65 by 2.8 inches. Use an upper 55% HumanEval/3 panel with two method lanes of 16 correct-sample tiles, grouped by AST frequency class. In the lower 45% show the 12 correct tiles for HumanEval/2 and a separate four-failed-draw block for each method. Assign local class labels j1,j2,... within each model, never aligned semantic labels. Print class counts and exact D4 beside lanes. Group borders and text distinguish classes without relying on color.'),
 ('Conditional rarefaction with observed-count evidence','Canvas 6.65 by 2.8 inches. Use 55% for two clearly separated per-task D_b curves for integer b=1,2,3,4 computed exactly from the supplied class counts. Put the measured class-count vectors in a 45% adjacent table with correct counts and task IDs. All curves are DERIVED rarefaction of the existing samples, not new model runs. Mark the opposite signs at b=4 without generalizing their frequency.')]
}
all_docs=[];manifest=[]
for num,item in items.items():
 is_pipeline=num==2
 facttitle='Scientific Ground Truth' if is_pipeline else 'Evidence Inventory'
 doc=f"# Figure {num} — {item['question']}\n\n## A. {facttitle}\n\n**Question:** {item['question']}\n\n**Supported answer:** {item['answer']}\n\n**Fact lock:** {item['facts']}\n\n**Missing/boundary:** {item['missing']}\n\n**Design skill:** `{item['skill']}`. **Production:** `{item['type']}`.\n\n## B. Three candidate designs\n\n| Option | Reading path | Main risk |\n|---|---|---|\n"
 for i,(title,layout) in enumerate(item['layouts'],1):doc+=f'| {i} | {title} | Misreading local/conditional evidence as a global guarantee. |\n'
 doc+='\n**Recommendation:** Option 1, used in the supplied manuscript, gives the principal relationship the largest area and matches the available evidence.\n'
 for i,(title,layout) in enumerate(item['layouts'],1):
  facts=item['facts']
  if num==1:
   facts='All arrays below are saved measurements (six round-0--5 entries, or five round-1--5 paired changes). '+facts+' Paired D4 intervals resample evaluation tasks 2,000 times; eligibility varies by contrast. Simpson uses tasks with at least two correct outputs. No uncertainty is plotted for phase or Simpson points.'
  if num==3:facts='Budget order k=[1,4,8,16,64]; paired correct budgets b=[4,8,16]. MEASURED arrays and archived intervals: '+facts
  visual=style if not is_pipeline else 'Use an editable vector diagram, white background, black text, thin gray borders, and light-gray fills only for persistent information and the temporary generation module. Minimum label size 8 pt at paper width. Keep all text horizontal and connectors clear. Export PDF and PNG. Prohibit reward models, verification gates, strategy labels, model ensembles, adapter pools, extra losses, numerical result claims, or semantic guarantees not specified here. '
  prompt=f"Create Figure {num} for an anonymous ICLR paper using {item['type']}. The immediate takeaway is: {item['answer']} {layout} Locked facts: {facts} {visual} Exact method labels are Initial model, Plain, SPECTRUM where present. Caption: {item['caption']} Alt text: {item['alt']} Boundary: {item['missing']} {finish}"
  assert len(prompt)<=5000,(num,i,len(prompt))
  doc+=f'\n## {chr(66+i)}. Option {i} — {title}\n\n**Rationale:** {layout}\n\n### Standalone English production prompt ({len(prompt)} characters)\n\n```text\n{prompt}\n```\n\n**Caption:** {item["caption"]}\n\n**Alt text:** {item["alt"]}\n'
  (OUT/f'figure_{num}_option_{i}.txt').write_text(prompt+'\n')
 doc+='\n## F. Fidelity and QA\n\n- Exactly three designs encode the same facts; layout changes do not change evidence.\n- Quantitative marks come from saved measurements or explicitly defined calculations.\n- One dominant scientific panel owns at least half the usable canvas.\n- Preserve single-seed scope, pairing, eligibility, and missing information.\n- Check legibility, clipping, arrow/text collisions, units, and grayscale reproduction at final paper width.\n'
 (OUT/f'figure_{num}_three_options.md').write_text(doc)
 all_docs.append(doc)
 manifest.append({'figure':num,'question':item['question'],'skill':item['skill'],'production':item['type'],'selected_option':1,'caption':item['caption'],'alt_text':item['alt']})
(HERE/'FIGURE_PROMPTS.md').write_text('# SPECTRUM — Complete English figure production prompts\n\nFour figures, each with three independent options. Every copyable prompt is below 5,000 characters. Quantitative figures use plotting code; no data image generation or prompt assembly is needed. Native LaTeX tables are in main.tex.\n\n'+'\n\n---\n\n'.join(all_docs))
(HERE/'figures/figure_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(HERE/'figures/CAPTIONS.md').write_text('\n\n'.join(f"## Figure {x['figure']}\n\n{x['caption']}\n\nAlt text: {x['alt_text']}" for x in manifest)+'\n')
print('Wrote 12 standalone English prompts, all under 5000 characters.')
