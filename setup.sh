#!/bin/bash

mkdir -p app/api/v1/endpoints
mkdir -p app/core
mkdir -p app/models
mkdir -p app/schemas
mkdir -p app/repositories
mkdir -p app/services/ingestion
mkdir -p app/services/processing
mkdir -p app/services/ai
mkdir -p app/services/ranking
mkdir -p app/services/delivery
mkdir -p app/workers/jobs
mkdir -p docs
mkdir -p migrations/versions
mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p scripts
mkdir -p docker

touch app/main.py
touch app/api/v1/endpoints/health.py
touch app/core/config.py
touch app/core/database.py
touch app/core/redis.py
touch app/core/logging.py
touch app/models/base.py
touch app/schemas/common.py
touch .env.example
touch README.md
touch pyproject.toml
touch docker-compose.yml
touch alembic.ini

echo "Project structure created 🚀"
