"""Validate the research records against the input list and report gaps.

Usage: python3 scripts/check.py [project_root]
"""
import json, glob, os, sys, csv
ROOT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
master = {}
with open(os.path.join(ROOT, 'data', 'input', 'erb_list.csv'), encoding='utf-8') as fh:
    for row in csv.DictReader(fh):
        master[int(row['id'])] = (row['name_listed'], row['institution_listed'], 'erb_list.csv')
KEYS = ["id","name_listed","institution_listed","full_name","current_institution","school_unit","moved",
        "title","rank","rank_detail","faculty_page_url","personal_website_url","cv_url","research_topics",
        "phd_institution","phd_field","phd_year","area","subfield","area_rationale","confidence","sources","notes"]
recs = {}
for f in sorted(glob.glob(os.path.join(ROOT, 'data', 'research', 'first_pass', '*.json'))):
    try:
        data = json.load(open(f, encoding='utf-8'))
    except Exception as e:
        print(f'PARSE ERROR {f}: {e}'); continue
    for r in data:
        recs[int(r['id'])] = r
        missing = [k for k in KEYS if k not in r]
        if missing: print(f"{os.path.basename(f)} id={r['id']} missing keys {missing}")
for f in sorted(glob.glob(os.path.join(ROOT, 'data', 'research', 'corrections', '*.json'))):
    for r in json.load(open(f, encoding='utf-8')):
        recs.setdefault(int(r['id']), {}).update(r)
print(f'records: {len(recs)} / {len(master)}')
gaps = {'faculty_page_url':0,'phd_institution':0,'title':0,'research_topics':0}
for i,(name,inst,b) in master.items():
    r = recs.get(i)
    if r is None: continue
    if r.get('name_listed','').strip() != name: print(f'NAME MISMATCH id={i}: {name!r} vs {r.get("name_listed")!r}')
    if r.get('rank') not in ('Assistant','Associate','Full','Other'): print(f'BAD RANK id={i} {name}: {r.get("rank")!r}')
    if r.get('area') not in ('Strategy & OT','OB'): print(f'BAD AREA id={i} {name}: {r.get("area")!r}')
    for k in gaps:
        if not str(r.get(k,'')).strip(): gaps[k]+=1; print(f'EMPTY {k}: id={i} {name}')
    if r.get('confidence') == 'low': print(f'LOW CONF id={i} {name}: {r.get("notes","")[:160]}')
print('gap counts:', gaps)
missing_ids = [i for i in master if i not in recs]
print('missing ids:', missing_ids if len(missing_ids) < 60 else f'{len(missing_ids)} ids')
