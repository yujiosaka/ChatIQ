#!/bin/sh

version=$1

# Update version in pyproject.toml
sed -i.bak "s/version = \".*\"/version = \"$version\"/" pyproject.toml && rm pyproject.toml.bak
