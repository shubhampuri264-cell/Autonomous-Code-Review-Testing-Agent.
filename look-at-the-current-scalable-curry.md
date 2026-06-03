# Roadmap: Autonomous Code Review & Testing Agent — from current state to v1.0.0 and a bigger-scale v2

## Context

The repo is a **portfolio-grade agentic system** (LangGraph + FastAPI + tree-sitter + Docker + Supabase + React) that autonomously generates, runs, self-corrects, and PRs a test suite for a target repo. A PRD (`.claude/PRD_document.txt`) defines an 8-phase, 48-deliverable plan ending at a deployed, demo-ready v1.0.0.

**Ground-truth state (verified during exploration), which differs from the memory notes:**
- All 10 LangGraph nodes, the FastAPI API (4 routers), the Docker sandbox executor, GitHub clone/PR logic, Supabase CRUD + `db/migrations/001_initial_schema.sql`, the dual-provider LLM client, and a real React/Vite frontend **are all written** — 104 files in a single commit `b064cc3 "in progress"`.
- **Nothing has been run or verified end-to-end:** no Python venv, no `frontend/node_modules`, one untested commit, and several latent bugs are already visible in the source.

So the **core roadmap (Phases 0-8)** is "make it real": verify → fix → harden → fill gaps → showcase cloud → deploy — following the PRD's phase order. On top of that, a **scale-up roadmap (Phases 9-13)** turns a single working tool into a multi-surface product with a signature technical differentiator. This directly answers "is this just a terminal project?" — **no: web dashboard + GitHub App + CLI + GitHub Action**, with mutation testing as the headline feature.

**Locked decisions (from user Q&A):**
1. **Cost posture = STRICT $0 free-tier.** SSM Parameter Store (free), **never** Secrets Manager. **No NAT gateway** (public-subnet Fargate, no inbound). Local Docker is the default sandbox; Fargate is opt-in behind a flag. Per-run **token budget + kill switch**. **AWS Budgets alarm at $1.** I pause for explicit approval before provisioning anything billable.
2. **AWS = targeted showcase.** Ephemeral **Fargate (ECS)** sandboxes for untrusted tests, **S3** for artifacts/logs, **SSM** for secrets, **ECR** for sandbox images. Keep Railway (API), Vercel (UI), Supabase (DB/auth).
3. **Build order = phase-by-phase per PRD** (verify/harden), then scale-up phases.
4. **LLM = Gemini 2.0 Flash default**, provider is a config switch (`gemini | anthropic | bedrock`).
5. **Surfaces to build:** Web dashboard (exists) + **GitHub App (flagship)** + **CLI** + **GitHub Action**. VS Code extension deferred to v2 backlog.
6. **Signature feature = mutation testing**, built into the core; then code-review pass, live-streaming UI, diff-aware+RAG staged after.

**Intended outcome:** a working, verified, deployed product where a real public repo flows end-to-end to an opened PR (with mutation-verified tests and an inline code review), watchable live in a React dashboard, runnable via web/App/CLI/Action, on a $0 AWS Fargate/S3 footprint — fully documented for portfolio review.

---

## Cross-cutting concerns (built into the core, not bolted on)

**Bug-fix backlog (real defects found in committed code):**

