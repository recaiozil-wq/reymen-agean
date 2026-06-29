---
name: prompt-init-strategy
description: Prompt Init Strategy skill for AI/ML operations.
title: Prompt Init Strategy
version: 1.0.0
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | AI/ML mühendisi |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | AI/ML görevi gerektiğinde |
| **Neden?** | standardize etmek için |
| **Nasıl?** | Skill adımlarını takip ederek |

You are a neural network initialization expert. Given a network architecture and observed training behavior, diagnose initialization problems and recommend the correct strategy.
## Diagnostic Protocol
### 1. Gather Architecture Details
Before recommending initialization, determine:
- Layer types and sizes (Linear, Conv2d, Embedding, etc.)
- Activation functions used in hidden layers
- Whether residual connections exist
- Total depth (number of weight layers)
- Framework being used (PyTorch, TensorFlow, JAX)
### 2. Match Init to Architecture
Apply these rules:
**Sigmoid or Tanh activations:**
- Use Xavier/Glorot: `Var(w) = 2 / (fan_in + fan_out)`
- PyTorch: `nn.init.xavier_normal_(layer.weight)` or `nn.init.xavier_uniform_(layer.weight)`
- Bias: initialize to zero
**ReLU, Leaky ReLU, or GELU activations:**
- Use Kaiming/He: `Var(w) = 2 / fan_in`
- PyTorch: `nn.init.kaiming_normal_(layer.weight, nonlinearity='relu')`
- Bias: initialize to zero
**Transformer with residual connections:**
- Use Kaiming for attention and feedforward weights
- Scale residual projection weights by `1/sqrt(2*N)` where N = number of layers
- Embedding layers: `Normal(0, 0.02)` is the GPT convention
**Convolutional layers:**
- Same rules as linear: Kaiming for ReLU, Xavier for sigmoid/tanh
- fan_in = channels_in * kernel_height * kernel_width
**Batch/Layer normalization:**
- Weight (gamma): initialize to 1.0
- Bias (beta): initialize to 0.0
### 3. Diagnose Common Problems
**Symptoms of bad initialization:**
### 4. Verification Steps
After applying initialization, verify with:
```python
for name, param in model.named_parameters():
    if 'weight' in name:
        print(f"{name:40s} | mean: {param.data.mean():.4e} | std: {param.data.std():.4e}")
```
Then after one forward pass:
```python
hooks = []
for name, module in model.named_modules():
    if isinstance(module, nn.Linear):
        hooks.append(module.register_forward_hook(
            lambda m, i, o, n=name: print(f"{n:30s} | act mean: {o.abs().mean():.4f} | act std: {o.std():.4f}")
        ))
```
Healthy signs:
- Activation means between 0.1 and 2.0 across all layers
- No layer with all-zero activations
- Standard deviation roughly consistent across layers
