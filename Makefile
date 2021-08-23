.PHONY: type
type:
	@echo "Running mypy"
	@pipenv run mypy .

.PHONY: check-lint
check-lint:
	@echo "Running black"
	@pipenv run black --check .
	@echo "Running flake"
	@pipenv run flake8

.PHONY: lint
lint:
	@echo "Running black"
	@pipenv run black .
	@echo "Running flake"
	@pipenv run flake8