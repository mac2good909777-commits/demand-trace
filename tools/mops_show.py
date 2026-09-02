# -*- coding: utf-8 -*-
"""列出 mops_scan 結果，並標示是否在觀察名單。"""
import sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

REPO = r"C:\Claude\projects\demand-trace"
path = sys.argv[1]
with open(path, encoding='utf-8') as f:
    d = json.load(f)
with open(os.path.join(REPO, 'docs', 'data', 'watchlist.json'), encoding='utf-8') as f:
    wl = json.load(f)
names = {c.get('company') for c in wl}
tickers = {str(c.get('ticker', '')).split('(')[0].strip() for c in wl}

KEY = ["取得", "處分", "購置", "購買", "收購", "標得", "興建", "設廠", "廠房", "土地", "不動產", "建物", "資產"]

rows = sorted(d['rows'], key=lambda r: (r.get('COMPANY_ID', ''), r.get('CTIME', '')))
hits, others = [], []
for r in rows:
    subj = r.get('SUBJECT', '')
    cid = str(r.get('COMPANY_ID', '')).strip()
    cname = r.get('COMPANY_NAME', '')
    inwl = cname in names or cid in tickers
    mark = "★名單" if inwl else "     "
    line = f"{mark} {cid:>6} {cname[:14]:<14} | {subj}"
    if inwl or any(k in subj for k in KEY):
        hits.append(line)
    else:
        others.append(line)

print(f"=== 相關/名單內 ({len(hits)}) ===")
for l in hits:
    print(l)
print(f"\n=== 其他 ({len(others)}) ===")
for l in others:
    print(l)
