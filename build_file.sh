#!/bin/bash
echo "Installing pipenv"
python3 -m pip install pipenv

echo "Building project packages..."
python3 -m pipenv install --system --deploy --ignore-pipfile

echo "Migrating Database..."
python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput

echo "Creating dist folder..."
mkdir -p dist

echo "Copying necessary files to dist..."
cp -r hng_stage2/wsgi.py dist/

echo "Setup complete"