#!/bin/bash

echo "Installing dependencies..."
pip install Flask python-chess

echo "Starting the chess engine application..."
python3 app.py