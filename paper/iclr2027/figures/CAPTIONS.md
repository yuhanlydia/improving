## Figure 1

Five MBPP self-distillation rounds, 500 tasks and 16 samples per task. Native-student point estimates; paired D4 changes are relative to initialization on common eligible tasks, with archived pointwise 95% task-bootstrap intervals. One training seed. AST classes are structural proxies.

Alt text: Accuracy rises as correct AST richness falls. SPECTRUM retains more richness and more dispersed correct outputs than Plain.

## Figure 2

SPECTRUM within Looped Self-Distillation. The fixed reference anchor calibrates changing native-student geometry; a temporary proximal K/V transform produces raw training data. Restoring weights and merging one LoRA yields the next student. Final inference uses no transform.

Alt text: A fixed anchor guides per-round geometry; the model generates all raw samples, learns through one LoRA, and returns as the next native student.

## Figure 3

The same final 64-sample pools on 500 MBPP tasks give Ck and pass@k for k=1,4,8,16,64. Paired SPECTRUM-minus-Plain Db contrasts use common eligible tasks at b=4,8,16 and archived 95% task-bootstrap intervals. One training seed.

Alt text: SPECTRUM yields more correct structures than Plain as total budget increases, with positive richness gains when correct-sample counts are matched.

## Figure 4

Actual saved equal-correct-count examples, selected by the same lowest-ID rule for each sign. Frequency ranks are within-model, not aligned semantic classes. Both positive and negative examples are shown. These sample-level equalities do not establish equality of true success probabilities.

Alt text: HumanEval/3 shows counts 16 versus 15+1 at equal success; HumanEval/2 shows fewer structures for SPECTRUM despite the same 12 correct outputs.
