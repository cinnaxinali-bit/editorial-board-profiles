# Task: profile management scholars (one batch of a 358-person Editorial Review Board list)

You are researching a batch of academic management scholars. Your batch file lists each person as
`id | name as listed | institution as listed`. For EVERY person in your batch, find the facts below
using web research, then write the results as JSON to the output path given in your prompt.
Do the research yourself (do not spawn other agents). Today's date is October 2026, so report the
CURRENT position (as of 2026).

## Facts to find for each person
1. **Website**: the official faculty profile URL at their current institution, plus a personal
   website if they have one (e.g., Google Sites, personal domain), plus a CV URL if you come across one.
   Only record URLs you actually saw in search results or fetched pages. Never construct/guess URLs.
2. **Current institution** and school/department/unit (e.g., "Wharton School, Management Dept").
   The listed institution may be outdated (people move) or contain typos/old names
   (e.g., "Cass Business School" is now "Bayes Business School"). Check whether they moved.
3. **Current title** exactly as stated (e.g., "Barbara and Meyer Feldberg Associate Professor of Business")
   and a normalized **rank**: one of `Assistant`, `Associate`, `Full`, `Other`.
   - Endowed/chaired/distinguished "Professor", HK "Chair Professor", UK/European "Professor" => `Full`.
   - UK "Associate Professor", "Senior Lecturer", "Reader" => `Associate` (mention Reader/Senior Lecturer in rank_detail).
   - UK "Lecturer", "Assistant Professor" => `Assistant`.
   - Emeritus, dean-only, non-faculty, lecturer/teaching track, research scientist, etc. => `Other` (explain in rank_detail).
   - Watch for recent promotions/moves (e.g., promoted July 2025 or 2026): if a CV, news item, or newer
     page shows a later title than the directory, use the newest and say so in rank_detail.
4. **Research topics**: concise summary (roughly 6-20 words, keyword-style, semicolon-separated),
   based on their own profile/CV/papers.
5. **PhD**: institution, program/field (e.g., "Sociology", "Organizational Behavior", "Strategy", "Management"),
   and year if available. Example: institution "Stanford University", field "Sociology", year "2012".
   Use faculty bios, CVs, dissertation records, LinkedIn snippets. If the PhD program is housed in a
   business school, give the university plus school in phd_institution (e.g., "University of Pennsylvania (Wharton)").
