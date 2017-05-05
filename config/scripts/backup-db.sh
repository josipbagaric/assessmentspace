#!/bin/sh
cd ~/assessment-space/
docker-compose exec -T db pg_dumpall -c -U postgres > ~/backup/db/dump_`date +%d-%m-%Y"_"%H_%M_%S`.sql