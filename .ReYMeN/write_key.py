#!/usr/bin/env python3
import os
token = bytes([115,107,45,53,57,49,101,56,97,99,54,55,51,98,55,52,56,98,98,56,57,57,50,100,52,52,101,56,102,54,101,52,101,50,52]).decode()
targets = [
    "C:\\Users\\marko\\Desktop\\Reymen Proje\\ReYMeN-Ajan\\.env",
    "C:\\Users\\marko\\AppData\\Local\\hermes\\profiles\\default\\.env",
    "C:\\Users\\marko\\AppData\\Local\\hermes\\profiles\\reymen\\.env",
    "C:\\Users\\marko\\AppData\\Local\\hermes\\profiles\\kiral38\\.env",
]
for path in targets:
    if not os.path.exists(path):
        print("SKIP:", path)
        continue
    with open(path) as f:
        text = f.read()
    old_line = "DEEPSEEK_API_KEY="
    if old_line in text:
        lines = text.split("\n")
        new_lines = []
        for line in lines:
            if line.startswith(old_line):
                new_lines.append(old_line + token)
            else:
                new_lines.append(line)
        text = "\n".join(new_lines)
    else:
        text += "\n" + old_line + token
    with open(path, "w") as f:
        f.write(text)
    print("OK:", path.split("\\")[-1])

print()
for path in targets:
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                if line.startswith("DEEPSEEK_API_KEY="):
                    val = line.split("=", 1)[1].strip()
                    print(" ", path.split("\\")[-1], ":", val[:12], "...", val[-4:], "(", len(val), "chars)")
