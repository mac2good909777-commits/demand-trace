# -*- coding: utf-8 -*-
"""查 MOPS 全文檢索（ezsearch_query），指定日期 + 關鍵字窄查，去重後輸出。

用法: python tools/mops_daily.py [YYYYMMDD]   （預設昨日需自行指定）
輸出: tools/_mops_<DATE>.json  （meta / count / rows）
再用 tools/mops_report.py <DATE> 轉成可讀報表。

註：MOPS 單次查詢硬上限 1000 筆，達到即在 meta 標記 [TRUNCATED]。
    同一則公告在不同關鍵字（甚至同一關鍵字）下會重複回傳，故以
    (COMPANY_ID, CTIME, SUBJECT, SEQ) 全欄位去重。
"""
import json, io, sys, time
import urllib.request, urllib.parse

URL = "https://mopsov.twse.com.tw/mops/web/ezsearch_query"
DATE = sys.argv[1] if len(sys.argv) > 1 else "20260825"
KEYWORDS = ["不動產", "土地", "廠房", "建物", "使用權資產", "取得", "處分", "購置",
            "興建", "標得", "收購", "廠區", "營建", "租賃"]


def q(subject):
    body = urllib.parse.urlencode({
        "step": "00", "RADIO_CM": "2", "TYPEK": "all", "CO_ID": "",
        "PRO_ITEM": "", "SUBJECT": subject, "SDATE": DATE, "EDATE": DATE,
    }, encoding="utf-8").encode()
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


allrows, meta = {}, []
for kw in KEYWORDS:
    r = q(kw)
    if "_error" in r:
        meta.append("%s ERROR %s" % (kw, r["_error"]))
        continue
    rows = r.get("data") or []
    meta.append("%s -> %d%s" % (kw, len(rows), " [TRUNCATED]" if len(rows) >= 1000 else ""))
    print(meta[-1], flush=True)
    for row in rows:
        allrows[json.dumps(row, ensure_ascii=False, sort_keys=True)] = row
    time.sleep(0.4)

out = list(allrows.values())
p = r"C:\Claude\projects\demand-trace\tools\_mops_%s.json" % DATE
io.open(p, "w", encoding="utf-8").write(
    json.dumps({"date": DATE, "meta": meta, "count": len(out), "rows": out},
               ensure_ascii=False, indent=1))
print("unique=%d  saved %s" % (len(out), p))
