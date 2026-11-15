"""Build output/Editorial_Boards_Profiles.xlsx (and CSVs) covering all five journals' editorial boards.

Combines the cross-journal people list (data/people/), the original Organization Science ERB profiles
(data/research/first_pass + corrections, ids 1-358 = person ids P0001-P0358) and the profiles of
everyone else (data/research/boards_pass + boards_corrections, keyed by person_id).
Usage: python3 scripts/build_boards.py [project_root]
"""
import csv, glob, json, math, os, re, sys
from collections import Counter, defaultdict
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from profile_utils import INST_NORM, canon_sub, clean, norm_univ

ROOT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda *p: os.path.join(ROOT, *p)
JOURNALS = ['SMJ', 'Organization Science', 'ASQ', 'AMJ', 'Management Science']
GROUP = {
    'Editor-in-Chief': 'Editor', 'Editor': 'Editor', 'Co-Editor': 'Editor', 'Deputy Editor': 'Editor', 'Department Editor': 'Editor',
    'Senior Editor': 'Associate / Senior Editor', 'Associate Editor': 'Associate / Senior Editor', 'Guest Associate Editor': 'Associate / Senior Editor',
    'Editorial Review Board': 'Review board', 'Editorial Board': 'Review board',
}
GROUP_ORDER = ['Editor', 'Associate / Senior Editor', 'Review board', 'Other editorial role']
group_of = lambda role: GROUP.get(role, 'Other editorial role')

# ---- load ----
people = list(csv.DictReader(open(J('data', 'people', 'people.csv'), encoding='utf-8')))
members = list(csv.DictReader(open(J('data', 'people', 'memberships.csv'), encoding='utf-8')))
recs = {}
for f in sorted(glob.glob(J('data', 'research', 'first_pass', '*.json'))):
    for r in json.load(open(f, encoding='utf-8')):
        recs[f"P{int(r['id']):04d}"] = r
for f in sorted(glob.glob(J('data', 'research', 'corrections', '*.json'))):
    for r in json.load(open(f, encoding='utf-8')):
        recs.setdefault(f"P{int(r['id']):04d}", {}).update(r)
for f in sorted(glob.glob(J('data', 'research', 'boards_pass', '*.json'))):
    for r in json.load(open(f, encoding='utf-8')):
        recs[r['person_id']] = r
for f in sorted(glob.glob(J('data', 'research', 'boards_corrections', '*.json'))):
    for r in json.load(open(f, encoding='utf-8')):
        recs.setdefault(r['person_id'], {}).update(r)
roles_by = defaultdict(list)
for m in members:
    roles_by[m['person_id']].append(m)

def role_cell(pid, journal):
    out = []
    for m in roles_by[pid]:
        if m['journal'] == journal:
            label = m['role'] + (f" ({m['department']})" if m['department'] else '')
            if label not in out: out.append(label)
    return '; '.join(out)
def top_group(pid):
    gs = {group_of(m['role']) for m in roles_by[pid]}
    return next((g for g in GROUP_ORDER if g in gs), '')
def borderline(r):
    return 'Yes' if re.search(r'hybrid|borderline|judgment call|could reasonably', clean(r.get('area_rationale')) + ' ' + clean(r.get('notes')), re.I) else ''

