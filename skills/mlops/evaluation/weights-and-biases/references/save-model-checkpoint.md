---
skill_id: 21dc6b58cd80
usage_count: 1
last_used: 2026-06-16
---
# Save model checkpoint
checkpoint = {
    'epoch': epoch,
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'loss': loss,
}

torch.save(checkpoint, 'checkpoint.pth')