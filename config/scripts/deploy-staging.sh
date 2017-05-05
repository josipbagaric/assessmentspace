#!/bin/sh
cd ~/tracegenomics
. venv/bin/activate
git pull origin master
make rebuild-web
rm -rf ~/.ssh/github_rsa*