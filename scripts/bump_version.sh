#!/usr/bin/env bash
# Usage: ./scripts/bump_version.sh 1.2.0
set -euo pipefail
NEW="$1"
sed -i "s/^version = \".*\"/version = \"${NEW}\"/" pyproject.toml
sed -i "s/^AppVersion=.*/AppVersion=${NEW}/" installer.iss
echo "Bumped to ${NEW} in pyproject.toml and installer.iss"
echo ""
echo "Next steps:"
echo "  git add pyproject.toml installer.iss"
echo "  git commit -m 'chore: bump version to ${NEW}'"
echo "  git push origin main"
echo "  git tag -a v${NEW} -m 'Release v${NEW}'"
echo "  git push origin v${NEW}"
