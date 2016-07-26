version ?= 'auto'
project ?= 'google.com:g6-kintaro-demo'

develop:
	pip install -t lib grow

deploy:
	gcloud preview app deploy \
	  -q \
	  --project=$(project) \
	  --version=$(version) \
	  app.yaml

run-gae:
	dev_appserver.py --allow_skipped_files=true .

.PHONY: develop deploy run-gae
