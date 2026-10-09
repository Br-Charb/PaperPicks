SHELL := /bin/bash
.DEFAULT_GOAL := help

.PHONY: help install test run deploy down generate_dot_env

help:
	@echo "Run from backend/: make install, make run, make test, make deploy, make down"

install: generate_dot_env
	uv sync --extra dev

test:
	uv run --extra dev python -m pytest

run: generate_dot_env
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

deploy: generate_dot_env
	docker compose up --build -d

down:
	docker compose down

generate_dot_env:
	@if [[ ! -e .env ]]; then cp .env.example .env; fi
