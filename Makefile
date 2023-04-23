help: ## Prints help for targets with comments
	@cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z_-]+:.*?## .*$$' | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

test: ## Run pytest
	pdm run -p backend pytest backend/tests -sv

build-docker-image: ## Build docker image for backend app
	docker build -t iamgodot/pistachio:v0.1.0 ./backend

build-gh-image: ## Build github image for backend app
	docker build -t ghcr.io/iamgodot/pistachio:latest ./backend

push-gh-image: ## Push image to github
	docker push ghcr.io/iamgodot/pistachio:latest
