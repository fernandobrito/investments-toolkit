APP_NAME?=investments-toolkit
REGISTRY?=eu.gcr.io/$(GCP_PROJECT_NAME)
IMAGE=$(REGISTRY)/$(APP_NAME)
SHORT_SHA?=$(shell git rev-parse --short HEAD)
VERSION?=$(SHORT_SHA)

#######################
# Development
#######################
.PHONY: serve
serve:
	@uvicorn investmentstk.server:app --reload --reload-dir=src/

.PHONY: type
type:
	@echo "Running mypy"
	@pipenv run mypy src/

.PHONY: check-lint
check-lint:
	@echo "Running black"
	@pipenv run black --check src/ tests/
	@echo "Running flake"
	@pipenv run flake8 src/ tests/

.PHONY: lint
lint:
	@echo "Running black"
	@pipenv run black src/ tests/
	@echo "Running flake"
	@pipenv run flake8 src/ tests/

.PHONY: test
test:
	@echo "Running pytest"
	@pipenv run pytest -m "not manual"

.PHONY: test-all
test-all:
	@echo "Running pytest"
	@pipenv run pytest

.PHONY: test-coverage
test-coverage:
	@echo "Running pytest (with coverage)"
	@pipenv run pytest -m "not manual" --cov --cov-report=xml


#######################
# Deployment
#######################
.PHONY: image
image:
	@echo "Building $(IMAGE):$(VERSION)"
	@docker build -f Dockerfile -t $(IMAGE):$(VERSION) -t $(IMAGE):latest .

.PHONY: push
push: image
	@echo "Pushing $(IMAGE)"
	@docker push $(IMAGE)

.PHONY: deploy-cloud-run
deploy-cloud-run:
	@gcloud run deploy $(APP_NAME) \
		--project=$(GCP_PROJECT_NAME) \
		--image=$(IMAGE):latest \
		--region=europe-west3 \
		--min-instances=0 \
		--max-instances=2 \
		--service-account=$(GCP_SERVICE_ACCOUNT_EMAIL) \
		--allow-unauthenticated \
		--concurrency 160 \
		--verbosity debug

.PHONY: deploy
deploy: push deploy-cloud-run
