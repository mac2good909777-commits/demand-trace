# -*- coding: utf-8 -*-
import json, io, sys
DATE = sys.argv[1] if len(sys.argv) > 1 else "20260825"
d = json.load(io.open(r"C:\Claude\projects\demand-trace\tools\_mops_%s.json" % DATE, encoding="utf-8"))
wl = json.load(io.open(r"C:\Claude\projects\demand-trace\docs\data\watchlist.json", encoding="utf-8"))
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
io.open(r"C:\Claude\projects\demand-trace\tools\_mops_report.txt", "w", encoding="utf-8").write("\n".join(lines))
print("ok")
