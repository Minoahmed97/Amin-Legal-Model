# Source License Register

**Project:** AMIN Legal Model  
**Last reviewed:** 2026-11-20  
**Policy:** Default deny. No production ingestion until the exact planned use is supported by current terms or written permission and recorded evidence.

This is an operational register, not a legal opinion or a declaration that AMIN has obtained any license. A status of `written_permission_required` or `unknown` means **do not bulk collect, scrape, store, index, use for commercial retrieval, redistribute, or train on the source** unless and until the required rights are documented.

## Status definitions

| Status | Operational meaning |
|---|---|
| `approved` | Written/current evidence covers the exact planned activities and commercial context. |
| `written_permission_required` | Obtain written/institutional permission before ingestion or use. |
| `research_only` | Limited research use only, within the source's stated conditions; not production commercial corpus. |
| `blocked` | The intended method/use is expressly prohibited or permission was refused. |
| `unknown` | Insufficiently reviewed; treat as not approved. |

## Initial source register

| Source | Current status | What is established | Required action before production |
|---|---|---|---|
| Egyptian Legislation Portal (IDSC) — https://elpai.idsc.gov.eg/ | `written_permission_required` | The portal offers paid individual/institutional access and states rights are reserved to the relevant IDSC center. Public subscription access is not evidence of a commercial AI/data license. | Ask IDSC for a signed institutional license covering the exact data categories, bulk/API access, storage, OCR, indexing/embeddings, RAG, commercial display/citations, updates, retention, and (separately) model training/fine-tuning. |
| Egyptian Court of Cassation — https://cc.gov.eg/ | `written_permission_required` for commercial reuse; `blocked` for automated extraction absent express written authorization | Published terms restrict use to specified legal/academic/research/documentation purposes, require prior written consent for commercial use/publication, and prohibit automated extraction/collection even for a subscribed user. | Do not scrape or bulk extract. Request express written institutional permission/API or authorized bulk export. License must cover storage, indexing, AI analysis/RAG, commercial user display, redistribution if needed, updates, and training separately. |
| Official Gazette / Al-Jarida Al-Rasmiyya and Al-Waqa'i Al-Misriyya | `unknown` for automated bulk acquisition and downstream database use | Official publication is the primary source for authoritative legal texts. The copyright treatment of official documents does not by itself settle access, bulk acquisition, database compilation, technical restrictions, or all downstream contractual issues. | Identify official publisher/distribution channel; confirm lawful access and bulk acquisition method. Obtain legal review of reproduction, database rights, and commercial product use. Preserve Gazette issue/page provenance. |
| Egyptian Ministry of Finance legislation portal — https://mof.gov.eg/en/legislation/legislation | `unknown` | It publishes a selection of tax/financial legal materials and indicates that its online texts are guidance while the Official Gazette is controlling. | Confirm terms, automated access, storage, commercial retrieval/display, attribution, and update reliability. Do not treat it as a complete or controlling corpus. |
| WIPO Lex — https://www.wipo.int/wipolex/ | `unknown` pending terms review | Useful secondary discovery/reference source for selected legislation and treaty texts; not a substitute for verifying the official Egyptian publication and current consolidated text. | Review WIPO Lex terms and record-level source/provenance; verify currentness against official publications. Do not assume bulk reuse or model-training rights. |

## Per-source permission checklist

Before changing a source to `approved`, the reviewer must answer and attach evidence for every item below:

- [ ] Identity of rights holder/operator and the contracting party is verified.
- [ ] Current terms and applicable law have been reviewed and saved with review date.
- [ ] Access method is expressly allowed: manual download, API, bulk export, or automated retrieval as applicable.
- [ ] Copying, OCR, normalization, backup, persistent storage, and retention are covered.
- [ ] Search indexing, chunking, embeddings, retrieval, and AI analysis are covered.
- [ ] Commercial service use and display of source passages/citations to end users are covered.
- [ ] Redistribution, export, and user downloads are covered or explicitly excluded in product behavior.
- [ ] Fine-tuning/model training is separately and expressly allowed, if intended. Silence is not consent.
- [ ] Attribution, linking, quotation limits, and source notices are implemented.
- [ ] Rate limits, account/user limits, confidentiality, personal data, and security conditions are implemented.
- [ ] Fees, renewal, termination, expiry, deletion/return duties, and update obligations are documented.
- [ ] Written permission is signed by an authorized representative where required.
- [ ] Legal reviewer and engineering owner approve the specific ingestion pipeline.

## Engineering enforcement

Use a source registry record with at least these fields:

```yaml
source_id: example_source
owner: rights_holder_or_operator
source_url: https://example.org
terms_url: https://example.org/terms
terms_checked_at: YYYY-MM-DD
license_status: unknown
evidence_ref: null
access_methods:
  manual: false
  api: false
  bulk_export: false
  automated_access: false
permissions:
  store: false
  ocr_and_normalize: false
  index_and_embed: false
  ai_retrieval_and_analysis: false
  commercial_display: false
  redistribute: false
  train_or_finetune: false
attribution_required: unknown
expires_at: null
reviewer: null
next_review_at: null
notes: "Default deny until verified."
```

Ingestion must fail closed if the source is `unknown`, `research_only`, `written_permission_required`, or `blocked` for the requested operation. Permission to retrieve does not imply permission to train. Permission to store does not imply permission to redistribute. Keep a machine-readable decision and human-readable evidence trail.

## Legal references and caution

Egyptian Intellectual Property Law No. 82 of 2002 includes an exception for certain official documents (including laws, regulations, decisions, treaties, and judicial rulings) in Article 141, while database compilation/selection/arrangement can raise separate protection questions. This should be reviewed against the current official Arabic text and the facts of the acquisition. It is not a blanket waiver of portal terms, access controls, database rights, privacy obligations, or contractual restrictions.

No AMIN source should be marked `approved` solely because a document can be viewed in a browser, a user paid for a personal subscription, or the text appears to be an official document.
