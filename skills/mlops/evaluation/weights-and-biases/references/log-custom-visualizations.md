---
skill_id: 388077d6a48b
usage_count: 1
last_used: 2026-06-16
---
# Log custom visualizations
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot(x, y)
wandb.log({"custom_plot": wandb.Image(fig)})