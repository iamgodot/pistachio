help: ## Prints help for targets with comments
	@cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z_-]+:.*?## .*$$' | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

clean: # Remove python cache&build results.
	find . -iname "*__pycache__" | xargs rm -rf
	find . -iname "*.pyc" | xargs rm -rf
	rm -rf .pytest_cache
	rm -rf build
	rm -rf dist

lint: # Check linting via ruff.
	pdm run ruff check .

format: # Format code via black&ruff.
	pdm run black .
	pdm run ruff check --fix .

test: clean lint ## Run pytest
	PISTACHIO_SETTINGS=TestSettings pdm run pytest tests -sv

run: ## Run local server
	pdm run flask --app pistachio run --debug -h 0.0.0.0 -p 9527

build-image: ## Build docker image for amd64
	docker buildx build --platform linux/amd64 -f Dockerfile -t iamgodot/pistachio .

push-image: ## Push docker image for amd64
	docker push iamgodot/pistachio

build-gh-image: ## Build github image for backend app
	docker build -t ghcr.io/iamgodot/pistachio:latest .

push-gh-image: ## Push image to github
	docker push ghcr.io/iamgodot/pistachio:latest