PCOLS = [  # header, function(person_row, record) -> value, width, wrap
    ('#', None, 6, False),
    ('Person ID', lambda p, r: p['person_id'], 9, False),
    ('Name', lambda p, r: clean(r.get('full_name')) or p['display_name'], 22, False),
    ('Website (faculty page)', lambda p, r: clean(r.get('faculty_page_url')), 36, False),
    ('Personal website', lambda p, r: clean(r.get('personal_website_url')), 28, False),
    ('Institution (current)', lambda p, r: INST_NORM.get(clean(r.get('current_institution')), clean(r.get('current_institution'))), 26, True),
    ('School / department', lambda p, r: clean(r.get('school_unit')), 28, True),
    ('Position', lambda p, r: clean(r.get('rank')), 11, False),
    ('Exact title', lambda p, r: clean(r.get('title')), 32, True),
    ('Expertise / research topics', lambda p, r: clean(r.get('research_topics')), 46, True),
    ('PhD institution', lambda p, r: clean(r.get('phd_institution')), 28, True),
    ('PhD field', lambda p, r: clean(r.get('phd_field')), 20, True),
    ('PhD year', lambda p, r: clean(r.get('phd_year')), 8, False),
    ('Strategy & OT vs OB', lambda p, r: clean(r.get('area')), 14, False),
    ('Subfield', lambda p, r: canon_sub(clean(r.get('area')), clean(r.get('subfield'))), 26, True),
    ('Borderline call?', lambda p, r: borderline(r), 10, False),
] + [(j, (lambda jj: (lambda p, r: role_cell(p['person_id'], jj)))(j), 20, True) for j in JOURNALS] + [
    ('Boards (count)', lambda p, r: len({m['journal'] for m in roles_by[p['person_id']]}), 8, False),
    ('Highest role', lambda p, r: top_group(p['person_id']), 16, False),
    ('Classification rationale', lambda p, r: clean(r.get('area_rationale')), 40, True),
    ('Subfield (detail)', lambda p, r: clean(r.get('subfield')), 26, True),
    ('Affiliation(s) on board pages', lambda p, r: p['affiliations_on_pages'], 30, True),
    ('Moved since listing?', lambda p, r: clean(r.get('moved')), 9, False),
    ('Position note', lambda p, r: clean(r.get('rank_detail')), 32, True),
    ('CV link', lambda p, r: clean(r.get('cv_url')), 28, False),
    ('Confidence', lambda p, r: clean(r.get('confidence')) or 'not yet researched', 10, False),
    ('Notes', lambda p, r: clean(r.get('notes')), 40, True),
    ('Sources', lambda p, r: clean(r.get('sources')).replace('\n', ' | '), 46, False),
    ('PhD university (normalized)', lambda p, r: norm_univ(r.get('phd_institution')), 24, False),
]
PH = {h: i + 1 for i, (h, *_) in enumerate(PCOLS)}
RCOLS = [('Journal', 18), ('Role', 24), ('Role group', 22), ('Department', 14), ('Name on board page', 24), ('Affiliation on board page', 30),
         ('Person ID', 9), ('Name', 22), ('Institution (current)', 26), ('Position', 11), ('Strategy & OT vs OB', 14), ('Subfield', 26), ('Website (faculty page)', 36)]
RH = {h: i + 1 for i, (h, _) in enumerate(RCOLS)}
URL_COLS = {'Website (faculty page)', 'Personal website', 'CV link'}

FONT = Font(name='Arial', size=10)
LINK = Font(name='Arial', size=10, color='0563C1', underline='single')
BOLD = Font(name='Arial', size=10, bold=True)
HFONT = Font(name='Arial', size=10, bold=True, color='FFFFFF')
HFILL = PatternFill('solid', fgColor='1F3864')
FILLS = {'Strategy & OT': PatternFill('solid', fgColor='DDEBF7'), 'OB': PatternFill('solid', fgColor='FCE4D6'), 'Other': PatternFill('solid', fgColor='E2EFDA')}
FILL_LOW = PatternFill('solid', fgColor='FFF2CC')
THIN = Side(style='thin', color='BFBFBF')

def header(ws, cols):
    for c, (h, *rest) in enumerate(cols, 1):
        x = ws.cell(row=1, column=c, value=h)
        x.font, x.fill = HFONT, HFILL
        x.alignment = Alignment(wrap_text=True, vertical='center')
        ws.column_dimensions[get_column_letter(c)].width = rest[-2] if len(rest) >= 2 else rest[0]
    ws.row_dimensions[1].height = 30

