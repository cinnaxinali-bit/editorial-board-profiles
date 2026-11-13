# Gap-filling pass (second pass) for the scholar-profile task

A first pass already profiled all 358 people (see instructions.md in this folder for the full field
definitions, allowed values, rank normalization and the Strategy & OT vs OB classification rules —
read it first). The people in YOUR list are the ones with missing or low-confidence fields, usually
because their school's website blocks automated fetching (Cloudflare/403) and the shared search budget
ran out. Each line of your list is:
`id | name as listed | listed institution | known: first-pass values | MISSING: fields to fill | notes: first-pass notes`

## Your job
- Fill the MISSING fields and confirm anything the notes flag as uncertain. For confidence=low lines,
  re-verify everything (identity, current institution, title/rank, website, topics, PhD, area).
- If a person seems to have left the listed school, find where they are now (search their name with
  "assistant professor"/"associate professor"/"joins", their recent papers' affiliations, coauthors).
  If they have left academia or cannot be found, say so in notes.
- Treat first-pass notes marked "background knowledge"/"unverified" as hypotheses to check, not facts.

## Search budget (important)
- HARD CAP: at most 38 WebSearch calls for your whole list. The budget is shared with other agents
  running at the same time; going over it starves them. Plan about 2-3 searches per person, 1 when only
  a PhD or a website is missing. Use mode "standard".
- WebSearch result summaries quote page text, so they work even when a school's site blocks direct
  fetching. A URL that appears in search results and is clearly the person's official profile page
  counts as a verified faculty_page_url (record it).
- Unlimited alternatives (use freely): WebFetch if you have it; curl via Bash with a browser
  User-Agent (never disable TLS verification) on sites that are not blocked; ORCID public API
  (e.g., curl -H "Accept: application/json" "https://pub.orcid.org/v3.0/expanded-search/?q=given-names:Jane+AND+family-name:Doe",
  then /v3.0/<orcid>/employments and /educations); OpenAlex (https://api.openalex.org/authors?search=Jane%20Doe);
  Crossref (https://api.crossref.org/works?query.author=...); personal websites; CV PDFs; SSRN author pages.

## Output
Write a JSON array to the output path in your prompt. One object per person in your list, each with:
- "id" and "name_listed" (always),
- every field you verified or corrected, using the same keys and allowed values as instructions.md
  (e.g., current_institution, school_unit, moved, title, rank, rank_detail, faculty_page_url,
  personal_website_url, cv_url, research_topics, phd_institution, phd_field, phd_year, area, subfield,
  area_rationale, full_name),
- and ALWAYS "confidence" (updated overall reliability), "sources" (the complete list of URLs that
  support the record, including earlier ones that still apply) and "notes" (rewritten: concise and
  current; drop remarks about the search budget running out).
Fields you omit keep their first-pass values, so omit only fields you did not check. To blank out a
wrong first-pass value, include the key with "". Never invent facts or URLs.
Write/overwrite the file progressively, validate that it parses
(python3 -c "import json;json.load(open('<path>'))"), and keep your final reply under 120 words:
the path, how many records, and who is still unresolved and why.
