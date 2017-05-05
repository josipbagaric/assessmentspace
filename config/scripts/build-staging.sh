#!/bin/sh
rm -rf ~/assessment-space
git clone git@github.com:Bagaric/assessment-space.git ~/assessment-space
cd ~/assessment-space
python -m virtualenv --python=/usr/bin/python2 venv
. venv/bin/activate
pip install -r config/requirements.txt
pip uninstall -y docker docker-py docker-compose
pip install docker-compose
cd src
./manage.py collectstatic --noinput
cd ~/assessment-space
make rebuild-local
rm -rf ~/.ssh/github_rsa*