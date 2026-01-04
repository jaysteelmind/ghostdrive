#!/bin/bash
# ==============================================================================
# GhostDrive Linux - Test Runner
# Version: 1.0.0
# Created: 2026-01-04
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "${SCRIPT_DIR}")"
VENV_PYTHON="${PROJECT_ROOT}/venv_ui/bin/python"

if [ ! -f "${VENV_PYTHON}" ]; then
    echo "[ERROR] Virtual environment not found. Run install_ghostdrive.sh first."
    exit 1
fi

echo "=============================================="
echo "       GhostDrive Linux Test Suite"
echo "=============================================="
echo ""

cd "${PROJECT_ROOT}"

echo "[INFO] Running unit tests: imports..."
"${VENV_PYTHON}" -m pytest "${SCRIPT_DIR}/unit/test_imports.py" -v --tb=short 2>/dev/null || "${VENV_PYTHON}" "${SCRIPT_DIR}/unit/test_imports.py"

echo ""
echo "[INFO] Running unit tests: encryption..."
"${VENV_PYTHON}" -m pytest "${SCRIPT_DIR}/unit/test_encryption.py" -v --tb=short 2>/dev/null || "${VENV_PYTHON}" "${SCRIPT_DIR}/unit/test_encryption.py"

echo ""
echo "[INFO] Running unit tests: wifi..."
"${VENV_PYTHON}" -m pytest "${SCRIPT_DIR}/unit/test_wifi.py" -v --tb=short 2>/dev/null || "${VENV_PYTHON}" "${SCRIPT_DIR}/unit/test_wifi.py"

echo ""
echo "[INFO] Running integration tests: model..."
"${VENV_PYTHON}" -m pytest "${SCRIPT_DIR}/integration/test_model.py" -v --tb=short 2>/dev/null || "${VENV_PYTHON}" "${SCRIPT_DIR}/integration/test_model.py"

echo ""
echo "=============================================="
echo "[SUCCESS] All tests completed."
echo "=============================================="
