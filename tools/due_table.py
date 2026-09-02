# -*- coding: utf-8 -*-
"""回訪／下一步到期表：依 watchlist.json 的 next 欄位，對照今日。"""
import sys, io, json, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
TODAY = datetime.date(2026, 9, 3)
with open(r"C:\Claude\projects\demand-trace\docs\data\watchlist.json", encoding='utf-8') as f:
    wl = json.load(f)
rows = []
for c in wl:
    n = (c.get('next') or '').strip()
    if not n:
        continue
    try:
        d = datetime.date.fromisoformat(n)
    except ValueError:
        continue
    delta = (TODAY - d).days
    rows.append((delta, c.get('score') or 0, c.get('company'), c.get('ticker'),
                 c.get('nextKind'), c.get('active'), n))
rows.sort(key=lambda r: (-r[0], -r[1]))
print(f"{'逾期天':>6} {'分':>4} {'公司':<12} {'類型':<6} 排定日")
for delta, sc, co, tk, kind, act, n in rows:
    if delta < 0:
        tag = f"未到({-delta}天後)"
    elif delta == 0:
        tag = "今日到期"
    else:
        tag = f"逾期{delta}天"
    print(f"{tag:>10} {sc:>4} {co:<12} {str(kind):<6} {n} active={act}")
