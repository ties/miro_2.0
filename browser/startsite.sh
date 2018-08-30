#!/bin/bash
FLASK_ENV=development FLASK_CONFIG=development FLASK_APP=run.py gunicorn -w 10 run:app -b 127.0.0.1:8080
