#!/bin/sh
sudo rm -rf ~/assessmentspace
git clone git@github.com:Bagaric/assessmentspace.git ~/assessmentspace
cd ~/assessmentspace
virtualenv --python=/usr/bin/python3 venv
. venv/bin/activate
pip install -r config/requirements.txt
pip uninstall -y docker docker-py docker-compose
pip install docker-compose
cd src
./manage.py collectstatic --noinput
cd ~/assessmentspace
make rebuild-local
rm -rf ~/.ssh/github_rsa*