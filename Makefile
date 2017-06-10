version ?= 'auto'
project ?= 'grow-base-kintaro'

develop:
	pip install -t lib grow

deploy:
	gcloud app deploy \
	  -q \
	  --project=$(project) \
	  --version=$(version) \
	  app.yaml

run-gae:
	dev_appserver.py --allow_skipped_files=true .

.PHONY: develop deploy run-gae
