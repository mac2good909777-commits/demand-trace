# -*- coding: utf-8 -*-
"""MOPS 全文檢索：依關鍵字掃指定日期區間的重大訊息。
用法：python tools/mops_scan.py <SDATE> <EDATE>
輸出：C:\\Claude\\projects\\demand-trace\\tmp\\mops_<SDATE>_<EDATE>.json
"""
import sys, io, os, json, time, urllib.request, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

URL = "https://mopsov.twse.com.tw/mops/web/ezsearch_query"
OUT_DIR = r"C:\Claude\projects\demand-trace\tmp"

KEYWORDS = ["不動產", "土地", "廠房", "建物", "使用權資產", "取得", "處分",
            "購置", "興建", "設備", "工程", "租賃", "廠區", "投資"]


def query(subject, sdate, edate, co_id=""):
    data = {
        "step": "00", "RADIO_CM": "2", "TYPEK": "all",
        "CO_ID": co_id, "PRO_ITEM": "", "SUBJECT": subject,
        "SDATE": sdate, "EDATE": edate,
    }
    body = urllib.parse.urlencode(data, encoding='utf-8').encode()
    req = urllib.request.Request(URL, data=body, headers={
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded",
    })
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read().decode('utf-8-sig', errors='replace')
            return json.loads(raw)
        except Exception as e:
            if attempt == 2:
                return {"_error": str(e)}
            time.sleep(3)


def main():
    sdate, edate = sys.argv[1], sys.argv[2]
    os.makedirs(OUT_DIR, exist_ok=True)
    all_rows = {}
    truncated = []
    for kw in KEYWORDS:
        res = query(kw, sdate, edate)
        if "_error" in res:
            print(f"[ERR] {kw}: {res['_error']}")
            continue
        rows = res.get("data") or []
        if len(rows) >= 1000:
            truncated.append(kw)
        print(f"[OK] {kw}: {len(rows)} 筆")
        for row in rows:
            key = json.dumps(row, ensure_ascii=False, sort_keys=True)
            all_rows[key] = row
        time.sleep(1)
    out = {"sdate": sdate, "edate": edate, "truncated": truncated,
           "rows": list(all_rows.values())}
    path = os.path.join(OUT_DIR, f"mops_{sdate}_{edate}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"\n合計去重 {len(out['rows'])} 筆 -> {path}")
    if truncated:
        print("⚠️ 可能被截斷的關鍵字:", truncated)
    if out["rows"]:
        print("欄位:", list(out["rows"][0].keys()))


if __name__ == "__main__":
    main()
