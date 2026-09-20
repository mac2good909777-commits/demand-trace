# -*- coding: utf-8 -*-
"""查單一公司近一年 MOPS 重訊（CO_ID 查詢）。"""
import json, sys, io, time
import urllib.request, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
URL = "https://mopsov.twse.com.tw/mops/web/ezsearch_query"

def q(co_id, sdate, edate, subject=""):
    data = {"step":"00","RADIO_CM":"2","TYPEK":"all","CO_ID":co_id,"PRO_ITEM":"",
            "SUBJECT":subject,"SDATE":sdate,"EDATE":edate}
    body = urllib.parse.urlencode(data, encoding="utf-8").encode("ascii")
    req = urllib.request.Request(URL, data=body, headers={
        "User-Agent":"Mozilla/5.0","Content-Type":"application/x-www-form-urlencoded"})
    for a in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8-sig", errors="replace"))
        except Exception as e:
            if a==2: return {"_error":str(e)}
            time.sleep(3)

CO = sys.argv[1] if len(sys.argv)>1 else "4571"
hits = {}
# 近一年按季切，避開 1000 上限
ranges = [("20250920","20251231"),("20260101","20260331"),
          ("20260401","20260630"),("20260701","20260920")]
for s,e in ranges:
    res = q(CO, s, e)
    if "_error" in res:
        print("ERROR", s, e, res["_error"]); continue
    d = res.get("data") or []
    print(f"{s}~{e}: {len(d)} 筆" + ("  ⚠️達1000上限" if len(d)>=1000 else ""))
    for x in d:
        hits[x.get("HYPERLINK") or json.dumps(x,sort_keys=True)] = x

out = sorted(hits.values(), key=lambda x:(x.get("CDATE",""), str(x.get("CTIME",""))))
print(f"\n=== {CO} 近一年去重後 {len(out)} 則 ===")
for d in out:
    print(f"{d.get('CDATE')} | {d.get('AN_NAME')} | {str(d.get('SUBJECT'))[:130]}")

KEY = ["不動產","土地","廠房","建物","使用權","購置","取得","處分","設廠","擴"]
print("\n=== 其中涉不動產/資產者 ===")
for d in out:
    s = str(d.get("SUBJECT",""))+str(d.get("AN_NAME",""))
    if any(k in s for k in KEY):
        print(f"{d.get('CDATE')} | {s[:140]}")
        print(f"   {d.get('HYPERLINK')}")
