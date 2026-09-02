# -*- coding: utf-8 -*-
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
with open(r"C:\Claude\projects\demand-trace\docs\data\watchlist.json", encoding='utf-8') as f:
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
