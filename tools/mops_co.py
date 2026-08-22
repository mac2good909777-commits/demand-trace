# -*- coding: utf-8 -*-
"""依公司名／關鍵字查 MOPS 全文檢索指定日期區間。
用法: python _mops_co.py <SDATE> <EDATE> <關鍵字1> [關鍵字2 ...]
"""
import json, io, os, sys, time
import urllib.request, urllib.parse

URL = "https://mopsov.twse.com.tw/mops/web/ezsearch_query"
HDR = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://mopsov.twse.com.tw/mops/web/ezsearch_query",
}


def query(subject, sdate, edate):
    data = {"step": "00", "RADIO_CM": "2", "TYPEK": "all", "CO_ID": "",
            "PRO_ITEM": "", "SUBJECT": subject, "SDATE": sdate, "EDATE": edate}
    body = urllib.parse.urlencode(data, encoding="utf-8").encode()
    req = urllib.request.Request(URL, data=body, headers=HDR)
    for a in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8-sig"))
        except Exception as e:
            if a == 2:
                return {"_error": str(e)}
            time.sleep(3)


sdate, edate = sys.argv[1], sys.argv[2]
kws = sys.argv[3:]
out = {}
for kw in kws:
    j = query(kw, sdate, edate)
    rows = j.get("data") or []
    out[kw] = rows
    print("===", kw, len(rows), "TRUNCATED!" if len(rows) >= 1000 else "", j.get("_error") or "")
    for r in rows:
        print("  ", r.get("CDATE"), r.get("TYPEK"), r.get("COMPANY_ID"), r.get("COMPANY_NAME"), "|", r.get("SUBJECT"))
        print("     ", r.get("HYPERLINK"))

with io.open(r"C:\Claude\projects\demand-trace\tmp\mops_co.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
