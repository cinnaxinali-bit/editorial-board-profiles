"""Merge the five rosters into one list of unique people.

Writes data/people/people.csv (one row per person) and data/people/memberships.csv (one row per
journal role). Names are matched on a normalized first name (nicknames and leading initials
handled) plus surname; data/people/name_overrides.csv forces merges or splits found on review.
Usage: python3 scripts/match_people.py [--review]
"""
import csv, glob, os, re, sys, unicodedata
from collections import defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NICK = {'drew': 'andrew', 'andy': 'andrew', 'bala': 'balagopal', 'dk': 'david', 'raj': 'prithwiraj', 'joe': 'joseph',
        'jeff': 'jeffrey', 'trent': 'trenton', 'tim': 'timothy', 'katy': 'katherine', 'matt': 'matthew', 'mike': 'michael',
        'doug': 'douglas', 'steve': 'steven', 'stephen': 'steven', 'ben': 'benjamin', 'dan': 'daniel', 'chris': 'christopher',
        'alex': 'alexander', 'jen': 'jennifer', 'pri': 'priti', 'lindy': 'lindred', 'beth': 'elizabeth', 'liz': 'elizabeth',
        'tom': 'thomas', 'bob': 'robert', 'rob': 'robert', 'jim': 'james', 'cindy': 'cynthia', 'trish': 'patricia',
        'john-paul': 'jp', 'jean-paul': 'jp', 'shahzad': 'shaz'}
PARTICLES = {'de', 'di', 'da', 'del', 'della', 'van', 'der', 'den', 'ter', 'von', 'le', 'la', 'du', 'dos', 'das'}
DROP = {'jr', 'iii', 'ii', 'phd'}
def ascii_lower(s):
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
def name_key(name):
    s = ascii_lower(name)
    s = re.sub(r'\((on leave|asia-pacific)\)', ' ', s)
    s = re.sub(r'[“”"].*?[“”"]', ' ', s)          # quoted nicknames: Dejun "Tony" Kong
    s = re.sub(r'\(.*?\)', ' ', s)                  # (Sarah), (Ronnie), (Zapata)
    s = s.replace('.', '. ').replace(',', ' ')
    toks = [t.strip('.') for t in s.split() if t.strip('.')]
    toks = [t for k, t in enumerate(toks) if not (k > 0 and t in DROP)]   # 'Jr.' suffix, but keep 'JR' Keller
    if not toks: return None
    # leading initials: "J. Daniel Kim" -> daniel; "J. P. Eggers"/"JP" -> jp; "M. K. Chin"/"MK" -> mk
    i, inits = 0, ''
    while i < len(toks) - 1 and len(toks[i]) == 1:
        inits += toks[i]; i += 1
    first = toks[i] if i < len(toks) - 1 else ''
    if inits and (len(inits) >= 2 and (not first or i == len(toks) - 1)):
        first = inits
    elif inits and first:
        pass                                         # "J. Daniel Kim" -> first = daniel
    elif not first:
        first = inits
    rest = toks[i + 1:] if first != inits or i < len(toks) - 1 else toks[i:]
    if first == inits and inits:
        rest = toks[i:]
    if not rest: return None
    last = rest[-1]
    j = len(rest) - 2
    while j >= 0 and rest[j] in PARTICLES:
        last = rest[j] + last; j -= 1
    first = NICK.get(first, first)
    return first, last.replace('-', '')
def load():
    rows = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'data', 'boards', '*_roster.csv'))):
        rows += list(csv.DictReader(open(f, encoding='utf-8')))
    erb = {r['name_listed']: int(r['id']) for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'input', 'erb_list.csv'), encoding='utf-8'))}
    return rows, erb
