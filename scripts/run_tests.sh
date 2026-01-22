#!/bin/bash
set -e

echo "Running Flake8..."
flake8 src tests

echo "Running Pytest..."
pytest
