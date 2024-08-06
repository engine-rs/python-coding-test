install:
	poetry install --no-root

dev:
	poetry run fastapi dev src/main.py

test:
	poetry run python src/tests.py

check_code:
	echo "Running Black..."
	poetry run black .

	echo "Running Flake8..."
	poetry run flake8 .

	echo "Running Pylint..."
	poetry run pylint src/main.py src/auth.py src/database_service.py src/models.py src/tests.py

	echo "Running Mypy..."
	poetry run mypy src/main.py src/auth.py src/database_service.py src/models.py src/tests.py

check_dev:
	sh check_dev_server.sh

.PHONY: install dev test check_code check_dev