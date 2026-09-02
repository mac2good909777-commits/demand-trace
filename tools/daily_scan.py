# -*- coding: utf-8 -*-
"""每日掃描輔助：連線測試 + 觀察名單摘要"""
import sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

REPO = r"C:\Claude\projects\demand-trace"

def load(name):
    with open(os.path.join(REPO, 'docs', 'data', name), encoding='utf-8') as f:
        return json.load(f)

if __name__ == '__main__':
    wl = load('watchlist.json')
    print("watchlist 家數:", len(wl))
    if wl:
        print("欄位:", list(wl[0].keys()))
    rows = []
    for c in wl:
        rows.append((c.get('score', 0) or 0, c.get('company'), c.get('ticker'),
                     c.get('priority'), c.get('active'), (c.get('advice') or '')[:0]))
    rows.sort(reverse=True, key=lambda r: r[0])
    for r in rows:
        print(f"{r[0]:>4} | {r[1]} {r[2] or ''} | {r[3]} | active={r[4]}")
