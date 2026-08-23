# -*- coding: utf-8 -*-
"""查單一公司近一年 MOPS 重訊（全文檢索，依 CO_ID）。用法：python _mops_co.py 7828 [SDATE] [EDATE]"""
import json, sys, urllib.request, urllib.parse, time
sys.stdout.reconfigure(encoding="utf-8")

URL = "https://mopsov.twse.com.tw/mops/web/ezsearch_query"
co = sys.argv[1]
SDATE = sys.argv[2] if len(sys.argv) > 2 else "20250824"
EDATE = sys.argv[3] if len(sys.argv) > 3 else "20260824"

data = {"step": "00", "RADIO_CM": "2", "TYPEK": "all", "CO_ID": co,
        "PRO_ITEM": "", "SUBJECT": "", "SDATE": SDATE, "EDATE": EDATE}
body = urllib.parse.urlencode(data, encoding="utf-8").encode()
req = urllib.request.Request(URL, data=body, headers={
    "User-Agent": "Mozilla/5.0", "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://mopsov.twse.com.tw/mops/web/ezsearch"})
raw = urllib.request.urlopen(req, timeout=60).read()
r = json.loads(raw.decode("utf-8-sig"))
rows = r.get("data") or []
print("n=%d%s" % (len(rows), " [TRUNCATED]" if len(rows) >= 1000 else ""))
KW = ["不動產", "土地", "廠房", "建物", "使用權", "取得", "處分", "購置", "興建", "營造", "工程", "租", "設廠", "投資"]
for x in rows:
    s = x.get("SUBJECT", "")
    if any(k in s for k in KW):
        print("%s | %s | %s" % (x.get("CDATE"), x.get("COMPANY_NAME"), s))
        print("   ", x.get("HYPERLINK"))
