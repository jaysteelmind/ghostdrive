#!/bin/bash
# ==============================================================================
# GhostDrive Linux Installer
# Version: 1.0.0
# Created: 2026-01-04
# Purpose: Create isolated Python environment and install dependencies
# ==============================================================================

set -e
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/venv_ui"
REQUIREMENTS_FILE="${SCRIPT_DIR}/requirements_linux.txt"
MODEL_INSTALLER="${SCRIPT_DIR}/Everything_else/install_models.py"
MIN_PYTHON_VERSION="3.10"

log_info() {
    echo "[INFO] $1"
}

log_error() {
    echo "[ERROR] $1" >&2
}

log_success() {
    echo "[SUCCESS] $1"
}

check_python_version() {
    log_info "Checking Python version..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 not found. Please install Python ${MIN_PYTHON_VERSION} or higher."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    PYTHON_MAJOR=$(echo "${PYTHON_VERSION}" | cut -d. -f1)
    PYTHON_MINOR=$(echo "${PYTHON_VERSION}" | cut -d. -f2)
    MIN_MAJOR=$(echo "${MIN_PYTHON_VERSION}" | cut -d. -f1)
    MIN_MINOR=$(echo "${MIN_PYTHON_VERSION}" | cut -d. -f2)
    
    if [ "${PYTHON_MAJOR}" -lt "${MIN_MAJOR}" ] || { [ "${PYTHON_MAJOR}" -eq "${MIN_MAJOR}" ] && [ "${PYTHON_MINOR}" -lt "${MIN_MINOR}" ]; }; then
        log_error "Python ${PYTHON_VERSION} found. Minimum required: ${MIN_PYTHON_VERSION}"
        exit 1
    fi
    
    log_info "Python ${PYTHON_VERSION} detected."
}

check_requirements_file() {
    log_info "Checking requirements file..."
    
    if [ ! -f "${REQUIREMENTS_FILE}" ]; then
        log_error "Requirements file not found: ${REQUIREMENTS_FILE}"
        exit 1
    fi
    
    log_info "Requirements file found."
}

remove_existing_venv() {
    if [ -d "${VENV_DIR}" ]; then
        log_info "Removing existing virtual environment..."
        rm -rf "${VENV_DIR}"
    fi
}

create_virtual_environment() {
    log_info "Creating virtual environment at ${VENV_DIR}..."
    
    python3 -m venv "${VENV_DIR}"
    
    if [ ! -f "${VENV_DIR}/bin/python" ]; then
        log_error "Virtual environment creation failed."
        exit 1
    fi
    
    log_info "Virtual environment created."
}

upgrade_pip() {
    log_info "Upgrading pip..."
    
    "${VENV_DIR}/bin/python" -m pip install --upgrade pip --quiet
    
    log_info "Pip upgraded."
}

install_dependencies() {
    log_info "Installing dependencies from ${REQUIREMENTS_FILE}..."
    
    "${VENV_DIR}/bin/python" -m pip install -r "${REQUIREMENTS_FILE}" --quiet
    
    if [ $? -ne 0 ]; then
        log_error "Dependency installation failed."
        exit 1
    fi
    
    log_success "Dependencies installed."
}

verify_installation() {
    log_info "Verifying critical packages..."
    
    "${VENV_DIR}/bin/python" -c "import PySide6; print(f'  PySide6: {PySide6.__version__}')"
    "${VENV_DIR}/bin/python" -c "import llama_cpp; print('  llama-cpp-python: OK')"
    "${VENV_DIR}/bin/python" -c "from cryptography.fernet import Fernet; print('  cryptography/Fernet: OK')"
    "${VENV_DIR}/bin/python" -c "import yaml; print('  PyYAML: OK')"
    "${VENV_DIR}/bin/python" -c "import psutil; print('  psutil: OK')"
    
    log_success "All critical packages verified."
}

run_model_installer() {
    if [ -f "${MODEL_INSTALLER}" ]; then
        log_info "Checking AI model..."
        
        MODEL_PATH="${SCRIPT_DIR}/Everything_else/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
        
        if [ -f "${MODEL_PATH}" ]; then
            MODEL_SIZE=$(stat -c%s "${MODEL_PATH}" 2>/dev/null || stat -f%z "${MODEL_PATH}" 2>/dev/null)
            if [ "${MODEL_SIZE}" -gt 4000000000 ]; then
                log_info "AI model already present ($(numfmt --to=iec ${MODEL_SIZE}))."
                return 0
            fi
        fi
        
        log_info "Running model installer..."
        "${VENV_DIR}/bin/python" "${MODEL_INSTALLER}"
    else
        log_info "Model installer not found. Skipping model download."
    fi
}

main() {
    echo "=============================================="
    echo "       GhostDrive Linux Installer"
    echo "=============================================="
    echo ""
    
    cd "${SCRIPT_DIR}"
    
    check_python_version
    check_requirements_file
    check_system_dependencies
    remove_existing_venv
    create_virtual_environment
    upgrade_pip
    install_dependencies
    verify_installation
    run_model_installer
    
    echo ""
    echo "=============================================="
    log_success "GhostDrive installation complete."
    echo "=============================================="
    echo ""
    echo "To launch GhostDrive, run:"
    echo "  ./launch_ghostdrive.sh"
    echo ""
}

main "$@"
