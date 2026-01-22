#!/bin/bash
set -e

echo "Running Flake8..."
flake8 src tests

echo "Running Yamllint..."
yamllint .

echo "Running Ansible Lint..."
ansible-lint ansible/

echo "Running Pytest..."
pytest
