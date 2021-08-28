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
	@pipenv run flake8 src/#######################
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
		--max-instances=1 \
		--service-account=$(SERVICE_ACCOUNT) \
		--allow-unauthenticated \
		--verbosity debug
