"""Helpers shared by build.py and build_boards.py: name normalization and standardized labels."""
import re

ALIASES = [
    (r'^(massachusetts institute of technology|mit)\b', 'MIT'),
    (r'^(university of pennsylvania|wharton|the wharton school)\b', 'University of Pennsylvania'),
    (r'^(harvard|harvard university|harvard business school)\b', 'Harvard University'),
    (r'^stanford', 'Stanford University'),
    (r'^(columbia university|columbia business school)\b', 'Columbia University'),
    (r'^(university of california,? berkeley|uc berkeley)\b', 'UC Berkeley'),
    (r'^(university of california,? los angeles|ucla)\b', 'UCLA'),
    (r'^(new york university|nyu)\b', 'New York University'),
    (r'^(university of michigan)\b', 'University of Michigan'),
    (r'^(northwestern)', 'Northwestern University'),
    (r'^(carnegie mellon)', 'Carnegie Mellon University'),
    (r'^(university of north carolina|unc)\b', 'UNC Chapel Hill'),
    (r'^(university of texas at austin|ut austin|the university of texas at austin)\b', 'UT Austin'),
    (r'^(university of minnesota)', 'University of Minnesota'),
    (r'^(university of toronto)', 'University of Toronto'),
    (r'^(university of chicago)', 'University of Chicago'),
    (r'^(duke)', 'Duke University'),
    (r'^(cornell)', 'Cornell University'),
    (r'^(yale)', 'Yale University'),
    (r'^(insead)', 'INSEAD'),
    (r'^(london business school)', 'London Business School'),
    (r'^(bocconi|universit[aà] bocconi)', 'Bocconi University'),
    (r'^(university of southern california|usc)\b', 'USC'),
    (r'^(university of washington)\b', 'University of Washington'),
    (r'^(university of illinois)', 'University of Illinois Urbana-Champaign'),
    (r'^(university of maryland)', 'University of Maryland'),
    (r'^(university of wisconsin)', 'University of Wisconsin-Madison'),
    (r'^(university of virginia)', 'University of Virginia'),
    (r'^(washington university)', 'Washington University in St. Louis'),
    (r'^(boston university)', 'Boston University'),
    (r'^(arizona state)', 'Arizona State University'),
    (r'^(university of alberta)', 'University of Alberta'),
    (r'^(university of british columbia|ubc)\b', 'University of British Columbia'),
    (r'^(purdue)', 'Purdue University'),
    (r'^(penn(sylvania)? state|the pennsylvania state)', 'Penn State University'),
    (r'^(university of utah)', 'University of Utah'),
    (r'^(university of georgia)', 'University of Georgia'),
    (r'^(eth z)', 'ETH Zurich'),
    (r'^(hec paris)', 'HEC Paris'),
    (r'^(university of oxford|oxford)', 'University of Oxford'),
    (r'^(university of cambridge|cambridge)', 'University of Cambridge'),
    (r'^(copenhagen business school)', 'Copenhagen Business School'),
    (r'^(university of st\.? ?gallen)', 'University of St. Gallen'),
    (r'^(texas a&m)', 'Texas A&M University'),
    (r'^(indiana university)', 'Indiana University'),
    (r'^(emory)', 'Emory University'),
    (r'^(university of california,? irvine|uc irvine)\b', 'UC Irvine'),
    (r'^(university of california,? san diego|uc san diego|ucsd)\b', 'UC San Diego'),
    (r'^(georgia (institute of technology|tech))', 'Georgia Tech'),
    (r'^(brigham young)', 'Brigham Young University'),
    (r'^(university of colorado)', 'University of Colorado'),
    (r'^(university of florida)', 'University of Florida'),
    (r'^(ohio state|the ohio state)', 'Ohio State University'),
    (r'^(rice university)', 'Rice University'),
    (r'^(university of arizona|the university of arizona)', 'University of Arizona'),
    (r'^(university of groningen|groningen)', 'University of Groningen'),
    (r'^(erasmus)', 'Erasmus University Rotterdam'),
    (r'^(university of iowa)', 'University of Iowa'),
    (r'^(university of south carolina)', 'University of South Carolina'),
]
def norm_univ(s):
    s = (s or '').strip()
    if not s: return ''
    base = re.sub(r'\s*\(.*?\)\s*', ' ', s).strip().strip(',;')
    base = re.split(r'\s*[;/]\s*', base)[0].strip()
    low = base.lower()
    for pat, rep in ALIASES:
        if re.search(pat, low): return rep
    return base


S_RULES = [
    (r'information systems', 'Information systems'),
    (r'^work|occupations', 'Work, occupations & technology (qualitative)'),
    (r'labor market|careers & inequality', 'Labor markets, careers & inequality'),
    (r'^entrepreneurship', 'Entrepreneurship'),
    (r'^organization theory', 'Organization theory'),
    (r'^organization design|^organizational design', 'Organization design'),
    (r'economic sociology', 'Economic sociology & networks'),
    (r'innovation|science of science', 'Innovation & technology strategy'),
    (r'nonmarket|csr|sustainab', 'Nonmarket strategy, CSR & sustainability'),
    (r'upper echelons', 'Upper echelons & corporate governance'),
    (r'strategic human capital', 'Strategic human capital'),
    (r'behavioral strategy', 'Behavioral strategy'),
    (r'organizational economics', 'Organizational economics'),
    (r'corporate strategy|alliance|interorganizational', 'Corporate strategy, alliances & M&A'),
    (r'design', 'Organization design'),
    (r'strategy', 'Strategy (general / competitive)'),
]
OB_RULES = [
    (r'diversity|identity', 'OB - diversity & identity'),
    (r'negotiation|decision', 'OB - negotiation & decision making'),
    (r'creativ', 'OB - creativity'),
    (r'leadership|ethic', 'OB - leadership & ethics'),
    (r'emotion|well-being', 'OB - emotions & well-being'),
    (r'network', 'OB - social networks'),
    (r'team', 'OB - teams'),
]
def canon_sub(area, sub):
    low = (sub or '').lower().strip()
    if not low: return ''
    if area == 'Other':
        return sub.strip()
    if area == 'OB':
        for pat, rep in OB_RULES:
            if re.search(pat, low): return rep
        return 'OB - micro (individual)'
    for pat, rep in S_RULES:
        if re.search(pat, low): return rep
    return sub

INST_NORM = {
    'Harvard Business School': 'Harvard University',
    'Harvard University (Harvard Business School)': 'Harvard University',
    'University of Illinois at Urbana-Champaign': 'University of Illinois Urbana-Champaign',
    'University of Maryland, College Park': 'University of Maryland',
}

def clean(v):
    if v is None: return ''
    if isinstance(v, bool): return 'Yes' if v else 'No'
    if isinstance(v, list): return '\n'.join(str(x) for x in v)
    return str(v).strip()