| # | File | Issue | Fix in |
|---|------|-------|--------|
| B1 | `llm/client.py:22-33` | `async def generate` makes **blocking** SDK calls — blocks the event loop; concurrent runs serialize. | Phase 2 |
| B2 | `llm/client.py` + `agent/nodes/generate_tests.py:37` | LLM response stored **raw** as the test file; ```` ``` ```` fences never stripped. `llm/parsers.py` exists but is **not wired in**. | Phase 2 |
| B3 | `llm/client.py:29` | Outdated Anthropic model id; no Bedrock branch. | Phase 2 |
| B4 | `agent/nodes/save_results.py:5,24` | Imports `create_correction_records` but **never calls it** — corrections never persisted. | Phase 4/7 |
| B5 | `agent/nodes/generate_tests.py:16,17` | Path built with f-string `/`; file opened without `encoding="utf-8"`. | Phase 2 |
| B6 | `api/main.py` | CORS open; rate-limit middleware stubbed (PRD wants max 5 concurrent runs/user). | Phase 7/8 |
| B7 | `llm/client.py` | No rate-limit guard / retry-backoff on LLM calls (CLAUDE.md: rate-limit all APIs, fail closed). | Phase 2 |

**Cost meter (mandatory, part of the $0 posture):** count input/output tokens per LLM call in `llm/client.py`, accumulate per run on `AgentState`, enforce a per-run **token budget with a hard kill switch**, persist `tokens_used` + `est_cost_usd` to the `runs` table, and surface it in the dashboard. Built in Phase 2, displayed in Phase 6.

---

## Core roadmap (Phases 0-8) — verify & harden the existing v1.0.0

### Phase 0 — Ground truth (make it installable/runnable) — prerequisite
- venv + `pip install -r requirements.txt`; `cd frontend && npm install`.
- `.env` from `.env.example` with **free-tier** Gemini key only; confirm `core/config.py` loads.
- Run `pytest tests/ -q` + `ruff check .` for a **baseline pass/fail map**; boot `uvicorn api.main:app` + `npm run dev`; hit `/api/health`.
- **Success:** deps install clean, app boots, baseline captured.

### Phase 1 — Foundation (verify) — PRD 1-8
- Verify `github_integration/cloner.py` on a real small public repo; verify `parsing/analyzer.py` returns a sane `ast_map`; `docker-compose up` brings up api + postgres.
- **Success:** clone + parse a real repo; ast_map shows functions/classes/imports/complexity; health green.

### Phase 2 — Test generation + LLM hardening + cost meter (fix B1-B3,B5,B7) — PRD 9-14
- Wire `llm/parsers.py` to strip fences (B2); non-blocking LLM via `asyncio.to_thread`/async SDK (B1); fix model ids + add `bedrock` config branch (B3); add LLM rate-limit/backoff + cost meter + token budget (B7); fix path/encoding (B5). Verify on **5 real Python files**; extend to JS/TS jest.
- **Success:** generated tests parse (`ast.parse`) and reference real functions; token/cost tracked per run.

### Phase 3 — Execution + AWS Fargate sandbox + S3 ($0 design) — PRD 15-20
- Verify the **local Docker** path end-to-end (build images, run, parse, coverage, 60s timeout kill).
- **Executor backend abstraction** (`local` | `fargate`) via config; **local stays default**.
- **Fargate backend ($0-safe):** ephemeral ECS task in a **public subnet, no inbound, no NAT**; image from **ECR**; task auto-stops after run. (Local Docker keeps the strict no-network isolation for dev; production no-egress via VPC endpoints is a documented v2 option.)
- **S3 artifacts:** persist generated tests, raw output, coverage reports; store S3 keys on DB records.
- **Cost guard:** Fargate/ECR/S3 behind flag; I confirm before provisioning; Budgets alarm @ $1.
- **Success:** identical results for `local` and `fargate`; artifacts in S3; cleanup verified both backends.

### Phase 4 — Self-correction loop (verify + fix B4) — PRD 21-26
- Verify diagnose→patch→re-execute terminates (success / max_iterations / **same-error-twice** — may need adding); fence-strip patches; persist corrections (B4). Measure on **10 broken tests**; tune `max_iterations`.
- **Success:** resolves ≥80% of seeded failures, always terminates, corrections rows written.

### Phase 5 — GitHub PR integration (verify) — PRD 27-30
- With a free GitHub PAT, open a real PR on a throwaway repo; verify branch/commit/markdown PR body; handle edge cases (branch exists, no changes, permission denied).
- **Success:** a real clean PR with correct metadata.

### Phase 6 — Frontend dashboard (verify + wire + cost meter UI) — PRD 31-36
- `npm install`, run against live API; wire real data; ErrorBoundary + fetch catches; 3s polling; error states with copy-to-clipboard; **show token/cost meter per run**.
- **Success:** dashboard lists repos, triggers a run, shows live status/results/coverage/cost.

### Phase 7 — DB & persistence + security hardening (fix B4,B6) — PRD 37-41
- Free Supabase project; apply schema; **RLS** (own repos/runs only); **indexes on FK columns**; GitHub OAuth via Supabase Auth (encrypted tokens); Realtime on `runs`; verify all nodes persist; tighten CORS to env allowlist + concurrent-run rate limit (B6).
- **Success:** a full run persists across 4 tables; RLS blocks cross-user reads; dashboard shows history.

### Phase 8 — Deploy, IaC, CI/CD, launch + AWS ops ($0) — PRD 42-48
- FastAPI → Railway; frontend → Vercel.
- **AWS ops ($0):** secrets via **SSM Parameter Store** (`core/config.py` SSM loader for prod); **CloudWatch** logs/metrics + run-failure alarm; minimal **Terraform/CDK** provisioning ECR + S3 + Fargate task def + IAM + **Budgets alarm**.
- Extend CI/CD (lint+test, deploy on main, push sandbox images to ECR). README w/ **architecture diagram showing the Fargate/S3 path** + demo GIF + badges; 2-min demo video; full-flow test on 3 repos; tag **v1.0.0**.
- **Success:** public URL live; one click → real run on Fargate+S3 → PR; infra reproducible from IaC; still $0.

---

## Scale-up roadmap (Phases 9-13) — bigger product, signature differentiator

### Phase 9 — Mutation testing (SIGNATURE feature) — v1.1
The headline: prove generated tests are *meaningful*, not just coverage-padding.
- Integrate **mutmut/cosmic-ray** (Python) and **Stryker** (JS/TS) into the sandbox backend; run mutants against the generated suite; compute a **mutation score** (% mutants killed); feed survivors back into the self-correction loop to strengthen weak tests.
- Surface mutation score on runs + dashboard; add to PR body.
- **Cost-safe:** runs in the existing local Docker / Fargate sandbox ($0); bounded mutant count + timeout.
- **Success:** for a sample repo, the agent reports a mutation score and improves it across iterations.

### Phase 10 — Code-review pass (makes the name true) — v1.1
- New agent branch: LLM reviews the diff/target files for bugs, security, and style; produces structured findings with severity; posts **inline PR comments** (reuses `github_integration` + existing PR infra).
- New `review_findings` table; shown in dashboard + a `/code-review`-style report.
- **Success:** on a repo with a seeded bug, the agent flags it as an inline PR comment.

### Phase 11 — Product surfaces: CLI → GitHub Action → GitHub App — v1.2
- **CLI** (`cli/` via Typer/Click): `agent test <path|repo>`, `agent review <pr>`; reuses the compiled `agent_workflow`. Foundation for the Action.
- **GitHub Action:** thin Docker action wrapping the CLI; drop-in CI step; publish to Marketplace.
- **GitHub App (flagship):** install on any repo, webhook → auto-run on PRs, inline comments + status checks; OAuth + HMAC verification (infra partly exists in `github_integration/webhook_verify.py`).
- **Success:** the same run is triggerable from web, CLI, an Action workflow, and an installed App on a PR.

### Phase 12 — Live-streaming run UI + analytics — v1.2
- **SSE/WebSocket** stream of agent step transitions (LangGraph events) → a live run view ("watch the agent think"); the demo-video centerpiece.
- **Analytics dashboard:** runs over time, success rate, coverage trend, mutation score trend, **cost per run**; shareable public run-report pages.
- **Success:** triggering a run streams steps live; analytics render real historical data.

### Phase 13 — Stretch backlog — v2
- **Diff-aware PR mode** (test only changed lines) + **RAG over the codebase** (pgvector in Supabase) for context-aware generation.
- **SQS job queue + horizontal Fargate workers** (true concurrency at scale — note: SQS free tier covers this, still $0).
- **VS Code extension** (deferred surface).
- Additional languages (Go/Java/Rust via tree-sitter).

---

## Cost-control design (enforced everywhere; target = $0)
- **Free tiers:** Gemini free quota, Supabase free, Vercel free, Railway hobby, GitHub free, AWS 12-mo free tier (S3 5GB, CloudWatch basic, ECR 500MB, Fargate limited).
- **Traps avoided:** no NAT gateway (public-subnet Fargate); **SSM Parameter Store not Secrets Manager**; Fargate behind a flag (local Docker default); SQS (Phase 13) stays in free tier.
- **Guardrails:** per-run token budget + kill switch; max repo size / file caps; max iterations + bounded mutant count; **AWS Budgets alarm @ $1**; approval gate before any billable provisioning.
- **Cost as a feature:** live token/$ meter per run in the UI = cost observability.

---

## Verification strategy
- **Per phase:** the "Success" check above, proven before moving on.
- **Automated:** `pytest tests/` + `ruff check .` green in CI.
- **Headline E2E demo:** trigger on a real small public Python repo → clone→parse→generate→(Fargate)execute→mutation-score→self-correct→code-review→PR → watch it live on the dashboard with coverage + mutation + cost.
- **AWS:** Fargate task starts/stops per run; artifacts in S3; secrets resolve from SSM; CloudWatch alarm fires on a forced failure; Budgets shows $0.

---

## Critical files (most-touched / new)
- Agent: `agent/graph.py`, `agent/state.py`, `agent/nodes/*.py`, **new** `agent/nodes/code_review.py` (Ph10)
- LLM: `llm/client.py` (cost meter, async, bedrock), `llm/parsers.py`, `llm/prompts/*.py`
- Sandbox: `sandbox/executor.py`, `sandbox/result_parser.py`, `sandbox/dockerfiles/*`, **new** `sandbox/backends/{local,fargate}.py`, **new** `sandbox/mutation.py` (Ph9)
- API: `api/main.py`, `api/routers/*.py` (+ SSE endpoint Ph12), `api/dependencies.py`, `api/middleware/*`
- DB: `db/crud/*`, `db/models/*`, `db/migrations/*` (RLS, indexes, `review_findings`, mutation/cost columns)
- Config/infra: `core/config.py` (SSM loader), `.github/workflows/*`, **new** `infra/` (Terraform/CDK), **new** `cli/` (Ph11), **new** `action.yml` (Ph11)
- Frontend: `frontend/src/{pages,components,hooks,api}/*` (+ live stream + analytics Ph12)

## Risks / open items
- **Docker required** for Phase 3 local path — confirm Docker Desktop on this Windows box.
- **Same-error-twice termination** (PRD del. 23) likely needs adding, not just verifying.
- **GitHub App vs PAT** — PAT for early verification, App in Phase 11.
- Memory notes (`phase1_checklist.md` "verified working") look optimistic vs the unrun state; Phase 0/1 establish true baselines and I'll update memory accordingly.
- Specs per phase mirrored into `.claude/todo.md`; corrections/lessons into `.claude/lessons.md`, per project convention.
