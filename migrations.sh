#!/bin/bash

cd ../..
chmod +x migrations.sh
pdm run aerich init -t infrastructure.database.connection.sample_conf --location infrastructure/database/migrations -s . || aerich init -t infrastructure.database.connection.sample_conf --location infrastructure/database/migrations -s .
pdm run aerich init-db || aerich init-db
pdm run aerich migrate || aerich migrate
