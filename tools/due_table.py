# -*- coding: utf-8 -*-
"""回訪／下一步到期表：依 watchlist.json 的 next 欄位，對照今日。

用法：python tools/due_table.py [YYYY-MM-DD]
　　　不給參數＝用系統今日；給日期＝以該日為基準（回溯檢查用）。

🔴 2026-09-25 修正：原本寫死 `TODAY = datetime.date(2026, 9, 3)`，
自 9/4 起每天都把已逾期的項目印成「未到(N天後)」，**連續 22 天輸出方向相反的到期表**。
到期表是每日總結置頂的「回訪到期表」的資料來源，一旦看成「未到」就不會被點名。
**基準日一律取系統今日，不要再寫死。**
"""
import sys, io, json, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import os as _os
_R = _os.environ.get('DT_REPO') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if not _os.path.isdir(_os.path.join(_R, 'docs', 'data')):
    _R = r"C:\Users\dell\Documents\Claude-DT\projects\20260808-需求軌跡\demand-trace"   # 本機（Windows）路徑；容器內以 __file__ 推導為主
TODAY = (datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1
         else datetime.date.today())
print(f"（基準日：{TODAY.isoformat()}）")
with open((_R + "/docs/data/watchlist.json"), encoding='utf-8') as f:
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
