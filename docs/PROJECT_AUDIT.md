# Project Audit — Israeli Tech News Intelligence

_Audit date: 2026-10-12 · Branch: `main` @ `f095956` · Scope: read-only analysis (no application code changed)_

**Legend:** ✅ **Verified** = checked by reading code or running a command. ⚠️ **Assumption** = inferred and not executed (it usually needs Postgres or a live API).

---

## 1. Project Overview

**Purpose:** a batch backend pipeline. It pulls Israeli tech news from RSS, stores it in PostgreSQL, enriches each article with OpenAI (summary, category, tags, importance, Israel relevance), builds a ranked digest and sends it to WhatsApp through Twilio.

**Architecture (as implemented):** the pipeline is a set of **standalone scripts** that you run by hand, one after another. There is no orchestrator.

```
scripts/seed_sources.py ─► scripts/run_ingestion_once.py ─► scripts/test_single_article_enrichment.py
                                   │                                   │
                     SourceFetchService                         EnrichmentService
              (RSSFetcher→RSSParser→RSSNormalizer)          (OpenAIClient + prompts)
                     ArticleRepository                        EnrichmentRepository
                                   ▼                                   ▼
                          PostgreSQL: sources / articles / article_enrichments
                                                   │
                     scripts/generate_digest.py / scripts/send_digest_to_whatsapp.py
                         DigestRepository → DigestBuilder → WhatsAppSender (Twilio)
```

| Layer | Files |
|---|---|
| Config / infra | `app/core/config.py` (pydantic-settings), `app/core/database.py`, `app/core/logging.py`, `app/core/redis.py` |
| Models | `app/models/source.py`, `article.py`, `article_enrichment.py` |
| Repositories | `app/repositories/{source,article,enrichment,digest}_repository.py` |
| Ingestion | `app/services/ingestion/{rss_fetcher,rss_parser,normalizer,source_fetch_service}.py`, `app/services/processing/{hasher,url_canonicalizer}.py` |
| AI | `app/services/ai/{openai_client,prompts,enrichment_service}.py` |
| Ranking / delivery | `app/services/ranking/digest_builder.py`, `app/services/delivery/whatsapp_sender.py` |
| API | `app/main.py`, `app/api/v1/endpoints/health.py` (only `/` and `/api/v1/health`) |
| Migrations | `migrations/versions/` (3 revisions, linear; head = `8231d15c168e`) |

**Tech stack:** Python 3.9.6 (venv), FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL 16 and Redis 7 (docker-compose), httpx, feedparser, OpenAI SDK 2.30 (Responses API), Twilio 9.10.

---

## 2. Current Progress

| Feature | Status | Evidence |
|---|---|---|
| RSS fetch / parse / normalize | ✅ Done | Smoke test: parser returned 2/2 entries; tracking params and fragment stripped; HTML cleaned |
| URL canonicalization + SHA-256 | ✅ Done | `url_canonicalizer.py`, `hasher.py` |
| Dedup by `canonical_url` | ✅ Done | `source_fetch_service.py:51` |
| Persistence + migrations | ✅ Done | `alembic upgrade head --sql` renders a clean linear chain |
| AI enrichment (single article) | 🟡 Partial | Only `scripts/test_single_article_enrichment.py` exists. It enriches **only the newest article** |
| Batch enrichment of pending articles | ❌ Missing | No repository query for "articles without enrichment"; `Article.status` is never moved past `"ingested"` |
| Digest generation | 🟡 Partial | Works, but always takes the **all-time** top 5 (`digest_repository.py:13`). No time window, no "already sent" tracking, no Israel-relevance filter |
| WhatsApp delivery | 🟡 Partial | Works per commit `d8edba3`. The Hebrew one-message-per-article format is **uncommitted**. No error handling |
| One-command pipeline | ❌ Missing | Priority #1 in `CLAUDE.md` |
| Automated tests | ❌ Missing | `tests/unit/` and `tests/integration/` are empty; pytest isn't installed. The `scripts/test_*.py` files are manual network/DB scripts, not tests |
| Structured JSON output | 🟡 Partial | `openai_client.py:26` runs `json.loads` on free text. There is no JSON schema or `text.format`, which goes against the "structured JSON" rule in `CLAUDE.md` |
| Fuzzy dedup (`title_hash`, `is_duplicated`) | ❌ Unused | Columns exist but nothing reads them |
| API beyond health | ❌ None | Fine for the MVP |

---

## 3. Development History

