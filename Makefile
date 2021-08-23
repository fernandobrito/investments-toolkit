.PHONY: type
type:
	@echo "Running mypy"
	@pipenv run mypy src/

.PHONY: check-lint
check-lint:
	@echo "Running black"
	@pipenv run black --check src/
	@echo "Running flake"
	@pipenv run flake8 src/

.PHONY: lint
lint:
	@echo "Running black"
	@pipenv run black src/
	@echo "Running flake"
	@pipenv run flake8 src/