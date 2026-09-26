# -*- coding: utf-8 -*-
import json, io, sys
import os as _os
_R = _os.environ.get('DT_REPO') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if not _os.path.isdir(_os.path.join(_R, 'docs', 'data')):
    _R = r"C:\Users\dell\Documents\Claude-DT\projects\20260808-需求軌跡\demand-trace"   # 本機（Windows）路徑；容器內以 __file__ 推導為主
DATE = sys.argv[1] if len(sys.argv) > 1 else "20260825"
d = json.load(io.open((_R + "/tools/_mops_%s.json") % DATE, encoding="utf-8"))
wl = json.load(io.open((_R + "/docs/data/watchlist.json"), encoding="utf-8"))
names = set()
for c in wl:
    names.add(c["company"])
    for g in c.get("group", []):
        names.add(g["n"].split("（")[0].split("(")[0])
rows = sorted(d["rows"], key=lambda r: r.get("CTIME", ""))
lines = ["meta: " + " | ".join(d["meta"]), "unique=%d" % d["count"], ""]
for r in rows:
    cn = r.get("COMPANY_NAME", "")
    hit = [n for n in names if n and (n in cn or cn in n)]
    lines.append("%s %s %s(%s) [%s] %s%s\n    %s" % (
        r.get("CDATE"), r.get("CTIME"), cn, r.get("COMPANY_ID"), r.get("TYPEK"),
        r.get("AN_NAME"), ("  <<<觀察名單 %s" % hit if hit else ""),
        (r.get("SUBJECT") or "").replace("\r\n", " ")))
    lines.append("    " + (r.get("HYPERLINK") or ""))
io.open((_R + "/tools/_mops_report.txt"), "w", encoding="utf-8").write("\n".join(lines))
print("ok")
