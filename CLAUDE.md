# CLAUDE.md

# Israeli Tech News Intelligence System

## Project Overview

This project is an AI-powered backend system that ingests technology news from RSS feeds, enriches articles using Large Language Models (OpenAI), ranks important stories, generates news digests, and delivers them automatically via WhatsApp.

The goal is to build a production-quality backend pipeline that demonstrates clean architecture, modular design, AI integration, and real-world software engineering practices.

---

# Current Architecture

RSS Feed
→ Fetch (httpx)
→ Parse (feedparser)
→ Normalize
→ Save Articles (PostgreSQL)
→ AI Enrichment (OpenAI)
→ Save Article Enrichments
→ Generate Digest
→ Send WhatsApp (Twilio)

---

# Tech Stack

Backend
- Python 3.9+
- SQLAlchemy
- Alembic
- PostgreSQL
- Docker

AI
- OpenAI Responses API
- Structured JSON Outputs
- Prompt Engineering

External APIs
- RSS Feeds
- Twilio WhatsApp API

---

# Architecture Principles

Always follow these principles.

## Repository Pattern

Repositories are responsible only for database access.

Repositories should never contain business logic.

Business logic belongs inside services.

---

## Service Layer

Services orchestrate the application.

Examples:

- SourceFetchService
- EnrichmentService
- DigestBuilder
- WhatsAppSender

Keep services focused and modular.

---

## Models

SQLAlchemy models should remain simple.

Avoid business logic inside models.

---

## Configuration

Never hardcode:

- API keys
- Tokens
- URLs
- Credentials

Always use the Settings object.

---

## Error Handling

Catch external API failures.

Log meaningful errors.

Never expose secrets in logs.

---

## Logging

Prefer logging over print().

Use informative log messages.

Example:

INFO:
- Fetching RSS feed...
- Parsed 20 articles...
- Sending WhatsApp digest...

ERROR:
- OpenAI request failed...
- Twilio delivery failed...

---

# Code Style

Always:

- Use type hints.
- Write small methods.
- Prefer readability.
- Keep functions focused.
- Avoid duplicated code.
- Follow PEP8.

---

# AI Layer

The AI layer must produce structured JSON.

Never rely on free-form text.

Prompt changes should remain isolated inside:

app/services/ai/prompts.py

The OpenAI client should remain generic.

---

# Current Project Status

Completed:

✅ RSS fetching

✅ RSS parsing

✅ Normalization

✅ URL canonicalization

✅ SHA-256 hashing

✅ PostgreSQL persistence

✅ OpenAI enrichment

✅ Digest generation

✅ WhatsApp delivery

---

# Current MVP Goal

Finish the Minimum Viable Product.

Current priorities:

1. Build one-command pipeline
2. Batch enrich pending articles
3. Improve WhatsApp formatting
4. Improve logging
5. Polish README

Do NOT introduce major new features before finishing the MVP.

---

# Out of Scope (For Now)

Do not implement unless explicitly requested:

- Redis
- Celery
- Kafka
- RAG
- Vector databases
- Dashboard
- Scheduler
- Multi-agent architecture

Focus on completing the MVP first.

---

# Workflow

Before making changes:

1. Understand the existing architecture.
2. Reuse existing code whenever possible.
3. Avoid unnecessary rewrites.
4. Preserve the modular structure.
5. Explain significant architectural decisions before implementing them.

---

# Communication Style

When helping with implementation:

- Explain the reasoning first.
- Then implement.
- Keep explanations concise.
- Prefer clean, production-style solutions.
- If multiple approaches exist, recommend the simplest maintainable one.

Avoid overengineering.

The priority is a clean MVP that is easy to explain during software engineering interviews.