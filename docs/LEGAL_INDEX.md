# Legal corpus indexing and retrieval

The first search layer uses SQLite FTS5 with Unicode tokenization. It is a deterministic lexical baseline, not a vector embedding or semantic reranker.

## Build

After a lawful source has `store: true` and `index_and_embed: true` in `configs/source_licenses.yaml`, run:

```bash
amin-legal ingest --input ./law.txt --source-id YOUR_APPROVED_SOURCE_ID --metadata '{"title":"عنوان القانون","document_type":"law","branch":"civil","source_reference":"رقم الجريدة الرسمية وتاريخها","publication_date":"2020-01-01","effective_from":"2020-02-01"}'
```

Then build the index from the generated JSONL using the Python API:

```python
from amin_legal_model.legal_index import build_legal_index

build_legal_index("data/corpus/legal_documents.jsonl", "data/index/legal.sqlite")
```

Each indexed chunk retains document ID, title, branch, source reference, source URL, publication/effective dates, and source ID. The indexer rechecks `index_and_embed` permission. Retrieval rechecks `ai_retrieval_and_analysis` permission, so a revoked or missing permission prevents passages from being returned.

## Limitations

- FTS5 is lexical matching; semantic embeddings and reranking are not implemented.
- Search currently requires all query tokens to match.
- Date-aware legal conflict resolution and amendment-chain traversal are not implemented.
- OCR and page-level PDF citation mapping are separate future stages.
- The index contains only records in the authorized staging corpus; it does not acquire data itself.
