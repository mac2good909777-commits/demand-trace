# -*- coding: utf-8 -*-
"""昨日 MOPS 全文檢索：分關鍵字窄查 + 觀察名單逐家查（近14天）"""
import json, io, os, sys, time
import urllib.request, urllib.parse

URL = "https://mopsov.twse.com.tw/mops/web/ezsearch_query"
OUT = r"C:\Claude\projects\demand-trace\tmp"
os.makedirs(OUT, exist_ok=True)

DAY = sys.argv[1] if len(sys.argv) > 1 else "20260822"
SDATE = sys.argv[2] if len(sys.argv) > 2 else DAY
EDATE = sys.argv[3] if len(sys.argv) > 3 else DAY

KEYWORDS = ["不動產", "土地", "廠房", "建物", "使用權資產", "取得", "處分", "購置", "興建", "廠區"]

HDR = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://mopsov.twse.com.tw/mops/web/ezsearch_query",
}


def query(subject, sdate, edate):
    data = {
        "step": "00", "RADIO_CM": "2", "TYPEK": "all", "CO_ID": "",
        "PRO_ITEM": "", "SUBJECT": subject, "SDATE": sdate, "EDATE": edate,
    }
    body = urllib.parse.urlencode(data, encoding="utf-8").encode()
    req = urllib.request.Request(URL, data=body, headers=HDR)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read()
            return json.loads(raw.decode("utf-8-sig"))
        except Exception as e:
            if attempt == 2:
                return {"_error": str(e)}
            time.sleep(3)


result = {}
for kw in KEYWORDS:
    j = query(kw, SDATE, EDATE)
    rows = j.get("data") or []
    result[kw] = {
        "n": len(rows),
        "truncated": len(rows) >= 1000,
        "error": j.get("_error"),
        "rows": rows,
    }
    print(kw, len(rows), "TRUNCATED!" if len(rows) >= 1000 else "", j.get("_error") or "")

with io.open(os.path.join(OUT, "mops_kw.json"), "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)

print("saved", os.path.join(OUT, "mops_kw.json"))
