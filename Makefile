.PHONY: install test test-backend test-frontend demo demo-online up down

install:
	python -m pip install -e "./backend[dev]"
	npm --prefix frontend install

test:
	python scripts/test_all.py --skip-install

test-backend:
	python scripts/test_all.py --backend-only --skip-install

test-frontend:
	python scripts/test_all.py --frontend-only --skip-install

demo:
	python scripts/demo.py

demo-online:
	python scripts/demo.py --base-url http://localhost:8080

up:
	docker compose up --build

down:
	docker compose down --remove-orphans
