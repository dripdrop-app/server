#!/bin/bash

psql -U $POSTGRES_USER postgres < /docker-entrypoint-initdb.d/postgres_copy.pgsql