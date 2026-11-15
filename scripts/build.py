"""Merge the research records and build output/ERB_Scholar_Profiles.xlsx and .csv.

Usage: python3 scripts/build.py [project_root]
"""
import json, glob, os, re, sys, csv, math
from collections import Counter
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

ROOT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

master = []
with open(os.path.join(ROOT, 'data', 'input', 'erb_list.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        master.append((int(row['id']), row['name_listed'], row['institution_listed']))
master.sort()
recs = {}
for f in sorted(glob.glob(os.path.join(ROOT, 'data', 'research', 'first_pass', '*.json'))):
    for r in json.load(open(f, encoding='utf-8')):
        recs[int(r['id'])] = r
for f in sorted(glob.glob(os.path.join(ROOT, 'data', 'research', 'corrections', '*.json'))):  # verified corrections override, in filename order
    for r in json.load(open(f, encoding='utf-8')):
        base = recs.get(int(r['id']), {})
        base.update({k: v for k, v in r.items()})
        recs[int(r['id'])] = base

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from profile_utils import norm_univ, canon_sub, INST_NORM, clean

COLS = [  # header, key/func, width, wrap
    ('#', lambda r, m: m[0], 5, False),
    ('Name', lambda r, m: clean(r.get('full_name')) or m[1], 22, False),
    ('Website (faculty page)', lambda r, m: clean(r.get('faculty_page_url')), 38, False),
    ('Personal website', lambda r, m: clean(r.get('personal_website_url')), 30, False),
    ('Institution (current)', lambda r, m: INST_NORM.get(clean(r.get('current_institution')), clean(r.get('current_institution'))), 28, True),
    ('School / department', lambda r, m: clean(r.get('school_unit')), 30, True),
    ('Position', lambda r, m: clean(r.get('rank')), 11, False),
    ('Exact title', lambda r, m: clean(r.get('title')), 34, True),
    ('Expertise / research topics', lambda r, m: clean(r.get('research_topics')), 50, True),
    ('PhD institution', lambda r, m: clean(r.get('phd_institution')), 30, True),
    ('PhD field', lambda r, m: clean(r.get('phd_field')), 22, True),
    ('PhD year', lambda r, m: clean(r.get('phd_year')), 8, False),
    ('Strategy & OT vs OB', lambda r, m: clean(r.get('area')), 14, False),
    ('Subfield', lambda r, m: canon_sub(clean(r.get('area')), clean(r.get('subfield'))), 26, True),
    ('Borderline call?', lambda r, m: 'Yes' if re.search(r'hybrid|borderline|judgment call|could reasonably', clean(r.get('area_rationale')) + ' ' + clean(r.get('notes')), re.I) else '', 10, False),
    ('Classification rationale', lambda r, m: clean(r.get('area_rationale')), 44, True),
    ('Subfield (detail)', lambda r, m: clean(r.get('subfield')), 28, True),
    ('Institution as listed on ERB', lambda r, m: m[2] or '(not given)', 26, True),
    ('Moved since list?', lambda r, m: clean(r.get('moved')), 9, False),
    ('Position note', lambda r, m: clean(r.get('rank_detail')), 34, True),
    ('CV link', lambda r, m: clean(r.get('cv_url')), 30, False),
    ('Confidence', lambda r, m: clean(r.get('confidence')), 10, False),
    ('Notes', lambda r, m: clean(r.get('notes')), 44, True),
    ('Sources', lambda r, m: clean(r.get('sources')), 50, False),
    ('PhD university (normalized)', lambda r, m: norm_univ(r.get('phd_institution')), 26, False),
]
HDR = {h: i + 1 for i, (h, *_ ) in enumerate(COLS)}
URL_COLS = {'Website (faculty page)', 'Personal website', 'CV link'}

FONT = Font(name='Arial', size=10)
LINK = Font(name='Arial', size=10, color='0563C1', underline='single')
BOLD = Font(name='Arial', size=10, bold=True)
HFONT = Font(name='Arial', size=10, bold=True, color='FFFFFF')
HFILL = PatternFill('solid', fgColor='1F3864')
FILL_S = PatternFill('solid', fgColor='DDEBF7')
FILL_O = PatternFill('solid', fgColor='FCE4D6')
FILL_LOW = PatternFill('solid', fgColor='FFF2CC')
THIN = Side(style='thin', color='BFBFBF')

wb = Workbook()
ws = wb.active
ws.title = 'Scholars'
for c, (h, _, w, _) in enumerate(COLS, 1):
    cell = ws.cell(row=1, column=c, value=h)
    cell.font, cell.fill = HFONT, HFILL
    cell.alignment = Alignment(wrap_text=True, vertical='center')
    ws.column_dimensions[get_column_letter(c)].width = w
ws.row_dimensions[1].height = 30

rows_out = []
for ridx, m in enumerate(master, 2):
    r = recs.get(m[0], {})
    vals = [fn(r, m) for _, fn, _, _ in COLS]
    rows_out.append(vals)
    max_lines = 1
    for c, ((h, _, w, wrap), v) in enumerate(zip(COLS, vals), 1):
        if h == 'Sources' and v: v = v.replace('\n', ' | ')
        if h in ('#',) : cell = ws.cell(row=ridx, column=c, value=int(v))
        else: cell = ws.cell(row=ridx, column=c, value=v)
        cell.font = FONT
        cell.alignment = Alignment(wrap_text=wrap, vertical='top')
        cell.border = Border(bottom=THIN)
        if h in URL_COLS and v.startswith('http'):
            cell.hyperlink = v
            cell.font = LINK
        if h == 'Name': cell.font = BOLD
        if h == 'Strategy & OT vs OB':
            if v == 'OB': cell.fill = FILL_O
            elif v: cell.fill = FILL_S
        if h == 'Confidence' and v.lower() == 'low': cell.fill = FILL_LOW
        if wrap and v:
            max_lines = max(max_lines, sum(math.ceil(max(len(p), 1) / (w * 1.15)) for p in v.split('\n')))
    ws.row_dimensions[ridx].height = 13.5 * min(max_lines, 4) + 2
last = len(master) + 1
ws.freeze_panes = 'C2'
ws.auto_filter.ref = f'A1:{get_column_letter(len(COLS))}{last}'

# ---- Summary sheet (formulas) ----
S = wb.create_sheet('Summary')
L = lambda h: get_column_letter(HDR[h])
rng = lambda h: f"Scholars!${L(h)}$2:${L(h)}${last}"
S.column_dimensions['A'].width = 38
for col in 'BCDEFG': S.column_dimensions[col].width = 13
def hdr(row, labels):
    for c, t in enumerate(labels, 1):
        x = S.cell(row=row, column=c, value=t); x.font, x.fill = HFONT, HFILL
        x.alignment = Alignment(horizontal='center' if c > 1 else 'left')
r0 = 1
S.cell(row=r0, column=1, value='Editorial Review Board: counts by area and position').font = Font(name='Arial', size=12, bold=True)
hdr(r0 + 1, ['Area', 'Assistant', 'Associate', 'Full', 'Other', 'Total', '% of board'])
areas = ['Strategy & OT', 'OB']
for k, a in enumerate(areas):
    rr = r0 + 2 + k
    S.cell(row=rr, column=1, value=a).font = BOLD
    for c, rk in enumerate(['Assistant', 'Associate', 'Full', 'Other'], 2):
        S.cell(row=rr, column=c, value=f'=COUNTIFS({rng("Strategy & OT vs OB")},$A{rr},{rng("Position")},"{rk}")')
    S.cell(row=rr, column=6, value=f'=SUM(B{rr}:E{rr})')
tr = r0 + 2 + len(areas)
S.cell(row=tr, column=1, value='Total').font = BOLD
for c in range(2, 7):
    cl = get_column_letter(c)
    S.cell(row=tr, column=c, value=f'=SUM({cl}{r0+2}:{cl}{tr-1})').font = BOLD
for rr in range(r0 + 2, tr + 1):
    S.cell(row=rr, column=7, value=f'=IF($F${tr}=0,0,F{rr}/$F${tr})').number_format = '0.0%'
S.cell(row=tr + 1, column=1, value=f'Check: rows in Scholars sheet').font = Font(name='Arial', size=9, italic=True, color='808080')
S.cell(row=tr + 1, column=6, value=f'=COUNTA(Scholars!$B$2:$B${last})').font = Font(name='Arial', size=9, italic=True, color='808080')

# subfields
r1 = tr + 3
S.cell(row=r1, column=1, value='Subfields (standardized)').font = Font(name='Arial', size=12, bold=True)
hdr(r1 + 1, ['Subfield', 'Count'])
sub_counts = Counter(v[HDR['Subfield'] - 1] for v in rows_out if v[HDR['Subfield'] - 1])
for k, (sname, _) in enumerate(sorted(sub_counts.items(), key=lambda x: (-x[1], x[0]))):
    rr = r1 + 2 + k
    S.cell(row=rr, column=1, value=sname)
    S.cell(row=rr, column=2, value=f'=COUNTIF({rng("Subfield")},$A{rr})')
r2 = r1 + 2 + len(sub_counts) + 1
S.cell(row=r2, column=1, value='PhD universities (normalized; 3+ board members)').font = Font(name='Arial', size=12, bold=True)
hdr(r2 + 1, ['PhD university', 'Strategy & OT', 'OB', 'Total'])
pu = Counter(v[HDR['PhD university (normalized)'] - 1] for v in rows_out if v[HDR['PhD university (normalized)'] - 1])
top = [(u, n) for u, n in sorted(pu.items(), key=lambda x: (-x[1], x[0])) if n >= 3]
for k, (u, _) in enumerate(top):
    rr = r2 + 2 + k
    S.cell(row=rr, column=1, value=u)
    S.cell(row=rr, column=2, value=f'=COUNTIFS({rng("PhD university (normalized)")},$A{rr},{rng("Strategy & OT vs OB")},B${r2+1})')
    S.cell(row=rr, column=3, value=f'=COUNTIFS({rng("PhD university (normalized)")},$A{rr},{rng("Strategy & OT vs OB")},C${r2+1})')
    S.cell(row=rr, column=4, value=f'=SUM(B{rr}:C{rr})')
r3 = r2 + 2 + len(top) + 1
S.cell(row=r3, column=1, value='Data quality').font = Font(name='Arial', size=12, bold=True)
hdr(r3 + 1, ['Measure', 'Count'])
dq = [('Moved since the list was published', f'=COUNTIF({rng("Moved since list?")},"Yes")'),
      ('High-confidence records', f'=COUNTIF({rng("Confidence")},"high")'),
      ('Medium-confidence records', f'=COUNTIF({rng("Confidence")},"medium")'),
      ('Low-confidence records (yellow in Scholars sheet)', f'=COUNTIF({rng("Confidence")},"low")'),
      ('Records with a personal website', f'=COUNTIF({rng("Personal website")},"http*")'),
      ('Records missing PhD institution', f'=COUNTBLANK({rng("PhD institution")})')]
for k, (lab, fml) in enumerate(dq):
    S.cell(row=r3 + 2 + k, column=1, value=lab)
    S.cell(row=r3 + 2 + k, column=2, value=fml)
for row in S.iter_rows():
    for x in row:
        if x.font == Font() or x.font.name != 'Arial':
            x.font = Font(name='Arial', size=10, bold=x.font.bold, color=x.font.color)
S.freeze_panes = 'A2'

# ---- Read me ----
R = wb.create_sheet('Read me')
R.column_dimensions['A'].width = 120
notes = open(os.path.join(ROOT, 'docs', 'workbook_readme.txt'), encoding='utf-8').read().split('\n')
for k, line in enumerate(notes, 1):
    x = R.cell(row=k, column=1, value=line)
    x.font = Font(name='Arial', size=12 if k == 1 else 10, bold=(k == 1 or line.endswith(':')))
    x.alignment = Alignment(wrap_text=True, vertical='top')
OUT_XLSX = os.path.join(ROOT, 'output', 'ERB_Scholar_Profiles.xlsx')
OUT_CSV = os.path.join(ROOT, 'output', 'ERB_Scholar_Profiles.csv')
wb.save(OUT_XLSX)

with open(OUT_CSV, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow([h for h, *_ in COLS])
    for v in rows_out:
        w.writerow([x.replace('\n', ' | ') if isinstance(x, str) else x for x in v])
print('rows', len(rows_out), 'records found', sum(1 for m in master if m[0] in recs))
