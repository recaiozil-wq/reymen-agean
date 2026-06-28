---
skill_id: 33b0f96df8fa
usage_count: 1
last_used: 2026-06-16
---
# Pad to max length in batch
    padded = nn.utils.rnn.pad_sequence(sequences, batch_first=True, padding_value=0)
    return padded, torch.tensor(labels)

dataloader = DataLoader(dataset, batch_size=32, collate_fn=collate_fn)
```