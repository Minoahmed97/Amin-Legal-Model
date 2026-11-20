# Comprehensive Egyptian Law Coverage

**Scope decision (2026-11-20): AMIN is a general-purpose Egyptian-law engine.** It must not be restricted to one practice area, court, client type, or legal workflow. This document defines the coverage target; it does not claim that the corpus has already been collected or that every source is licensed for ingestion.

## Coverage principle

Cover every branch of Egyptian law: general laws, special legislation, regulations, ministerial and administrative decisions, treaties binding on Egypt, judicial principles, and authoritative interpretations. This taxonomy is expandable, not a closed list.

## Required subject-matter coverage

- **Constitutional and public law:** constitutional principles, rights and freedoms, elections, political parties, public authorities, constitutional litigation.
- **Civil law:** obligations, contracts, liability, compensation, property, possession, real rights, leases, insurance, gifts, agency, guarantees, limitation, evidence, persons.
- **Commercial and business law:** commercial transactions, companies, investment, bankruptcy/restructuring, negotiable instruments, banking, capital markets, competition, consumer protection, commercial agencies, intellectual property.
- **Criminal law:** general part, crimes and penalties, special penal statutes, economic crimes, cybercrime, public funds, corruption, drugs, weapons, customs, tax crimes.
- **Criminal procedure:** investigation, evidence, arrest, detention, trial, jurisdiction, appeals, cassation, execution, reconciliation, limitation.
- **Civil and commercial procedure:** jurisdiction, pleadings, service, interim relief, evidence, experts, judgments, appeals, cassation, enforcement, arbitration-related court proceedings.
- **Administrative law and State Council:** administrative decisions/contracts, public employment, disciplinary matters, procurement, public utilities/funds, administrative liability, annulment and compensation, State Council jurisdiction, administrative judgments and published fatwas/opinions.
- **Personal status and family law:** Muslim personal status, marriage, divorce, maintenance, custody, lineage, guardianship, inheritance, wills, endowments; distinct personal-status rules for non-Muslim communities, including differences by recognized denomination, subject, and applicable legislation. Never assume one uniform code.
- **Labor and social protection:** employment, collective labor, occupational safety, social insurance, pensions, work injuries, unions, labor disputes.
- **Tax, customs, and public finance:** income tax, VAT, stamp tax, real estate tax, customs, tax procedures, public budget, public debt, financial control.
- **Real estate, land, and construction:** registration, property development, planning, building, rent, agricultural land, expropriation, land allocation, utilities.
- **Specialized and regulatory law:** environment, health, education, universities, transport, aviation, maritime, telecoms, media, data and technology, energy, natural resources, agriculture, antiquities, tourism, sports, associations, NGOs, professional syndicates.
- **International and transnational law:** treaties binding on Egypt, private international law, nationality, immigration/residency, extradition, mutual legal assistance, cross-border commerce.
- **Legal professions and judicial organization:** judiciary, prosecution, lawyers, experts, notaries, court organization, judicial inspection, professional discipline.

## Required judicial coverage

Collect and index, subject to lawful access and reuse: Court of Cassation (civil, commercial, economic, labor, personal-status, criminal, general-assembly principles); Supreme Administrative Court and Administrative Judiciary; Supreme Constitutional Court; Economic Courts and other specialized/ordinary courts where authoritative material is available; State Council opinions/fatwas where publication and reuse are permitted.

For every item record court/authority, circuit where available, date, docket or appeal number, source, and procedural/legal status. Distinguish a full judgment from an extracted principle, headnote, summary, and commentary. Never call a ruling binding precedent without checking its authority and legal effect.

## Primary-source hierarchy and discovery sources

1. Official Gazette (Al-Jarida Al-Rasmiyya) and the applicable official publication for ministerial/administrative instruments.
2. Official government and ministry portals, recording any disclaimer that the Gazette is controlling.
3. Official court portals and official judgment/principle databases.
4. Official parliamentary records for legislative history.
5. Secondary legal libraries and commentary only as supplementary discovery, never silently substituted for authoritative text.

Initial discovery points (access and reuse terms must be checked before bulk collection):
- Egyptian Legislation Portal (IDSC): https://elpai.idsc.gov.eg/
- Court of Cassation: https://cc.gov.eg/
- Ministry of Finance legislation collection: https://mof.gov.eg/en/legislation/legislation
- Library of Congress Egypt legal research guide: https://wwws.loc.gov/law/help/guide/nations/egypt.php

