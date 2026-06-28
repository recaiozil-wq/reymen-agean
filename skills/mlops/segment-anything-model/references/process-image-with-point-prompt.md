---
skill_id: cd1b9d38d3d0
usage_count: 1
last_used: 2026-06-16
---
# Process image with point prompt
image = Image.open("image.jpg")
input_points = [[[450, 600]]]  # Batch of points

inputs = processor(image, input_points=input_points, return_tensors="pt")
inputs = {k: v.to("cuda") for k, v in inputs.items()}