# Editorial Board Profiles

Profiles of the 358 people on a management journal's Editorial Review Board list (supplied as
names and institutions in October 2026). For each person the data gives their website, current
institution, position, research topics, PhD, and whether their work falls on the
**Strategy & OT** or the **OB** side of the field.

## Outputs

| File | What it is |
|---|---|
| `output/ERB_Scholar_Profiles.xlsx` | **Scholars** sheet (one row per person, filters on), **Summary** sheet (live counts by area, position, subfield and PhD university), **Read me** sheet (definitions and caveats) |
| `output/ERB_Scholar_Profiles.csv` | The Scholars sheet as CSV (UTF-8) |

Headline numbers (October 2026):

| | Assistant | Associate | Full | Other | Total |
|---|---|---|---|---|---|
| Strategy & OT | 94 | 98 | 81 | 8 | 281 (78%) |
| OB | 22 | 33 | 22 | 0 | 77 (22%) |

34 people have moved since the list was published. Both the listed and current institutions are kept.

## Layout

```
data/input/erb_list.csv              the list as supplied (id, name, listed institution)
data/research/first_pass/*.json      first-pass research records, 20 people per file
data/research/corrections/*.json     gap-filling and verified corrections; applied over the
                                     first pass in filename order (only the fields they contain)
docs/workbook_readme.txt             text of the workbook's "Read me" sheet
prompts/                             the research instructions used for the first pass and gap pass
scripts/build.py                     merges the records and writes output/
scripts/check.py                     reports missing fields, invalid values and low-confidence records
output/                              the built workbook and CSV
```

## Rebuilding

```bash
pip install openpyxl
python3 scripts/check.py    # sanity-check the records
python3 scripts/build.py    # writes output/ERB_Scholar_Profiles.xlsx and .csv
```

The Summary sheet uses formulas; Excel calculates them when the file opens. The committed
workbook was also recalculated with LibreOffice so the values show in previewers.

To correct a record, add a JSON file to `data/research/corrections/` containing `id`,
`name_listed` and only the fields being changed, then rebuild.

## Record fields

Each record in `data/research/` has: `id`, `name_listed`, `institution_listed`, `full_name`,
`current_institution`, `school_unit`, `moved`, `title`, `rank` (Assistant / Associate / Full /
Other), `rank_detail`, `faculty_page_url`, `personal_website_url`, `cv_url`, `research_topics`,
`phd_institution`, `phd_field`, `phd_year`, `area` (Strategy & OT / OB), `subfield`,
`area_rationale`, `confidence` (high / medium / low), `sources`, `notes`.

## How it was made

The records were researched in October 2026 by parallel Claude research agents working from
official faculty pages, CVs, dissertation records, ORCID and web search, following
`prompts/research_instructions.md`. A second pass (`prompts/gap_fill_instructions.md`) filled
records that were incomplete because school websites blocked automated access. Surprising
claims, such as moves, and a random sample were then checked by hand. Every record lists the
URLs it relies on in `sources`, and links were taken from pages and search results, never
constructed.

Rules for normalizing positions and assigning Strategy & OT vs OB are in
`docs/workbook_readme.txt`. In short, OB means micro, psychological research on individuals and
teams. Strategy & OT means macro research: strategy, innovation, entrepreneurship, governance,
organization theory and economic sociology, including qualitative studies of work. The 36 people
who straddle the line are flagged "Borderline call?" in the workbook, with a one-line rationale.

## Caveats

- Titles change every July with promotions and moves, so check a profile before relying on it.
- 318 records are high confidence and 40 medium, usually because a PhD year is missing or a 2026
  title could not be confirmed. 62 records have no PhD year, and 5 have no website link.
- Research-topic summaries are condensed from each person's own profile, CV and recent papers.
