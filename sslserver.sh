#!/usr/bin/env bash

python manage.py runsslserver 0.0.0.0:8100 --certificate server.crt --key server.key
