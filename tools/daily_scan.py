# -*- coding: utf-8 -*-
"""每日掃描輔助：連線測試 + 觀察名單摘要"""
import sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import os as _os
_R = _os.environ.get('DT_REPO') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if not _os.path.isdir(_os.path.join(_R, 'docs', 'data')):
    _R = r"C:\Users\dell\Documents\Claude-DT\projects\20260808-需求軌跡\demand-trace"   # 本機（Windows）路徑；容器內以 __file__ 推導為主

REPO = _R

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
