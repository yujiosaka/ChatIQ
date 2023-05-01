.PHONY: build create-configmap create-secrets deploy delete

LOG_LEVEL ?= info

create-configmap:  ## Create ConfigMap with LOG_LEVEL
	kubectl create configmap chatiq-config \
		--from-literal=LOG_LEVEL=$(LOG_LEVEL) \
		--dry-run=client -o yaml | kubectl apply -f -

create-secrets:  ## Create Secrets from .env file
	kubectl create secret generic chatiq-secrets \
		--from-env-file=.env \
		--dry-run=client -o yaml | kubectl apply -f -

deploy:  ## Deploy Kubernetes resources
	kubectl apply -f ./kubernetes/

delete:  ## Delete Kubernetes resources
	kubectl delete -f ./kubernetes/
