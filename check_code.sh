#!/bin/bash

echo "Running Black..."
poetry run black .

echo "Running Flake8..."
poetry run flake8 .

echo "Running Pylint..."
poetry run pylint src/main.py src/auth.py src/database_service.py src/models.py src/tests.py

echo "Running Mypy..."
poetry run mypy src/main.py src/auth.py src/database_service.py src/models.py src/tests.py