✅ **Git (12 commits, 2026-04-03 → 2026-05-14):** scaffold (`3c66f7e`) → RSS pipeline (`eff15fe`) → normalizer (`0a96f08`) → ingestion done (`2af38ab`) → AI layer (`7d6a55e`, `c9541b5`) → digest (`41e0e52`) → WhatsApp (`d8edba3`) → README (`f095956`). Commit messages are inconsistent (some use `feat:`/`chore:`, others are free text, and some have typos).

✅ **Uncommitted work (last edited around Aug 2026). This is important:**
- `app/api/v1/endpoints/health.py`: fixes a **committed bug**. `text["Select 1"]` raised `TypeError`, so `/health` always reported the DB as down.
- `app/services/ingestion/rss_parser.py`: fixes a **committed bug**. `return entries` was indented inside the loop, so **only the first entry of every feed was ever returned** in the committed code.
- `prompts.py` and `digest_builder.py`: switch to Hebrew output, shorter summaries and one WhatsApp message per article.
- `scripts/send_digest_to_whatsapp.py`: sends multiple messages.
- `output/latest_digest.txt`: regenerated output. It is a generated file but is tracked in git.
- `CLAUDE.md` is untracked.

✅ **Docs:** `README.md`, `CLAUDE.md`, `docs/architecture.png`. **TODO/FIXME comments:** none found.

✅ **Claude Code session history:** none from before this audit (only the current session exists in `~/.claude/projects/...`). The memory directory is empty.

---

## 4. Code Quality

### Bugs (✅ verified by reading code unless noted)
1. **Committed `HEAD` is broken** (see §3). Anyone who clones the repo gets the one-entry-per-feed parser and the always-failing health check.
2. **One bad entry rolls back a whole source.** `source_fetch_service.py:59-72` commits once per source. If any entry has no title, the normalizer returns `title=None` (verified), the `NOT NULL` constraint fails, and every article from that feed is rolled back. ⚠️ The DB failure itself is an assumption; the `None` title is verified.
3. **Non-RFC-822 dates are lost.** `normalizer.py:65` uses `parsedate_to_datetime`. ISO-8601/Atom dates return `None` (verified). `feedparser` already provides `published_parsed`, which handles both.
4. **The LLM response is never validated.** `openai_client.py:26-27`: if the model wraps its output in markdown fences or returns bad JSON, `json.loads` raises and nothing catches it. There is no check on the result's shape or the score range.
5. **The digest repeats old news.** `digest_repository.py` has no date filter or sent flag. Also, `published_at DESC` puts NULLs first in Postgres.
6. **No error handling on external calls.** `whatsapp_sender.py` and `openai_client.py` don't catch Twilio or OpenAI exceptions, which goes against the `CLAUDE.md` error-handling rule.
7. **RSS timeout is 500 s** (`rss_fetcher.py:9`), so one stalled feed can block a run for more than 8 minutes. The value is hardcoded rather than read from Settings.
8. **Migrations can't apply to a non-empty DB.** `49560768f142` adds `sources.category NOT NULL` and `8231d15c168e` adds `articles.title/url NOT NULL`, all without `server_default`. They only work on empty tables.
9. **Duplicate enrichments are only prevented in code.** `article_enrichments.article_id` has no unique constraint.

### Technical debt
- `requirements.txt` is a raw `pip freeze`. It includes **`MyApplication==0.1.0`**, a junk PyPI placeholder package ("Useful towel-related stuff"), plus Flask/Werkzeug/structlog, which nothing uses. pytest is missing. `pyproject.toml` is empty.
- **`.env.example` is gitignored and was deleted from the repo** (`57d53ef`). A fresh clone has no config template. The README env section shows `DATABASE_URL`, which `Settings` **does not read**: it builds the URL from `POSTGRES_*`.
- The README says scripts live in `app/scripts/`, but they're actually in the root `scripts/`. The README also doesn't say that enrichment handles only one article.
- Scripts use `print` instead of logging. Only `run_ingestion_once.py` calls `setup_logging()`. There's a `"Diges saved"` typo at `generate_digest.py:30`.
- Every script repeats the same `sys.path.insert` hack, even though `python -m scripts.x` makes it unnecessary.
- Redis is wired into `core/redis.py` and `/health` but isn't used anywhere else (Redis is out of scope per `CLAUDE.md`). As a result, `/health` reports "degraded" whenever Redis is down.
- Small items: `enrichment_date` typo (`enrichment_repository.py:19`); the `list[Type[Source]]` type hint is wrong (`source_repository.py:12`); `datetime.utcnow()` naive timestamps go into `timestamptz` columns; `last_fetched_at` and `poll_interval_minutes` are never used; `debug=True` by default; `docker-compose.yml` uses the obsolete `version:` key; `docker/` and `app/schemas/common.py` are empty.

