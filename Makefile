help:
	@echo "--local--"
	@echo "build-local - Build container locally"
	@echo "rebuild-local - Rebuild local containers"
	@echo "delete-local - Delete local containers"
	@echo "--staging--"
	@echo "deploy-staging - sync local code to staging server"
	@echo "build-staging - sync local code to staging server, rebuild Docker image and reload on staging server"

STAGING_HOST=assessmentspace.com
SSH_KEY=~/keypair1.pem

build-local:
	docker-compose build
	docker-compose up -d
	docker ps -a

delete-local:
	docker-compose stop
	docker-compose rm -f

rebuild-local: delete-local build-local

rebuild-web:
	docker-compose stop web
	docker-compose rm -f web
	docker-compose build web
	docker-compose up web

backup-db-staging:
	scp -i $(SSH_KEY) ~/.ssh/id_rsa.pub ubuntu@$(STAGING_HOST):~/.ssh/github_rsa.pub
	scp -i $(SSH_KEY) ~/.ssh/id_rsa ubuntu@$(STAGING_HOST):~/.ssh/github_rsa
	ssh -i $(SSH_KEY) ubuntu@$(STAGING_HOST) 'bash -s' < config/scripts/backup-db.sh

build-staging:
	scp -i $(SSH_KEY) ~/.ssh/id_rsa.pub ubuntu@$(STAGING_HOST):~/.ssh/github_rsa.pub
	scp -i $(SSH_KEY) ~/.ssh/id_rsa ubuntu@$(STAGING_HOST):~/.ssh/github_rsa
	ssh -i $(SSH_KEY) ubuntu@$(STAGING_HOST) 'bash -s' < config/scripts/build-staging.sh

deploy-staging:
	scp -i $(SSH_KEY) ~/.ssh/id_rsa.pub ubuntu@$(STAGING_HOST):~/.ssh/github_rsa.pub
	scp -i $(SSH_KEY) ~/.ssh/id_rsa ubuntu@$(STAGING_HOST):~/.ssh/github_rsa
	ssh -i $(SSH_KEY) ubuntu@$(STAGING_HOST) 'bash -s' < config/scripts/backup-db.sh
	ssh -i $(SSH_KEY) ubuntu@$(STAGING_HOST) 'bash -s' < config/scripts/deploy-staging.sh
	


