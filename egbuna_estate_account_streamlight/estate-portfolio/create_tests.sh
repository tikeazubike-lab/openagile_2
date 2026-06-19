#!/bin/bash

mkdir -p ./epm-tests
mkdir -p ./epm-tests/backend/tests/{unit,integration,contract,db,performance}
mkdir -p ./epm-tests/frontend/tests/{unit/stores,unit/hooks,unit/lib,unit/components,e2e}
mkdir -p ./epm-tests/.github/workflows
mkdir -p ./epm-tests/.pre-commit-hooks
echo "Directories created"
