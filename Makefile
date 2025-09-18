.PHONY: help install lint format test run migrate makemigrations shell

help:
	@echo "Available commands:"
	@echo "  make install         Install dependencies"
	@echo "  make lint            Run flake8 linting"
	@echo "  make format          Auto-format with black & isort"
	@echo "  make test            Run pytest with coverage"
	@echo "  make makemigrations  Create new Django migrations"
	@echo "  make migrate         Apply migrations"
	@echo "  make shell           Open Django shell"
	@echo "  make run             Run development server"

install:
	pip install -r requirements.txt
	pip install black isort flake8 pytest pytest-django coverage pre-commit

lint:
	flake8 .

format:
	black .
	isort .

test:
	coverage run -m pytest --ds=movie_backend.settings --disable-warnings --maxfail=3
	coverage report -m

makemigrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

shell:
	python manage.py shell

run:
	python manage.py runserver
