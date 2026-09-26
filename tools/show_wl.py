# -*- coding: utf-8 -*-
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import os as _os
_R = _os.environ.get('DT_REPO') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if not _os.path.isdir(_os.path.join(_R, 'docs', 'data')):
    _R = r"C:\Users\dell\Documents\Claude-DT\projects\20260808-需求軌跡\demand-trace"   # 本機（Windows）路徑；容器內以 __file__ 推導為主
with open((_R + "/docs/data/watchlist.json"), encoding='utf-8') as f:
    wl = json.load(f)
args = sys.argv[1:]
if args and args[0] == 'one':
    for c in wl:
        if c.get('company') == args[1]:
            print(json.dumps(c, ensure_ascii=False, indent=1))
else:
    for c in sorted(wl, key=lambda x: -(x.get('score') or 0)):
        if (c.get('score') or 0) < 60:
            continue
        print(f"--- {c.get('company')} {c.get('ticker')} score={c.get('score')} tier={c.get('tier')} active={c.get('active')} next={c.get('next')} nextKind={c.get('nextKind')}")
        print(f"    nextWhat: {c.get('nextWhat')}")
        print(f"    advice: {c.get('advice')}")
