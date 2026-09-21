# Model and data recovery — 2026-09-21

This inventory preserves exact identities. It does not claim that local archives
have already been uploaded. Check remote chunk/asset hashes before retiring this disk.

## Must preserve

- `runs/checkpoint_archives/sep20_ssd/round_1` through `round_5`, including each
  `manifest.json` and **all** payload files. These are the only verified recoverable
  copies of the newly trained SSD models. Rounds 1–4 full weights were previously
  pruned; round 5 full weights remain on this disk. Every archive is relative to the
  same immutable Qwen 1.5B base, not to another SSD round.
- `RECOVERY_INVENTORY.json`, `SSD_ROUND5_ARCHIVE_PROOF.json`, the lossless archive
  utility and its environment. Archive model-file hashes match each round's original
  completion proof. SSD5 archive creation included actual streaming decode verification.
- `extra_reproducibility.tar.gz`, `EXTRA_REPRODUCIBILITY_MANIFEST.json`, and its proof.
  This contains exact MBPP prepared splits and the EvalPlus expected-output/timing cache.
- The separately prepared code/config/runtime/control backups, raw research results,
  task snapshots and hardlink mapping. Model weights cannot regenerate the same
  sampled programs or the original measured times.

The extra archive's `repo/data/mbpp/*` maps to `${REPO_ROOT}/data/mbpp/*`.
Its `cache/evalplus/*` maps to `${HOME}/.cache/evalplus/*`.
The pickle is a locally generated EvalPlus 0.3.1 cache for public HumanEvalPlus
v0.1.10, including oracle outputs and base_time/plus_time. It was not unpickled in
this migration. Validate SHA256 and use only the matching trusted evaluation code;
do not deserialize arbitrary replacement pickle files.

## Re-download instead of uploading tens of GB

`DOWNLOAD_PINNED_RESOURCES.sh` lists exact snapshot revisions and cached filenames.
Use the project environment's `hf download`, then verify file sizes and SHA256 against
`RECOVERY_INVENTORY.json`. Do not substitute `main` or a different model revision.

Model revisions:

| Model | Pinned revision |
|---|---|
| Qwen/Qwen2.5-Coder-1.5B-Instruct | `2e1fd397ee46e1388853d2af2c993145b0f1098a` |
| Qwen/Qwen2.5-Coder-3B-Instruct | `488639f1ff808d1d3d0ba301aef8c11461451ec5` |
| Qwen/Qwen2.5-Coder-7B-Instruct | `c03e6d358207e414f1eca0bb1891e29f1db0e242` |
| deepseek-ai/deepseek-coder-6.7b-instruct | `e5d64addd26a6a1db0f9b863abf6ee3141936807` |
| humanlong/improving-self-evolution-mbpp | `4f56c88502ebba3a1ad856fc59831ace3d9b53ee` |

The historical HF repository contains `plain`, `spd_hard`, and `spectral_soft`
final models. The remote immutable revision and all three remote LFS weight SHA256
values were checked through the HF API. They match local files. Consequently the
local historical-Plain duplicate delta is optional, not part of the indispensable
SSD backup. The completed SSD models are not present in that verified historical
repository.

Dataset revisions:

| Dataset | Pinned cached source revision |
|---|---|
| google-research-datasets/mbpp | `4bb6404fdc6cacfda99d4ac4205087b89d32030c` |
| codeparrot/apps | `21e74ddf8de1a21436da12e3e653065c5213e9d1` |
| deepmind/code_contests | `802411c3010cb00d1b05bad57ca77365a3c699d6` |
| livecodebench/code_generation_lite | `0fe84c3912ea0c4d4a78037083943e8f0c4dd505` |

Carry the prepared snapshots directly, not only the upstream revision: preparation
includes split seed, exclusions, limits and normalization. MBPP's original preparation
manifest had a null revision; the revision above identifies its surviving local HF
snapshot. HumanEvalPlus comes from EvalPlus release v0.1.10, not these HF datasets.
Prepared LiveCodeBench is one 2,426,900,841-byte file shared with two run task snapshots;
keep one content copy and restore the recorded hardlink mapping.

## Restore SSD byte-for-byte

After downloading the pinned Qwen 1.5B snapshot and reconstructing the archive files:

```bash
python runs/sep20_control/checkpoint_archive.py verify \
  --archive runs/checkpoint_archives/sep20_ssd/round_5 \
  --base "$HOME/.cache/huggingface/hub/models--Qwen--Qwen2.5-Coder-1.5B-Instruct/snapshots/2e1fd397ee46e1388853d2af2c993145b0f1098a"

python runs/sep20_control/checkpoint_archive.py restore \
  --archive runs/checkpoint_archives/sep20_ssd/round_5 \
  --base "$HOME/.cache/huggingface/hub/models--Qwen--Qwen2.5-Coder-1.5B-Instruct/snapshots/2e1fd397ee46e1388853d2af2c993145b0f1098a" \
  --output runs/sep20_ssd_5round_seed43_eval16_3090/ssd/round_5/model
```

The destination must not exist. The same procedure works independently for rounds
1–4, using new restoration directories; preserve their original pruned completion
markers. Restoration verifies exact file bytes, including metadata/tokenizer files.
Install the standard `xdelta3` CLI first; the archive tooling uses no GPU.

## GitHub transfer options

Prefer GitHub Release assets for immutable binary backups when the authenticated
transport supports them: the official limit is **under 2 GiB per asset**, up to 1,000
assets per release. Each SSD round archive easily fits. [GitHub release limits](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)

If only Git blob transport is available, split a deterministic bundle into **at most
40 MiB binary parts**, store ordered filenames/size/SHA256 for every part plus the
reassembled bundle SHA256, and verify remote bytes before considering it backed up.
This stays below the ordinary file limit; it does not remove repository/push limits.
GitHub documents a 2 GB push limit and a 100 MB object limit, with 10 GB as its
recommended maximum repository size. [GitHub repository limits](https://docs.github.com/en/repositories/creating-and-managing-repositories/repository-limits)

Do not upload base-model caches, access tokens, credentials, or entire virtualenvs.
Pinned download manifests and package requirements cover replaceable dependencies.
