# Legal timelines, amendments and date-aware retrieval

Each corpus record may identify an instrument using \`legal_identifier\`, list instruments it \`amends\` or fully \`repeals\`, and list affected \`amended_articles\`. Dates must use ISO \`YYYY-MM-DD\`.

The timeline resolver:
- Excludes instruments whose recorded effective date is later than the requested date.
- Excludes an instrument explicitly fully repealed by a recorded instrument effective by that date.
- Keeps partially amended instruments and attaches the recorded active amendment references; it does not pretend to produce a consolidated text.
- Marks missing effective dates as unknown instead of assuming current validity.

\`amin-legal search --as-of-date YYYY-MM-DD\` applies this recorded-metadata filter. Search results include temporal status and warnings. They are not a legal opinion or certificate of law in force: completeness of repeal/amendment records, transitional provisions, court interpretation, commencement conditions, partial invalidity and interactions with other instruments still require legal review and authoritative source verification.

Use a stable, unique \`legal_identifier\` for every instrument and the exact same identifier in \`amends\`/\`repeals\`. Only use \`repeals\` for full repeal. For partial modification, use \`amends\` and specify affected article numbers. Never list a source as verified unless the source text and legal effect have actually been checked.