The IDSC portal exposes searches for legislation, Supreme Constitutional Court, Cassation, Supreme Administrative Court, Administrative Judiciary, economic judgments, and State Council opinions. The Cassation portal exposes civil and criminal divisions and related specializations. These are discovery sources, not proof that every record is downloadable, complete, machine-readable, or licensed for bulk reuse.

## Rights, permissions, and source admission (mandatory)

**Default-deny rule:** no document collection, automated extraction, bulk download, persistent storage, indexing, commercial retrieval/display, redistribution, or model training from a source until the exact intended use has a documented legal basis. Public accessibility, a paid personal subscription, or the fact that a document is an official document does not by itself establish permission for every technical and commercial use.

Before onboarding a source, complete [SOURCE_LICENSE_REGISTER.md](SOURCE_LICENSE_REGISTER.md) and retain evidence (terms snapshot/PDF, written permission, contract, correspondence, date checked, and reviewer). Do not use a personal login or subscription as a substitute for institutional permission. Do not circumvent rate limits, access controls, CAPTCHAs, robots restrictions, or express anti-automation terms.

Every source and every permitted processing activity must be independently classified. A source can permit reading but not automated collection; storage but not redistribution; RAG/retrieval but not fine-tuning. **RAG, model training/fine-tuning, and displaying source passages to commercial end users are separate permissions and must each be expressly covered where required.**

Required per-source record:
- legal owner/operator and exact source/service;
- terms URL, version/date checked, and evidence location;
- access method permitted (manual, API, bulk export, automated access);
- permitted copying, storage, backup, OCR, normalization, and retention;
- permitted indexing, embeddings, retrieval, AI analysis, and commercial end-user display;
- permitted redistribution/export and attribution requirements;
- whether training/fine-tuning is expressly allowed;
- user/account limits, rate limits, geography, confidentiality and personal-data restrictions;
- fee, contract term, expiry, termination/deletion duties, and contact;
- decision owner, legal review date, next review date, and status.

Allowed status values:
- `approved`: documented basis covers the exact planned processing and commercial use.
- `written_permission_required`: do not ingest until signed/written permission is received.
- `research_only`: use only within the documented non-commercial/research limits; exclude from production commercial corpus.
- `blocked`: terms expressly prohibit the planned method/use, or permission was refused.
- `unknown`: terms have not been adequately checked; treat as not approved.

## Temporal law and amendment tracking

Store each legal instrument as a versioned record. Capture, where available: instrument type/number/year and authority; official publication number/date; enactment, publication, commencement, repeal dates; every amending/repealing/suspending/interpreting instrument; affected articles and before/after text; transitional provisions; territorial/personal/subject scope; status as of a specified date; source URL/file, retrieval date, checksum, OCR and human-review status.

Retrieval must answer **law in force today**, **law applicable on the date of the facts**, and **the change history between two dates**. Never apply a later amendment retroactively unless the applicable rule supports it. Surface conflicts, transitional provisions, and uncertainty.

## Data quality and legal safety

- Preserve original Arabic and page/source references. Mark OCR as unverified until checked.
- Preserve article numbering, paragraphs, footnotes, tables, schedules, annexes, and amendment notes.
- Separate official text, judgment, extracted principle, commentary, and model-generated explanation.
- Store passage-level citation metadata.
- Detect duplicates/conflicting versions; never silently overwrite history.
- Mark missing years, inaccessible records, and unverified citations.
- Never fabricate laws, articles, judgments, appeal numbers, dates, courts, quotations, or facts.
- Keep private client files separate from the public corpus; they are not training data by default.
- Do not treat a statutory exception from copyright protection for official documents as blanket permission to breach portal terms, bypass access restrictions, or copy a protected database compilation/arrangement. Obtain Egyptian legal review for each acquisition route.

## Coverage as a release requirement

A branch is not covered merely because it appears in a prompt or taxonomy. Track source inventory, date range and gaps, verified-text rate, amendment-chain completeness, judicial coverage, citation resolution, benchmark performance, and last update. Do not advertise that all Egyptian law is complete and current until measurable coverage, provenance, monitoring, and human-reviewed validation support that claim.
