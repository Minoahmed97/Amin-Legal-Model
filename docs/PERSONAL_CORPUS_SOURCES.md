# Egyptian legal corpus acquisition map — personal AMIN

This document identifies likely primary and supplementary sources for building a private Egyptian-law corpus. It does **not** grant permission to scrape, bulk-download, store, OCR, index, train on, or redistribute any source. The machine-readable source register remains default-deny until the relevant rights and access method are confirmed.

## Primary discovery and research sources

### 1. Egyptian Legislation Portal (IDSC)

- Portal: https://elpai.idsc.gov.eg/
- About: https://elpai.idsc.gov.eg/Home/About
- The portal describes coverage of Egyptian legislation and judgments, including more than 290,000 legislative items and more than 100,000 judgments. Treat these as the portal's own published figures, not independently audited corpus counts.
- Its navigation identifies legislation, Supreme Constitutional Court judgments, Cassation judgments, Supreme Administrative Court judgments, Economic Court judgments and State Council opinions.
- Action: request a private individual license/access route and written clarification whether manual export, personal storage, OCR, indexing and retrieval for the user's own legal work are permitted. Do not assume that a personal subscription includes automated or bulk extraction.

### 2. Ministry of Finance

- Legislation portal: https://mof.gov.eg/ar/legislation/legislation
- English portal: https://mof.gov.eg/en/legislation/legislation
- Useful for tax, public finance, customs and financial regulations.
- The Ministry states that its online texts are for guidance and that the Official Gazette is the controlling legal reference.
- Action: use as a discovery and cross-check source only until terms, storage and personal indexing permissions are confirmed. Verify every instrument against its Official Gazette publication.

### 3. Official Gazette and Al-Waqa'i Al-Misriyya

- The Official Gazette is the authoritative publication channel for primary legislation; Al-Waqa'i Al-Misriyya publishes secondary legislation and administrative decisions.
- Access/distribution can be subscription-based. The official publication, issue, date and page must be captured for provenance.
- Action: obtain official copies through an authorized access route; no automated extraction or bulk copying until the applicable terms and permissions are verified.

### 4. Ministry of Foreign Affairs legal database links

- https://welcometoegypt.mfa.gov.eg/GeneralSearch/LegalDatabases
- The portal exposes search links for legislation, Supreme Constitutional Court, Cassation, Supreme Administrative Court, administrative justice, economic judgments and State Council opinions.
- Action: treat as a navigation/discovery index. Follow each link to the actual source and assess its own terms; the MFA landing page is not itself a data license.

## Supplementary specialist sources

| Domain | Source | Role |
|---|---|---|
| Intellectual property | WIPO Lex — https://www.wipo.int/wipolex/ | Supplementary IP legislation and treaty discovery |
| Labour | ILO NATLEX — https://natlex.ilo.org/ | Supplementary labour and social-security materials |
| Agriculture/environment | FAOLEX — https://www.fao.org/faolex/ | Supplementary agriculture, food and environmental legislation |
| International law | Relevant treaty repositories and Egyptian treaty publication records | Verify ratification, publication, reservations and domestic effect |

These sources do not replace the Egyptian Official Gazette or the controlling official judicial source. Check currentness, translation status and record-specific reuse terms.

## Coverage plan

The ingestion inventory must be organized by legal branch and document class, not just by source website:

- Constitutional and public law.
- Civil obligations, contracts, torts, property, possession and registration.
- Civil and commercial procedure, evidence, execution and arbitration.
- Criminal substantive law, criminal procedure and special penal legislation.
- Commercial, companies, insolvency, banking, capital markets and investment.
- Labour, social insurance, public employment and civil service.
- Personal status for Muslims and non-Muslims, family and inheritance.
- Administrative law, State Council, public contracts and disciplinary law.
- Tax, customs, public finance and fees.
- Real estate, construction, planning, land, rent and urban communities.
- Intellectual property, cybercrime, telecommunications, data protection and media.
- Consumer protection, competition, transport, maritime, aviation and tourism.
- Environment, agriculture, health, education and professional regulation.
- International treaties, implementation instruments and conflict-of-laws materials.

For every branch, record laws, executive regulations, ministerial decisions, governorate/local decisions, circulars where legally relevant, official interpretations, binding judgments and persuasive judgments separately.

## Corpus acceptance gates

A document is not accepted as current law until it has:
1. An exact title, number, year and issuing authority.
2. Official publication reference (Gazette name, issue, date and page) or an identified official court source.
3. Original file hash and text hash.
4. Publication, commencement and effective dates.
5. Amendment, repeal, suspension and transitional-provision relationships.
6. Human verification of OCR and legal text, especially article numbers and punctuation.
7. Branch, document type, court/authority and precedential classification.
8. A source permission record for storage, OCR, indexing and AI retrieval.
9. A review date and an explicit unresolved-status field.

A personal-use corpus may omit public redistribution rights, but it still needs a lawful acquisition method and permission for any automated access or processing required by the project. Do not train or fine-tune on the corpus unless training permission is separately established.
