import sys, zipfile, re
import xml.etree.ElementTree as ET
NS='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
RNS='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
z=zipfile.ZipFile(sys.argv[1])
# shared strings
ss=[]
if 'xl/sharedStrings.xml' in z.namelist():
    r=ET.fromstring(z.read('xl/sharedStrings.xml'))
    for si in r.findall(NS+'si'):
        ss.append(''.join(t.text or '' for t in si.iter(NS+'t')))
wb=ET.fromstring(z.read('xl/workbook.xml'))
rels=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
rmap={rel.get('Id'):rel.get('Target') for rel in rels}
def colnum(ref):
    m=re.match(r'([A-Z]+)',ref); n=0
    for ch in m.group(1): n=n*26+ord(ch)-64
    return n-1
out={}
for sh in wb.find(NS+'sheets'):
    name=sh.get('name'); rid=sh.get(RNS+'id')
    tgt=rmap[rid]
    path='xl/'+tgt if not tgt.startswith('/') else tgt[1:]
    ws=ET.fromstring(z.read(path))
    rows=[]
    for row in ws.iter(NS+'row'):
        cells={}
        for c in row.findall(NS+'c'):
            ref=c.get('r'); t=c.get('t'); v=c.find(NS+'v'); isx=c.find(NS+'is')
            if t=='s' and v is not None: val=ss[int(v.text)]
            elif t=='inlineStr' and isx is not None: val=''.join(x.text or '' for x in isx.iter(NS+'t'))
            elif v is not None: val=v.text
            else: val=''
            cells[colnum(ref)]=val or ''
        if cells:
            w=max(cells)+1
            rows.append([cells.get(i,'') for i in range(w)])
    out[name]=rows
import json
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False)
for k,v in out.items(): print(k, len(v))
