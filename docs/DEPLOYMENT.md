# Deployment notes

The initial service is a development scaffold, not a production legal AI service.

Recommended production shape:
- A dedicated inference host with suitable GPU capacity for the selected model.
- An API service separated from model weights and private datasets.
- Secrets supplied through the hosting environment, never committed.
- Authentication, authorization, rate limiting, audit logging, and encrypted transport.
- Monitoring for latency, errors, resource usage, and model/version changes.
- Backups and tested retention/deletion procedures.

Do not assume a serverless web deployment can host long-running model inference or GPU workloads. Choose infrastructure only after model and load requirements are measured.
