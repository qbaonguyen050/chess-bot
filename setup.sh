#!/bin/bash

echo "Installing dependencies for fast setup..."
pip install --no-cache-dir -r requirements.txt

echo "Starting the chess engine application on a public port..."
python3 app.py