### Architecture issues
- There is no pipeline/orchestration service. The flow lives across 6 scripts.
- Services create their own dependencies (`OpenAIClient()`, `Client()`) instead of receiving them, which makes unit testing harder. This is cheap to fix with constructor injection.
- `seed_sources.py` queries the DB directly instead of going through `SourceRepository`.

---

## 5. Run Status

| Check | Result |
|---|---|
| venv (`.venv`, Python 3.9.6) | ✅ Present. `pip check` passes. ⚠️ Python 3.9 reached end of life in Oct 2025; consider moving to 3.11+ |
| Compile / import `app.main`, all services | ✅ OK |
| Offline smoke test (parser, normalizer, canonicalizer, digest builder) | ✅ OK (uncommitted versions) |
| Alembic chain | ✅ Single head `8231d15c168e`; offline SQL renders |
| Docker | ❌ Docker Desktop is installed but the daemon **is not running** |
| PostgreSQL | ❌ Nothing is listening on `:5432`, and Postgres isn't installed locally. ⚠️ The `postgres_data` volume probably still holds earlier data, but this wasn't checked |
| Redis | ✅ Homebrew `redis` is running on `:6379` (not Docker). ⚠️ It **will clash** with the compose `redis` port mapping |
| `.env` | ✅ Present (not committed). It has every key `Settings` needs, including `OPENAI_MODEL` |
| OpenAI / Twilio live calls | ⚠️ Not exercised (they cost money and send real messages) |

**Expected local start** (⚠️ not executed): start Docker Desktop → `docker compose up -d postgres` (skip `redis`, or stop the brew one) → `alembic upgrade head` → `python -m scripts.seed_sources` → `python -m scripts.run_ingestion_once` → … in the README order.

---

## 6. Roadmap (prioritized)

**P0: Stabilize (about 1 hour)**
1. Commit the uncommitted bug fixes (parser and health check) and the Hebrew formatting as separate commits. Add `CLAUDE.md`. Stop tracking `output/`.
2. Clean up `requirements.txt` (remove `MyApplication`, Flask and structlog; add `pytest`). Restore a committed `.env.example` and remove it from `.gitignore`.
3. Bring the stack up and run the full README flow once to confirm it works end to end.

**P1: Finish the MVP (matches the `CLAUDE.md` priorities)**
4. **Batch enrichment:** add `ArticleRepository.get_pending_enrichment(limit)` and `EnrichmentService.enrich_pending()`, with per-article try/except and setting `status="enriched"`/`"failed"`.
5. **One-command pipeline:** add `scripts/run_pipeline.py` with a small `PipelineService` (ingest → enrich pending → build → send), plus `--dry-run` / `--no-send` flags.
6. **Reliable structured output:** use a Responses API JSON schema (`text.format`), check the result with a Pydantic model, and handle failures.
7. **Digest correctness:** only include articles from the last N hours, filter `is_israeli_relevant`, and either add `sent_at` tracking or keep it simple with the time window. Use `NULLS LAST`.
8. **Error handling and logging:** wrap OpenAI and Twilio calls, replace `print` with logging in scripts, and move the fetch timeout into Settings (around 15 s).
9. **Ingestion robustness:** skip entries without a title or link, use `published_parsed`, and commit per article or use a savepoint.

**P2: Interview-ready polish**
10. **Tests (highest value for interviews):** unit tests for `URLCanonicalizer`, `RSSNormalizer`, `RSSParser` (fixture XML), `DigestBuilder`, and `EnrichmentService` with a mocked client. Add one integration test for repositories.
11. Add a GitHub Actions workflow that runs `ruff` and `pytest`.
12. README: fix the env vars and folder layout, add "Quickstart in 5 commands", a sample digest screenshot, and a "Design decisions & trade-offs" section.
13. Optional: a `Dockerfile` plus an `app` service in compose; add a unique constraint on `article_enrichments.article_id` (new migration); upgrade to Python 3.11.

**Talking points to prepare:** why dedup uses the canonical URL; why the repository/service split; how you'd prevent LLM hallucination or malformed output (schema + validation); idempotency (re-running the pipeline doesn't double-send); what you'd add with Redis/Celery and why you deliberately didn't.
