# AMIN Legal API

Base URL is the host running Uvicorn. The interactive OpenAPI schema is available at \`/docs\` in development; do not expose development documentation publicly without an access policy.

## Health

\`GET /health\` reports whether a provider is configured and whether model weights have actually loaded. \`status=ok\` only verifies the API process.

## Access control

Set \`AMIN_ENV=production\` and a strong \`AMIN_API_KEY\`. All \`/v1\` routes then require:

\`\`\`http
X-Amin-Api-Key: <secret>
\`\`\`

The secret must be stored in the host's secret manager, never in source control or browser code. In development the key is optional. This shared-key gate is not a substitute for per-user identity, roles, tenant isolation, quotas or distributed rate limiting.

## Strategy triage

\`POST /v1/legal/strategy\` accepts structured facts and returns an auditable preliminary choice. Example:

\`\`\`json
{
  "objective": "رفض طلب الخصم",
  "case_stage": "استئناف",
  "client_role": "مستأنف ضده",
  "as_of_date": "2026-11-20",
  "deadline_date": "2026-11-25",
  "deadline_verified": false,
  "mandatory_response": false,
  "silence_harm_possible": false,
  "risk_of_curative_reply": true,
  "response_points": [
    {
      "title": "مخالفة الثابت بالمستند رقم 3",
      "supported_by_record": true,
      "materiality": "high"
    }
  ],
  "missing_documents": ["أصل محضر التسليم"]
}
\`\`\`

The rule-based result is not an AI opinion and does not calculate Egyptian procedural deadlines. The user must identify whether a response is legally mandatory and verify service, commencement, suspension, extension and holiday rules.

## Source-grounded legal response

\`POST /v1/legal/respond\` accepts the task and case text. To request retrieval from an authorized SQLite FTS index, include \`retrieval_query\`; include \`as_of_date\` to filter using recorded effective dates and amendment/repeal relationships.

\`\`\`json
{
  "task": "analyze",
  "jurisdiction": "EG",
  "language": "ar",
  "text": "وقائع الدعوى والمستندات والطلبات...",
  "retrieval_query": "المادة 147 الظروف الطارئة تنفيذ العقد",
  "as_of_date": "2024-06-01"
}
\`\`\`

The response contains:
- \`answer\`: model-generated output.
- \`sources\`: retrieved passages' provenance fields.
- \`warnings\`: missing index, empty retrieval, temporal uncertainty or permission errors.

A retrieval result proves only that a matching record exists in the locally supplied index and that the requested operation passed the current permission register. It does not prove corpus completeness, legal validity, binding status or that an amendment has been consolidated. Verify every source against the official publication and the facts date. Without \`retrieval_query\`, the API explicitly warns that no indexed legal retrieval was performed.

## Current limitations

The lexical search requires a deliberate retrieval query; it is not yet semantic search. No official Egyptian-law corpus is bundled. Model selection, legal citation validation, source completeness and lawyer-reviewed strategy evaluation remain release gates.
