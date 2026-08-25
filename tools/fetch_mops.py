# -*- coding: utf-8 -*-
"""抓 MOPS 重訊原文並轉純文字。用法: python _fetch_mops.py <SPOKE_DATE> <SPOKE_TIME> <COMPANY_ID> <SEQ_NO> <tag>"""
import sys, re, io, urllib.request

d, t, cid, seq, tag = sys.argv[1:6]
url = ("https://mopsov.twse.com.tw/mops/web/ajax_t05sr01_1?firstin=true&stp=1&step=1"
       "&SEQ_NO=%s&SPOKE_TIME=%s&SPOKE_DATE=%s&COMPANY_ID=%s" % (seq, t, d, cid))
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
html = re.sub(r"(?is)<script.*?</script>", "", html)
html = re.sub(r"(?is)<style.*?</style>", "", html)
html = re.sub(r"(?i)</(tr|div|p|table)>", "\n", html)
html = re.sub(r"(?i)</t[dh]>", " | ", html)
txt = re.sub(r"<[^>]+>", "", html)
txt = txt.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
txt = re.sub(r"[ \t]+", " ", txt)
txt = "\n".join(l.strip() for l in txt.split("\n") if l.strip())
p = r"C:\Claude\projects\demand-trace\tools\_orig_%s.txt" % tag
io.open(p, "w", encoding="utf-8").write(url + "\n\n" + txt)
print("saved", p, len(txt))
