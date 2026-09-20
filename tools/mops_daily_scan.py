# -*- coding: utf-8 -*-
"""每日 MOPS 重訊全市場掃描（關鍵字窄查 ＋ 觀察名單公司名逐一查）。

用法：
    python tools/mops_daily_scan.py 20260919 [20260920 ...]
    （不給參數則預設掃「昨天」；本任務 02:30 執行，MOPS 即時端點凌晨查當日是空的，
      一律要查昨天——見 SKILL.md「MOPS 的時間特性」）

🔴 去重鍵＝完整 HYPERLINK，不要用主旨、也不要用 SPOKE_DATE/SPOKE_TIME。

  2026-09-19 教訓：用 SUBJECT 當 key，玉山金同日兩則同主旨重訊（台中 3.75 億／
  新北 5.276 億）被併成一則，台中那筆被靜默吞掉。
  2026-09-20 教訓：改用 (COMPANY_ID, SPOKE_DATE, SPOKE_TIME) 仍然錯——
  ezsearch_query 實際回傳欄位是 CDATE/CTIME，**根本沒有 SPOKE_DATE/SPOKE_TIME**
  （那兩個只存在於 HYPERLINK 的 query string 裡）。用不存在的欄位當 key，
  dict.get() 全回 None，去重鍵塌成 (COMPANY_ID, None, None)
  ＝一家公司一天只留一則，**不拋例外、只少資料**。

  實際回傳欄位：CDATE, CTIME, COMPANY_ID, COMPANY_NAME, SUBJECT,
                AN_NAME, AN_CODE, CODE_NAME, TYPEK, HYPERLINK
  HYPERLINK 內含 SEQ_NO+SPOKE_TIME+SPOKE_DATE+COMPANY_ID，天然唯一，直接拿來當 key。

⚠️ 單次查詢硬上限 1000 筆，本腳本會檢查並在達標時列出該關鍵字（代表可能被截斷）。
⚠️ 回應為 UTF-8 with BOM，須以 utf-8-sig 解碼。
"""
import json, sys, io, os, time, datetime
import urllib.request, urllib.parse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE_URL = "https://script.google.com/macros/s/AKfycbzmlpV1fpt1RWxVwZj8teUHWw4fs4zpix_3JqCVGX4SeMPIp5Di6_6m_YDRZn4fBQ4/exec"
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tmp")
os.makedirs(OUTDIR, exist_ok=True)
URL = "https://mopsov.twse.com.tw/mops/web/ezsearch_query"

DATES = sys.argv[1:] or [(datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y%m%d")]

KEYWORDS = ["不動產", "土地", "廠房", "建物", "使用權資產", "取得", "處分",
            "購置", "購買", "收購", "標得", "興建", "擴產", "設廠", "廠區", "資產",
            "租賃", "工廠", "投資"]

def query(subject, date):
    data = {"step":"00","RADIO_CM":"2","TYPEK":"all","CO_ID":"","PRO_ITEM":"",
            "SUBJECT":subject,"SDATE":date,"EDATE":date}
    body = urllib.parse.urlencode(data, encoding="utf-8").encode("ascii")
    req = urllib.request.Request(URL, data=body, headers={
        "User-Agent":"Mozilla/5.0","Content-Type":"application/x-www-form-urlencoded"})
    for a in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8-sig", errors="replace"))
        except Exception as e:
            if a == 2: return {"_error": str(e)}
            time.sleep(3)

req = urllib.request.Request(BASE_URL + "?list=watch", headers={"User-Agent": "Mozilla/5.0"})
w = json.loads(urllib.request.urlopen(req, timeout=180).read().decode("utf-8-sig", errors="replace"))
companies = [str(r[0]).strip() for r in w.get("watchlist", [])[1:] if r and str(r[0]).strip()]

hits = {}
truncated = []
errors = []
summary = {}

for date in DATES:
    for t in KEYWORDS + companies:
        res = query(t, date)
        if isinstance(res, dict) and "_error" in res:
            errors.append((date, t, res["_error"])); continue
        data = res.get("data") or []
        if len(data) >= 1000: truncated.append((date, t, len(data)))
        if data: summary.setdefault(date, {})[t] = len(data)
        for d in data:
            key = d.get("HYPERLINK") or json.dumps(d, sort_keys=True)
            if key not in hits:
                d["_hit_date"] = date
                hits[key] = d

print("查詢日期：", DATES)
print("關鍵字數：", len(KEYWORDS), "／觀察名單公司數：", len(companies))
print("錯誤數：", len(errors))
for e in errors[:10]: print("  ERROR", e)
print("達1000上限：", truncated if truncated else "無")
print("\n=== 有命中的關鍵字 ===")
for date, m in summary.items():
    print(f"[{date}]", ", ".join(f"{k}:{v}" for k,v in m.items()))

out = sorted(hits.values(), key=lambda x: (x.get("CDATE",""), str(x.get("CTIME",""))))
outpath = os.path.join(OUTDIR, "mops_%s_%s.json" % (DATES[0], DATES[-1]))
with open(outpath, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("\n已寫入:", os.path.normpath(outpath))

print(f"\n=== 去重後共 {len(out)} 則（key=HYPERLINK）===")
for d in out:
    print(f"{d.get('CDATE')} {d.get('CTIME')} | {d.get('COMPANY_ID')} {d.get('COMPANY_NAME')} "
          f"[{d.get('TYPEK')}/{d.get('CODE_NAME')}] {d.get('AN_NAME')}")
    print(f"    {str(d.get('SUBJECT'))[:150]}")
