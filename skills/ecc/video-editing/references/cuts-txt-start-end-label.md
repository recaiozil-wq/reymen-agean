---
skill_id: d2b716574956
usage_count: 1
last_used: 2026-06-16
---
# cuts.txt: start,end,label
while IFS=, read -r start end label; do
  ffmpeg -i raw.mp4 -ss "$start" -to "$end" -c copy "segments/${label}.mp4"
done < cuts.txt
```

### Concatenate segments

```bash