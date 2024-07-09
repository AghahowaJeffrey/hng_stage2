#!/bin/bash

echo "Create a virtual environment"
python3 -m venv venv
source venv/Script/activate

echo "Building project packages..."
python3 -m pip install -r requirements.txt

echo "Migrating Database..."
python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput