#!/bin/bash
# ==============================================================================
# GhostDrive Linux Launcher
# Version: 1.0.0
# Created: 2026-01-04
# Purpose: Launch GhostDrive application with proper environment
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/venv_ui"
VENV_PYTHON="${VENV_DIR}/bin/python"
MAIN_SCRIPT="${SCRIPT_DIR}/main.py"

log_error() {
    echo "[ERROR] $1" >&2
}

check_venv() {
    if [ ! -f "${VENV_PYTHON}" ]; then
        log_error "Virtual environment not found at ${VENV_DIR}"
        log_error "Please run ./install_ghostdrive.sh first."
        exit 1
    fi
}

check_main_script() {
    if [ ! -f "${MAIN_SCRIPT}" ]; then
        log_error "main.py not found at ${MAIN_SCRIPT}"
        exit 1
    fi
}

launch_application() {
    echo "=============================================="
    echo "         Launching GhostDrive"
    echo "=============================================="
    echo ""
    echo "[INFO] Using Python: ${VENV_PYTHON}"
    echo ""
    
    cd "${SCRIPT_DIR}"
    
    source "${VENV_DIR}/bin/activate"
    
    "${VENV_PYTHON}" "${MAIN_SCRIPT}"
    
    EXIT_CODE=$?
    
    deactivate 2>/dev/null || true
    
    if [ ${EXIT_CODE} -ne 0 ]; then
        echo ""
        log_error "GhostDrive exited with code: ${EXIT_CODE}"
    fi
    
    exit ${EXIT_CODE}
}

main() {
    check_venv
    check_main_script
    launch_application
}

main "$@"
