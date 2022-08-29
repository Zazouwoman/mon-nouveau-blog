#! /bin/bash
echo "pg dump deltapi vers $1"

pg_dump DELTAPI | gzip > $1