6. **Area classification** (binary): `Strategy & OT` or `OB`, plus a short subfield label and a one-line rationale.
   - `OB` = primarily micro/meso and psychological: individuals, dyads, teams; leadership, motivation,
     emotions, creativity, prosocial behavior, voice, status/power/hierarchy (social-psych lens),
     negotiation, judgment & decision making, ethics/morality, diversity/identity from a psychological
     lens, well-being, meaning of work, work-family, proactivity, feedback, team processes.
     Typical training: OB or social/organizational psychology; typical outlets: JAP, OBHDP, AMJ, PSPB,
     Psych Science, Personnel Psych; AOM OB division.
   - `Strategy & OT` = primarily macro: strategy (competitive advantage, corporate strategy, M&A,
     alliances, governance, CEOs/upper echelons/TMTs, nonmarket strategy, CSR/sustainability,
     strategic human capital, innovation/technology strategy, R&D, science of science, platforms,
     entrepreneurship, venture capital, organizational economics) and organization theory /
     economic sociology (institutions, categories, networks, labor markets & hiring, careers and
     inequality from a sociological lens, ecology, social movements, organizational learning, routines,
     field-level change, qualitative/ethnographic studies of work, occupations, professions and technology).
     Typical training: strategy, sociology, economics, macro management; outlets: SMJ, ASQ, Org Science,
     ASR/AJS, Management Science; AOM BPS/OMT/STR/TIM/ENT/SIM divisions; SMS.
   - Hybrids: pick the dominant side based on their body of work and home group, and explain in
     area_rationale (e.g., "qualitative work & occupations scholar -> OT", or "identity research in
     psych tradition -> OB"). Behavioral strategy -> Strategy & OT. Information systems / technology &
     organizing scholars -> Strategy & OT (note IS in subfield). Micro-level sociologists of work
     (hiring, inequality, careers) -> Strategy & OT.
   - Suggested subfield labels (use one, or a short custom label): "Strategy", "Corporate strategy & governance",
     "Upper echelons / corporate governance", "Innovation & technology strategy", "Entrepreneurship",
     "Nonmarket strategy / CSR", "Strategic human capital", "Organizational economics", "Behavioral strategy",
     "Organization theory", "Economic sociology / networks", "Labor markets, careers & inequality",
     "Work, occupations & technology (qualitative)", "Information systems", "OB - micro",
     "OB - teams", "OB - negotiation / decision making", "OB - leadership & ethics", "OB - diversity & identity",
     "OB - emotions & well-being", "OB - creativity".

## Method (be efficient: typically 2-4 searches per person)
- Use the WebSearch tool with mode "standard" (switch to "extended" only if standard results are thin
  for a specific person). Good queries: `"<name>" <institution> faculty`, `"<name>" CV PhD`,
  `"<name>" management professor`.
- If you have a WebFetch tool, use it to open the faculty page or CV when the search summary lacks a
  needed fact (PhD, exact title). Fetching with curl via Bash is often blocked by Cloudflare, but may
  work for some sites (use a browser User-Agent; never disable TLS verification).
- Disambiguate carefully: many names are common (e.g., multiple "Kevin Lee", "Ying Li", "Daniel Kim").
  The person must be a management/organizations/strategy scholar plausibly on a top management
  journal's editorial board, at or recently at the listed institution. If two batch entries might be
  the same person, check and note it.
- Prefer official university pages and CVs; treat outdated pages with care. Record the URLs you relied
  on in `sources`.
- If something truly cannot be found, leave the field as an empty string and explain in `notes`;
  set confidence accordingly. Do not invent facts.

## Output
Write a JSON array (UTF-8, valid JSON, one object per person, in batch order) to the output path.
Write/overwrite the file progressively (e.g., after every ~5 people) so partial work is saved.
Each object must have exactly these keys:

{
  "id": 1,                                   // integer from the batch file
  "name_listed": "Mabel Abraham",
  "institution_listed": "Columbia University",
  "full_name": "Mabel Abraham",              // as they present it (include middle initial if commonly used)
  "current_institution": "Columbia University",
  "school_unit": "Columbia Business School, Management Division",
  "moved": false,                            // true if current institution differs from the listed one
  "title": "Barbara and Meyer Feldberg Associate Professor of Business",
  "rank": "Associate",                       // Assistant | Associate | Full | Other
  "rank_detail": "",                         // e.g., "promoted to Associate effective July 2025 per CV"
  "faculty_page_url": "https://...",
  "personal_website_url": "",
  "cv_url": "",
  "research_topics": "gender inequality; labor markets; networks; entrepreneurship",
  "phd_institution": "Massachusetts Institute of Technology (MIT Sloan)",
  "phd_field": "Management (Economic Sociology)",
  "phd_year": "2014",
  "area": "Strategy & OT",                   // Strategy & OT | OB
  "subfield": "Labor markets, careers & inequality",
  "area_rationale": "Economic sociologist studying network/organizational sources of gender gaps",
  "confidence": "high",                      // high | medium | low (overall reliability of the record)
  "sources": ["https://..."],
  "notes": ""                                // anything uncertain, name typos, disambiguation, etc.
}

(The example values are illustrative only; verify everything independently.)

After the file is written, validate it parses (e.g., `python3 -c "import json;json.load(open('<path>'))"`).
Your final reply should be SHORT (under 120 words): the output path, how many records were written,
and which people (if any) are low-confidence or unresolved and why.
