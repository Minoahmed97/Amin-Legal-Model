# Private single-user deployment

This stack is designed for one lawyer on a private GPU server. It keeps the model server on an internal Docker network and binds the API only to the server's loopback interface. It does not expose vLLM directly to the internet.

## 1. Server prerequisites

- Linux server with NVIDIA GPU, compatible NVIDIA driver and NVIDIA Container Toolkit.
- Docker Engine and Docker Compose plugin.
- Enough GPU memory for the selected Gemma 4 31B QAT checkpoint, runtime, KV cache and chosen context. The 4-bit model weights alone are estimated at about 17.5 GB by Google's model documentation; do not treat that as the complete GPU requirement. Begin with a conservative 16K context and one simultaneous sequence.
- Persistent disk for model cache, legal corpus, index and backups. Use encrypted storage and restrict host access.

The full BF16 Gemma 4 31B deployment recipe uses an 80 GB NVIDIA GPU. The QAT compressed-tensors checkpoint is used here to reduce weight memory, but actual memory must be verified on the target server.

## 2. Configure secrets

```bash
cp .env.personal.example .env
```

Replace both secrets with independent random values. For example, generate them locally using `openssl rand -hex 32`. Never commit `.env`, paste secrets into GitHub, or put the model-server key in a browser.

- `AMIN_API_KEY`: your private app/client-to-API key.
- `AMIN_MODEL_SERVER_KEY`: internal API key used only between the AMIN API container and vLLM.
- `AMIN_MODEL_ID`: exact model checkpoint.
- `AMIN_MODEL_NAME`: internal served name.

## 3. Start the private server

```bash
docker compose -f docker-compose.personal.yml up -d --build
docker compose -f docker-compose.personal.yml logs -f model
```

The first run downloads the checkpoint to a persistent Docker volume. It may take a long time. Wait for the model health check to become healthy, then:

```bash
curl http://127.0.0.1:8000/health
```

Expected readiness fields:
- `model_configured: true`
- `model_server_ready: true`

If the server cannot fit the model, do not reduce safeguards or silently switch to a hosted API. Adjust the GPU, quantization, or model size after measuring the failure.

## 4. Test a real private inference request

```bash
curl -X POST http://127.0.0.1:8000/v1/legal/respond \
  -H "Content-Type: application/json" \
  -H "X-Amin-Api-Key: $AMIN_API_KEY" \
  -d '{
    "task": "analyze",
    "jurisdiction": "EG",
    "language": "ar",
    "text": "اختبار تشغيل فقط: اشرح الفرق بين الدفع الشكلي والدفع الموضوعي، ولا تذكر مادة قانونية ما لم تستند إلى مصدر مسترجع."
  }'
```

This request verifies the inference path only. It is not a legal accuracy benchmark and will warn that no legal source retrieval was performed unless a reviewed index exists.

Run the repeatable readiness + real-inference smoke test after startup:

```bash
AMIN_API_KEY="$AMIN_API_KEY" python scripts/check_personal_deployment.py
```

The script prints pass/fail state without printing the answer or secret.

## 5. Private access from phone and computer

The API port is bound to `127.0.0.1`, so it is not directly reachable from the public internet. For remote personal access, use a private VPN such as WireGuard or Tailscale, or a reverse proxy accessible only through your private network with TLS and strong authentication. Do not change the bind address to `0.0.0.0` or expose port 8000 publicly as a shortcut.

Your client sends the `X-Amin-Api-Key` header. Store it in a trusted server-side integration, not in public frontend source code. For a browser-only client, use an authenticated same-origin backend proxy rather than exposing the secret in JavaScript.

## 6. Legal data and index

Place only authorized, reviewed documents under the ingestion workflow. Build the SQLite index using the CLI after each approved corpus import. The default source register denies collection and reuse until a source has explicit permission for each operation.

No Egyptian legal corpus is bundled with this deployment. Do not interpret an empty index as absence of a law or judgment. A legal production acceptance test requires a comprehensive, verified corpus and tested amendment history.

## 7. Operations

```bash
docker compose -f docker-compose.personal.yml ps
docker compose -f docker-compose.personal.yml logs --tail=200 api model
docker compose -f docker-compose.personal.yml down
```

Back up the legal corpus and SQLite index separately from the model cache. Encrypt backups. Never include case documents in public issue reports or CI logs.

## 8. What this deployment does not do automatically

It does not create or rent a GPU server, pay for hosting, obtain model-gated access, populate the Egyptian-law corpus, validate official legal sources, or connect the existing Ameen web app. Those steps require the actual server, source files/permissions and a private network route. The repository now contains the deployment recipe and API connector; a successful live deployment must be recorded only after running the health and inference tests on the actual host.
