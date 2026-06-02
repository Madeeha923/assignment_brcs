#!/usr/bin/env bash
set -o errexit

# Update pip to latest version
pip install --upgrade pip

# Install with pre-built wheels only (no source builds)
pip install --only-binary :all: -r requirements.txt || \
pip install --prefer-binary -r requirements.txt
