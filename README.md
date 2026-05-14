# Israeli Tech News Intelligence System

An AI-powered backend system that ingests real-time technology news, enriches articles using Large Language Models (LLMs), ranks important stories, and automatically delivers curated news updates through WhatsApp.

---

## Overview

This project was built to simulate a real-world AI-powered data pipeline used in modern backend and information intelligence systems.

The system continuously:

1. Fetches technology news from RSS sources
2. Parses and normalizes article data
3. Stores articles in PostgreSQL
4. Enriches articles using OpenAI
5. Generates ranked news digests
6. Sends updates automatically to WhatsApp

The project focuses on:

* Backend architecture
* AI integration
* Data pipelines
* External API integrations
* Modular software design
* Real-world engineering practices

---

## Features

### News Ingestion Pipeline

* RSS feed ingestion using `httpx`
* Feed parsing and normalization
* URL canonicalization
* SHA-256 content hashing
* Duplicate prevention
* PostgreSQL persistence

### AI Enrichment Layer

* OpenAI integration
* Structured JSON outputs
* AI-generated summaries
* Importance scoring
* Technology categorization
* Israeli relevance detection
* Tag generation

### Delivery Layer

* Digest generation
* Ranking based on article importance
* WhatsApp delivery using Twilio

---

## End-to-End Flow

```text
RSS Feed
   ↓
Fetch + Parse
   ↓
Normalize
   ↓
Save Articles
   ↓
AI Enrichment
   ↓
Generate Digest
   ↓
WhatsApp Delivery
```

---

## Architecture

![Architecture Diagram](docs/architecture.png)

The system follows a modular service-oriented backend architecture.

### Main Components

#### Ingestion Layer

Responsible for:

* Fetching RSS feeds
* Parsing XML feeds
* Normalizing article data
* Deduplication

#### AI Layer

Responsible for:

* OpenAI communication
* Prompt engineering
* Structured enrichment generation
* Article intelligence extraction

#### Persistence Layer

Responsible for:

* PostgreSQL storage
* Repository abstraction
* Data access logic
* Entity relationships

#### Delivery Layer

Responsible for:

* Digest creation
* WhatsApp notifications
* Message formatting

---

## Tech Stack

### Backend

* Python 3.9+
* SQLAlchemy
* Alembic
* PostgreSQL

### AI

* OpenAI API
* Structured prompting
* JSON response parsing

### Messaging

* Twilio WhatsApp API

### Infrastructure

* Docker
* Docker Compose

---

## Project Structure

```text
app/
 ├── core/
 ├── models/
 ├── repositories/
 ├── services/
 │    ├── ai/
 │    ├── delivery/
 │    ├── ingestion/
 │    ├── processing/
 │    └── ranking/
 └── scripts/
```

---

## Database Design

### Sources

Stores RSS source configuration.

### Articles

Stores normalized article data.

### Article Enrichments

Stores AI-generated intelligence:

* summaries
* importance score
* tags
* categories
* Israeli relevance

---

## Example AI Enrichment Output

```json
{
  "category": "Quantum Computing",
  "short_summary": "An Israeli startup introduced a new scalable quantum computing architecture.",
  "why_it_matters": "The innovation could accelerate practical quantum computing adoption.",
  "tags": ["quantum", "startup", "Israel"],
  "importance_score": 8,
  "is_israeli_relevant": true
}
```

---

## Example WhatsApp Digest

```text
Israeli Tech News Digest

1. Israeli startup reveals breakthrough quantum architecture
Summary: ...
Why it matters: ...
Importance: 8
```

---

## Running the Project

### Start infrastructure

```bash
docker compose up -d
```

### Run migrations

```bash
alembic upgrade head
```

### Seed RSS sources

```bash
python -m scripts.seed_sources
```

### Run ingestion

```bash
python -m scripts.run_ingestion_once
```

### Run AI enrichment

```bash
python -m scripts.test_single_article_enrichment
```

### Generate digest

```bash
python -m scripts.generate_digest
```

### Send digest to WhatsApp

```bash
python -m scripts.send_digest_to_whatsapp
```

---

## Environment Variables

Example `.env` configuration:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/israeli_tech_news

OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4.1-mini

TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
WHATSAPP_TO=whatsapp:+972XXXXXXXXX
```

---

## Engineering Concepts Demonstrated

* Modular backend architecture
* Repository pattern
* AI system integration
* Structured LLM outputs
* Data normalization
* Deduplication strategies
* External API integrations
* Pipeline orchestration
* Environment-based configuration
* Database migrations
* Dockerized infrastructure

---

## Future Improvements
Planned improvements include:

* Redis-based queue workers
* Scheduled background jobs
* Advanced ranking algorithms
* Better RSS coverage
* Vector search and RAG
* Multi-language support
* Web dashboard
* Delivery analytics
* Retry and observability systems
