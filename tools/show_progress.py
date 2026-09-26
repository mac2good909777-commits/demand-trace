# -*- coding: utf-8 -*-
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import os as _os
_R = _os.environ.get('DT_REPO') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if not _os.path.isdir(_os.path.join(_R, 'docs', 'data')):
    _R = r"C:\Users\dell\Documents\Claude-DT\projects\20260808-需求軌跡\demand-trace"   # 本機（Windows）路徑；容器內以 __file__ 推導為主
with open((_R + "/tmp/progress.json"), encoding='utf-8') as f:
    d = json.load(f)
rows = d.get('progress', [])
print("共", len(rows), "列")
for r in rows:
    print(" | ".join(str(x) for x in r))
