# -*- coding: utf-8 -*-
"""查 MOPS 全文檢索（ezsearch_query），指定日期區間 + 關鍵字窄查。
輸出 JSON 到 scratchpad。"""
import json, sys, urllib.request, urllib.parse, time

URL = "https://mopsov.twse.com.tw/mops/web/ezsearch_query"
SDATE = "20260822"
EDATE = "20260824"

KEYWORDS = ["不動產", "土地", "廠房", "建物", "使用權資產", "取得", "處分", "購置", "興建", "廠區", "營建"]

def q(subject):
    data = {
        "step": "00", "RADIO_CM": "2", "TYPEK": "all", "CO_ID": "",
        "PRO_ITEM": "", "SUBJECT": subject, "SDATE": SDATE, "EDATE": EDATE,
    }
    body = urllib.parse.urlencode(data, encoding="utf-8").encode()
    req = urllib.request.Request(URL, data=body, headers={
        "User-Agent": "Mozilla/5.0", "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://mopsov.twse.com.tw/mops/web/ezsearch",
    })
    for attempt in range(3):
        try:
            raw = urllib.request.urlopen(req, timeout=60).read()
            return json.loads(raw.decode("utf-8-sig"))
        except Exception as e:
            if attempt == 2:
                return {"_error": str(e)}
            time.sleep(3)

out = {}
for k in KEYWORDS:
    r = q(k)
    rows = r.get("data") or []
    out[k] = {"n": len(rows), "truncated": len(rows) >= 1000, "rows": rows}
    print("%s -> %d%s" % (k, len(rows), " [TRUNCATED]" if len(rows) >= 1000 else ""), flush=True)

p = r"C:\Users\dell\AppData\Local\Temp\claude\C--Users-dell-Documents-Claude-DT-projects-00000000-----\7eb4fd5f-a1e3-4ec9-86d0-859b9de1aacc\scratchpad\mops.json"
json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False)
print("saved", p)
