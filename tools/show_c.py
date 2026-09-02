# -*- coding: utf-8 -*-
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
p = r"C:\Users\dell\Documents\Claude-DT\projects\00000000-全域設定\industrial-monitor-DT\queue\export_c.json"
with open(p, encoding='utf-8') as f:
    d = json.load(f)
print("count:", d.get('count'), "latest:", d.get('latest_處理時間'))
for i, r in enumerate(d['rows'], 1):
    print(f"\n[{i}] {r.get('標題')}")
    print(f"    來源={r.get('來源名稱')} 分類={r.get('分類')} impact={r.get('impact_level')} urgency={r.get('urgency_level')} 擴廠訊號={r.get('擴廠訊號')} 發布={r.get('文章發布日')}")
    s = r.get('LLM摘要') or r.get('摘要') or ''
    print(f"    摘要: {s[:260]}")
    y = r.get('要項') or ''
    if y:
        print(f"    要項: {y[:400]}")
    a = r.get('業務應用建議') or r.get('action_suggestion') or ''
    if a:
        print(f"    建議: {a[:260]}")
    if r.get('連結'):
        print(f"    連結: {r.get('連結')}")
