"""Write the five journals' rosters to data/boards/<journal>_roster.csv in one common format.

Usage: python3 scripts/make_rosters.py <pasted_dir> <amj_parsed_csv>
  pasted_dir: folder with smj.txt (raw page text), orgsci_editors.txt, asq.txt, mnsc.txt (pipe-delimited)
  amj_parsed_csv: AMJ roster parsed from the AOM editorial-team pages
The Organization Science Editorial Review Board comes from data/input/erb_list.csv.
"""
import csv, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTED, AMJ = sys.argv[1], sys.argv[2]
COLS = ['journal', 'role', 'department', 'name', 'affiliation_on_page', 'keywords_on_page', 'rank_on_page', 'source_url', 'retrieved']
SRC = {
    'AMJ': ('https://www.aom.org/publications/journals/journal/journal-editorial-team/', '2026-11-13'),
    'SMJ': ('https://sms.onlinelibrary.wiley.com/hub/journal/10970266/homepage/editorialboard.html', '2026-11-15 (page text supplied by user)'),
    'Organization Science': ('https://pubsonline.informs.org/page/orsc/editorial-board', '2026-11-15 (page text supplied by user)'),
    'ASQ': ('https://journals.sagepub.com/editorial-board/asq', '2026-11-15 (page text supplied by user)'),
    'Management Science': ('https://pubsonline.informs.org/page/mnsc/editorial-board', '2026-11-15 (page text supplied by user; page last updated 2026-11-13)'),
}
def row(journal, role, name, aff='', dept='', kw='', rank=''):
    url, when = SRC[journal]
    return {'journal': journal, 'role': role, 'department': dept, 'name': name.strip(), 'affiliation_on_page': aff.strip(),
            'keywords_on_page': kw.strip(), 'rank_on_page': rank.strip(), 'source_url': url, 'retrieved': when}
out = {}
# AMJ (already parsed from the AOM pages)
out['amj'] = [row('AMJ', r['role'], r['name'], r['affiliation'], rank=r.get('rank_on_page', '')) for r in csv.DictReader(open(AMJ, encoding='utf-8'))]
# SMJ (raw page text: role headings, then name / affiliation line pairs)
ROLE_MAP = {'CO-EDITORS': 'Co-Editor', 'ASSOCIATE EDITORS': 'Associate Editor', 'GUEST ASSOCIATE EDITORS': 'Guest Associate Editor',
            'SMS COLLECTIONS EDITOR': 'SMS Collections Editor', 'MEDIA CO-EDITORS': 'Media Co-Editor',
            'FOUNDING AND CONSULTING EDITOR': 'Founding and Consulting Editor', 'CONSULTING EDITORS': 'Consulting Editor',
            'EDITORIAL REVIEW BOARD': 'Editorial Review Board'}
smj, role, buf = [], None, []
for l in (x.strip() for x in open(os.path.join(PASTED, 'smj.txt'), encoding='utf-8')):
    if not l: continue
    if l in ROLE_MAP:
        assert not buf; role = ROLE_MAP[l]; continue
    buf.append(l)
    if len(buf) == 2:
        smj.append(row('SMJ', role, buf[0], buf[1])); buf = []
assert not buf
out['smj'] = smj
# Organization Science: editors (pipe-delimited, with keywords) + Editorial Review Board (the original 358-person list)
osc = []
for l in open(os.path.join(PASTED, 'orgsci_editors.txt'), encoding='utf-8'):
    if l.strip():
        role, name, aff, kw = (l.rstrip('\n').split('|') + [''])[:4]
        osc.append(row('Organization Science', role, name, aff, kw=kw))
for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'input', 'erb_list.csv'), encoding='utf-8')):
    osc.append(row('Organization Science', 'Editorial Review Board', r['name_listed'], r['institution_listed']))
out['orgsci'] = osc
# ASQ
out['asq'] = [row('ASQ', *(l.rstrip('\n').split('|')[:3])) for l in open(os.path.join(PASTED, 'asq.txt'), encoding='utf-8') if l.strip()]
# Management Science (Strategy, Organizations and Sustainability departments, plus the Editor-in-Chief)
mn = []
for l in open(os.path.join(PASTED, 'mnsc.txt'), encoding='utf-8'):
    if l.strip():
        role, name, aff, dept = (l.rstrip('\n').split('|') + [''])[:4]
        mn.append(row('Management Science', role, name, aff, dept=dept))
out['mnsc'] = mn
os.makedirs(os.path.join(ROOT, 'data', 'boards'), exist_ok=True)
for k, rows in out.items():
    with open(os.path.join(ROOT, 'data', 'boards', f'{k}_roster.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(rows)
    print(k, len(rows))