def main(review=False):
    rows, erb = load()
    ov_path = os.path.join(ROOT, 'data', 'people', 'name_overrides.csv')
    force = {}
    if os.path.exists(ov_path):
        for r in csv.DictReader(open(ov_path, encoding='utf-8')):
            force[(r['journal'], r['name'])] = r['person_key']
    groups = defaultdict(list)
    for r in rows:
        k = force.get((r['journal'], r['name'])) or '|'.join(name_key(r['name']))
        groups[k].append(r)
    # stable person ids: the 358 Organization Science ERB members keep P0001-P0358 (their list id)
    people, next_id = [], 359
    def sort_key(item):
        k, rs = item
        ids = [erb[r['name']] for r in rs if r['journal'] == 'Organization Science' and r['role'] == 'Editorial Review Board' and r['name'] in erb]
        return (0, min(ids)) if ids else (1, k)
    for k, rs in sorted(groups.items(), key=sort_key):
        ids = sorted({erb[r['name']] for r in rs if r['journal'] == 'Organization Science' and r['role'] == 'Editorial Review Board' and r['name'] in erb})
        assert len(ids) <= 1, (k, ids)
        if ids: pid = f'P{ids[0]:04d}'
        else: pid = f'P{next_id:04d}'; next_id += 1
        people.append((pid, k, ids[0] if ids else '', rs))
    os.makedirs(os.path.join(ROOT, 'data', 'people'), exist_ok=True)
    with open(os.path.join(ROOT, 'data', 'people', 'people.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['person_id', 'display_name', 'orgsci_erb_id', 'n_roles', 'journals', 'roles', 'names_on_pages', 'affiliations_on_pages', 'keywords_on_pages'])
        for pid, k, eid, rs in sorted(people):
            names = sorted({r['name'] for r in rs}, key=len, reverse=True)
            w.writerow([pid, names[0], eid, len(rs), '; '.join(sorted({r['journal'] for r in rs})),
                        '; '.join(f"{r['journal']}: {r['role']}{' (' + r['department'] + ')' if r['department'] else ''}" for r in rs),
                        ' / '.join(names), ' / '.join(sorted({r['affiliation_on_page'] for r in rs if r['affiliation_on_page']})),
                        ' | '.join(sorted({r['keywords_on_page'] for r in rs if r['keywords_on_page']}))])
    with open(os.path.join(ROOT, 'data', 'people', 'memberships.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['person_id', 'journal', 'role', 'department', 'name_on_page', 'affiliation_on_page'])
        for pid, k, eid, rs in sorted(people):
            for r in rs:
                w.writerow([pid, r['journal'], r['role'], r['department'], r['name'], r['affiliation_on_page']])
    print(f'{len(rows)} role entries -> {len(people)} people ({sum(1 for p in people if p[2])} already profiled from the Organization Science ERB)')
    if review:
        bylast = defaultdict(list)
        for pid, k, eid, rs in people:
            first, last = k.split('|')
            bylast[last].append((pid, first, rs))
        print('\n== same surname, compatible first initial, NOT merged (check: same person?)')
        for last, ps in sorted(bylast.items()):
            for a in range(len(ps)):
                for b in range(a + 1, len(ps)):
                    fa, fb = ps[a][1], ps[b][1]
                    if fa[0] == fb[0]:
                        print(f"  {last}: [{ps[a][0]}] {ps[a][2][0]['name']} ({ps[a][2][0]['affiliation_on_page']}) <> [{ps[b][0]}] {ps[b][2][0]['name']} ({ps[b][2][0]['affiliation_on_page']})")
        print('\n== possible missed merges: first name of one appears in the other name, or hyphenated-surname part')
        allp = [(pid, k.split('|')[0], k.split('|')[1], rs) for pid, k, eid, rs in people]
        toks = {pid: set(re.findall(r'[a-z]+', ascii_lower(' '.join(r['name'] for r in rs)))) for pid, f, l, rs in allp}
        for x in range(len(allp)):
            for y in range(x + 1, len(allp)):
                a, b = allp[x], allp[y]
                same_last = a[2] == b[2]
                part_last = a[1] == b[1] and (a[2] in b[2] or b[2] in a[2]) and a[2] != b[2] and min(len(a[2]), len(b[2])) >= 4
                if (same_last and a[1] != b[1] and (a[1] in toks[b[0]] or b[1] in toks[a[0]])) or part_last:
                    print(f"  [{a[0]}] {a[3][0]['name']} ({a[3][0]['affiliation_on_page']}) <> [{b[0]}] {b[3][0]['name']} ({b[3][0]['affiliation_on_page']})")
        print('\n== merged across pages with different affiliations (check: same person?)')
        for pid, k, eid, rs in people:
            affs = {re.sub(r'[^a-z]', '', ascii_lower(r['affiliation_on_page']))[:14] for r in rs if r['affiliation_on_page']}
            if len(affs) > 1:
                print(f"  [{pid}] " + ' | '.join(sorted({f"{r['name']} @ {r['affiliation_on_page']}" for r in rs})))
if __name__ == '__main__':
    main('--review' in sys.argv)
