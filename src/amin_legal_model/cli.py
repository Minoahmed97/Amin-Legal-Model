import argparse
import json

from amin_legal_model.ingestion import ingest_document


def main() -> None:
    parser = argparse.ArgumentParser(description="AMIN Legal Model utilities")
    parser.add_argument("--version", action="version", version="AMIN Legal Model 0.1.0")
    commands = parser.add_subparsers(dest="command")

    ingest = commands.add_parser("ingest", help="Ingest a lawfully acquired legal document")
    ingest.add_argument("--input", required=True, help="Local TXT, MD, HTML, PDF or DOCX file")
    ingest.add_argument("--source-id", required=True, help="Source ID from configs/source_licenses.yaml")
    ingest.add_argument("--metadata", required=True, help="JSON object with required document metadata")
    ingest.add_argument("--output", default="data/corpus", help="Corpus output directory")

    args = parser.parse_args()
    if args.command == "ingest":
        try:
            metadata = json.loads(args.metadata)
        except json.JSONDecodeError as exc:
            parser.error(f"--metadata must be valid JSON: {exc}")
        result = ingest_document(
            args.input,
            source_id=args.source_id,
            metadata=metadata,
            output_dir=args.output,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print("AMIN Legal Model foundation is installed. No inference model is configured yet.")


if __name__ == "__main__":
    main()