wb = Workbook()
# ---- People ----
ws = wb.active
ws.title = 'People'
header(ws, [(h, w, wr) for h, _, w, wr in PCOLS])
people.sort(key=lambda p: (GROUP_ORDER.index(top_group(p['person_id'])) if top_group(p['person_id']) else 9, (clean(recs.get(p['person_id'], {}).get('full_name')) or p['display_name']).split()[-1].lower()))
people_out = []
for i, p in enumerate(people, 1):
    r = recs.get(p['person_id'], {})
    vals = [i] + [fn(p, r) for h, fn, _, _ in PCOLS[1:]]
    people_out.append(vals)
    lines = 1
    for c, ((h, _, w, wrap), v) in enumerate(zip(PCOLS, vals), 1):
        cell = ws.cell(row=i + 1, column=c, value=v)
        cell.font = FONT
        cell.alignment = Alignment(wrap_text=wrap, vertical='top')
        cell.border = Border(bottom=THIN)
        if h in URL_COLS and isinstance(v, str) and v.startswith('http'):
            cell.hyperlink, cell.font = v, LINK
        if h == 'Name': cell.font = BOLD
        if h == 'Strategy & OT vs OB' and v in FILLS: cell.fill = FILLS[v]
        if h == 'Confidence' and v in ('low', 'not yet researched'): cell.fill = FILL_LOW
        if wrap and isinstance(v, str) and v:
            lines = max(lines, sum(math.ceil(max(len(x), 1) / (w * 1.15)) for x in v.split('\n')))
    ws.row_dimensions[i + 1].height = 13.5 * min(lines, 4) + 2
plast = len(people) + 1
ws.freeze_panes = 'D2'
ws.auto_filter.ref = f'A1:{get_column_letter(len(PCOLS))}{plast}'

# ---- Board roles ----
RS = wb.create_sheet('Board roles')
header(RS, [(h, w) for h, w in RCOLS])
pidx = {p['person_id']: (recs.get(p['person_id'], {}), p) for p in people}
jorder = {j: k for k, j in enumerate(JOURNALS)}
members.sort(key=lambda m: (jorder[m['journal']], GROUP_ORDER.index(group_of(m['role'])), m['role'], m['department'], m['name_on_page'].split()[-1].lower()))
roles_out = []
for i, m in enumerate(members, 2):
    r, p = pidx[m['person_id']]
    area = clean(r.get('area'))
    vals = [m['journal'], m['role'], group_of(m['role']), m['department'], m['name_on_page'], m['affiliation_on_page'], m['person_id'],
            clean(r.get('full_name')) or p['display_name'], INST_NORM.get(clean(r.get('current_institution')), clean(r.get('current_institution'))),
            clean(r.get('rank')), area, canon_sub(area, clean(r.get('subfield'))), clean(r.get('faculty_page_url'))]
    roles_out.append(vals)
    for c, v in enumerate(vals, 1):
        cell = RS.cell(row=i, column=c, value=v)
        cell.font = FONT
        cell.border = Border(bottom=THIN)
        if c == RH['Website (faculty page)'] and v.startswith('http'):
            cell.hyperlink, cell.font = v, LINK
        if c == RH['Strategy & OT vs OB'] and v in FILLS: cell.fill = FILLS[v]
rlast = len(members) + 1
RS.freeze_panes = 'C2'
RS.auto_filter.ref = f'A1:{get_column_letter(len(RCOLS))}{rlast}'

# ---- Summary (formulas) ----
S = wb.create_sheet('Summary')
S.column_dimensions['A'].width = 34
for col in 'BCDEFGH': S.column_dimensions[col].width = 15
rr = lambda h: f"'Board roles'!${get_column_letter(RH[h])}$2:${get_column_letter(RH[h])}${rlast}"
pr = lambda h: f"People!${get_column_letter(PH[h])}$2:${get_column_letter(PH[h])}${plast}"
TITLE = Font(name='Arial', size=12, bold=True)
def hrow(row, labels):
    for c, t in enumerate(labels, 1):
        x = S.cell(row=row, column=c, value=t); x.font, x.fill = HFONT, HFILL
        x.alignment = Alignment(horizontal='left' if c == 1 else 'center', wrap_text=True)
    S.row_dimensions[row].height = 30
def table(r0, title, row_labels, col_labels, formula):
    S.cell(row=r0, column=1, value=title).font = TITLE
    hrow(r0 + 1, [''] + col_labels + ['Total'])
    for k, lab in enumerate(row_labels):
        r = r0 + 2 + k
        S.cell(row=r, column=1, value=lab).font = BOLD
        for c, cl in enumerate(col_labels, 2):
            S.cell(row=r, column=c, value=formula(lab, cl, r, c)).font = FONT
        S.cell(row=r, column=len(col_labels) + 2, value=f'=SUM(B{r}:{get_column_letter(len(col_labels) + 1)}{r})').font = BOLD
    tr = r0 + 2 + len(row_labels)
    S.cell(row=tr, column=1, value='Total').font = BOLD
    for c in range(2, len(col_labels) + 3):
        cl = get_column_letter(c)
        S.cell(row=tr, column=c, value=f'=SUM({cl}{r0 + 2}:{cl}{tr - 1})').font = BOLD
    return tr + 2
