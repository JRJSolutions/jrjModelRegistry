#!/bin/bash

set -e

source venv/bin/activate

rm -rf build
rm -rf dist

yarn run test

./increaseVersion.ts

new_version=$(node -p "require('./package.json').version")


python -m build


twine upload dist/*

git add .

git commit -m "chore: bump version to $new_version"

git tag -a "v$new_version" -m "Version $new_version"

git push origin main
git push origin "v$new_version"

echo "Version updated to $new_version, committed, and pushed with tag v$new_version"
