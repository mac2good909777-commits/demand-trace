# -*- coding: utf-8 -*-
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
with open(r"C:\Claude\projects\demand-trace\tmp\progress.json", encoding='utf-8') as f:
    d = json.load(f)
rows = d.get('progress', [])
print("共", len(rows), "列")
for r in rows:
    print(" | ".join(str(x) for x in r))