r = 1
r = table(r, 'Board seats by journal and role (one count per role held)', JOURNALS, GROUP_ORDER,
          lambda lab, cl, rw, c: f'=COUNTIFS({rr("Journal")},"{lab}",{rr("Role group")},"{cl}")')
AREAS = ['Strategy & OT', 'OB', 'Other']
r = table(r, 'Board seats by journal and area', JOURNALS, AREAS,
          lambda lab, cl, rw, c: f'=COUNTIFS({rr("Journal")},"{lab}",{rr("Strategy & OT vs OB")},"{cl}")')
r = table(r, 'Editors and associate/senior editors by journal and area', JOURNALS, AREAS,
          lambda lab, cl, rw, c: f'=COUNTIFS({rr("Journal")},"{lab}",{rr("Strategy & OT vs OB")},"{cl}",{rr("Role group")},"Editor")+COUNTIFS({rr("Journal")},"{lab}",{rr("Strategy & OT vs OB")},"{cl}",{rr("Role group")},"Associate / Senior Editor")')
r = table(r, 'People (unique) by area and position', AREAS, ['Assistant', 'Associate', 'Full', 'Other'],
          lambda lab, cl, rw, c: f'=COUNTIFS({pr("Strategy & OT vs OB")},"{lab}",{pr("Position")},"{cl}")')
r = table(r, 'People (unique) by number of these boards they sit on', ['1', '2', '3', '4', '5'], AREAS,
          lambda lab, cl, rw, c: f'=COUNTIFS({pr("Boards (count)")},{lab},{pr("Strategy & OT vs OB")},"{cl}")')
S.cell(row=r, column=1, value='Data quality').font = TITLE
hrow(r + 1, ['Measure', 'Count'])
dq = [('People in the workbook', f'=COUNTA({pr("Person ID")})'),
      ('High-confidence profiles', f'=COUNTIF({pr("Confidence")},"high")'),
      ('Medium-confidence profiles', f'=COUNTIF({pr("Confidence")},"medium")'),
      ('Low-confidence profiles', f'=COUNTIF({pr("Confidence")},"low")'),
      ('Not yet researched', f'=COUNTIF({pr("Confidence")},"not yet researched")'),
      ('Moved since a board page listed them', f'=COUNTIF({pr("Moved since listing?")},"Yes")'),
      ('Borderline area calls', f'=COUNTIF({pr("Borderline call?")},"Yes")')]
for k, (lab, fml) in enumerate(dq):
    S.cell(row=r + 2 + k, column=1, value=lab).font = FONT
    S.cell(row=r + 2 + k, column=2, value=fml).font = FONT
S.freeze_panes = 'A2'

# ---- Read me ----
R = wb.create_sheet('Read me')
R.column_dimensions['A'].width = 120
notes = open(J('docs', 'boards_workbook_readme.txt'), encoding='utf-8').read().split('\n')
for k, line in enumerate(notes, 1):
    x = R.cell(row=k, column=1, value=line)
    x.font = Font(name='Arial', size=12 if k == 1 else 10, bold=(k == 1 or line.endswith(':')))
    x.alignment = Alignment(wrap_text=True, vertical='top')

os.makedirs(J('output'), exist_ok=True)
wb.save(J('output', 'Editorial_Boards_Profiles.xlsx'))
with open(J('output', 'Editorial_Boards_People.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f); w.writerow([h for h, *_ in PCOLS])
    for v in people_out: w.writerow([x.replace('\n', ' | ') if isinstance(x, str) else x for x in v])
with open(J('output', 'Editorial_Boards_Roles.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f); w.writerow([h for h, _ in RCOLS]); w.writerows(roles_out)
done = sum(1 for p in people if recs.get(p['person_id'], {}).get('confidence'))
print(f'people {len(people)} (profiled {done}), board roles {len(members)}')
