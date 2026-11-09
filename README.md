# AuraGem — AI Jewellery Photography SaaS

Turn ordinary phone photos of jewellery into studio, lifestyle and on-model photographs, with an automated
design-fidelity check on every image.

## Features
- **Product studio** — 8 jewellery categories, 11 photography styles, background/lighting/angle/aspect/size controls, 1–4 variations, notes.
- **Model photography** — 6 Indian presets (bridal, South Indian, North Indian bridal, modern, festive, editorial), gender, appearance, pose, clothing, scene.
- **Background removal** — AI isolation onto an adaptive chroma key (green, or magenta for green stones) → transparent PNG; client-side background replacement & download.
- **Fidelity inspector** — pixel metrics (masked colour histogram, proportions) + AI vision inspector (shape, stones, metal, details). Low scores auto-regenerate once; results are labelled honestly (High fidelity / Review / Likely altered / Unverified).
- **Projects & gallery** — create/search/filter/delete projects, save images to projects, history table, ZIP download.
- **Credits & billing** — reserve-then-refund credit ledger, plans (Free 3 / Starter 20 / Growth 75 / Business 300), Razorpay orders + signature verification + webhook; labelled demo checkout when keys are absent.
- **Auth** — Emergent-managed Clerk (email/password + Google).

## Architecture
```
backend/
  server.py              FastAPI app wiring, startup (indexes, migrations, storage, job recovery)
  clerk_auth.py          Clerk session verification + production relay
  core/                  config, db + indexes, Pydantic document models, deps, security (signed URLs, rate limits), migrations
  ai/
    prompts.py           preset catalogue + prompt templates (preservation rules)
    imaging.py           validation, preprocessing, segmentation/mask, chroma key, aspect fit, resize
    quality.py           fidelity evaluation pipeline
    providers/           ImageGenerationProvider ABC, Gemini (Nano Banana) and Mock implementations
  services/              storage (object storage), credits ledger, jobs worker, serializers
  payments/razorpay.py   Razorpay REST + HMAC verification
  api/                   account, projects, studio (uploads, jobs, images, files), billing
frontend/src/
  pages/                 Landing, Dashboard, Studio, ModelStudio, BackgroundRemoval, Projects, ProjectDetail, History, Billing
  components/studio/     Uploader, Controls, ResultsCanvas, ImageCard, CompareSlider, QualityBadge, useGeneration
```
Platform note: this deployment runs React (CRA) + FastAPI + MongoDB with an in-process asyncio worker. The provider,
storage and job layers are isolated so they can be swapped for Celery/Redis or PostgreSQL later.

### Generation pipeline
upload (decoded validation, 15 MB, ≥256px) → reserve credits → job queued → preprocess (EXIF, flatten, resize, sharpen)
→ provider render (retry ×2) → post-process (aspect fit without cutting jewellery, resize) → fidelity evaluation
(regenerate once if score < 5) → store → settle (refund failed outputs).

## Setup
Backend env: see `backend/.env.example`. Frontend env: `REACT_APP_BACKEND_URL`.
```
cd backend && pip install -r requirements.txt && uvicorn server:app --port 8001
cd frontend && yarn install && yarn start
docker compose up --build        # local stack incl. MongoDB
```
Set `AI_PROVIDER=mock` for a clearly watermarked development mode with no AI calls.

## API
Interactive docs: `GET /api/docs` (OpenAPI at `/api/openapi.json`). Main routes:
`/api/catalog`, `/api/me`, `/api/dashboard`, `/api/projects`, `/api/uploads`, `/api/jobs`, `/api/jobs/{id}/rerun`,
`/api/images`, `/api/files/{kind}/{id}` (signed), `/api/billing/{summary,orders,verify,demo-complete,cancel,webhook}`.

## Tests
`cd backend && python -m pytest tests -q` (unit) · `python tests/e2e_smoke.py <api> <image>` (live smoke).
