import torch
from tests.helpers import tiny_model_and_tokenizer
from improving.training import train_on_records


def test_real_lora_update_and_merged_checkpoint_reload(tmp_path):
    model, tok = tiny_model_and_tokenizer()
    before = model.model.layers[0].self_attn.q_proj.weight.detach().clone()
    tasks = [{'task_id': 'toy/1', 'prompt': 'Write a function', 'source': 'fixture', 'split': 'train'}]
    records = [{'task_id': 'toy/1', 'sample_id': 0, 'completion': 'def f ( ) : return 1'}]
    config = {'epochs': 1, 'batch_size': 1, 'gradient_accumulation_steps': 4,
              'learning_rate': 0.01, 'max_length': 64, 'lora_rank': 2,
              'lora_alpha': 2, 'lora_dropout': 0.0, 'gradient_checkpointing': False,
              'loss_scope': 'completion', 'warmup_ratio': 0.0}
    merged, stats = train_on_records(model, tok, tasks, records, config, tmp_path / 'model', seed=42)
    assert stats['optimizer_steps'] == 1
    assert stats['examples'] == 1
    assert not torch.equal(before, merged.model.layers[0].self_attn.q_proj.weight)
    from transformers import AutoModelForCausalLM
    restored = AutoModelForCausalLM.from_pretrained(tmp_path / 'model')
    torch.testing.assert_close(restored.model.layers[0].self_attn.q_proj.weight,
                               merged.model.layers[0].self_attn.q_proj.weight)
