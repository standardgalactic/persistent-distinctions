#!/bin/bash
# Project management script for persistent-distinctions
# Supports: clean, install, test, run, version management, release

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION_FILE="${PROJECT_ROOT}/pyproject.toml"
VENV_PATH="${PROJECT_ROOT}/.venv"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

get_current_version() {
    grep "^version = " "${VERSION_FILE}" | sed 's/version = "//' | sed 's/"//' 
}

set_version() {
    local new_version=$1
    local temp_file="${VERSION_FILE}.tmp"
    sed "s/^version = .*/version = \"${new_version}\"/" "${VERSION_FILE}" > "${temp_file}"
    mv "${temp_file}" "${VERSION_FILE}"
    print_success "Version updated to ${new_version}"
}

increment_major() {
    local version=$1
    local major=$(echo "$version" | cut -d. -f1)
    echo "$((major + 1)).0.0"
}

increment_minor() {
    local version=$1
    local major=$(echo "$version" | cut -d. -f1)
    local minor=$(echo "$version" | cut -d. -f2)
    echo "${major}.$((minor + 1)).0"
}

increment_patch() {
    local version=$1
    local major=$(echo "$version" | cut -d. -f1)
    local minor=$(echo "$version" | cut -d. -f2)
    local patch=$(echo "$version" | cut -d. -f3)
    echo "${major}.${minor}.$((patch + 1))"
}

ensure_venv() {
    if [ ! -d "${VENV_PATH}" ]; then
        print_header "Creating Python virtual environment"
        python3 -m venv "${VENV_PATH}"
        print_success "Virtual environment created"
    fi
    source "${VENV_PATH}/bin/activate"
}

cmd_help() {
    cat << EOF
${BLUE}persistent-distinctions - Project Management${NC}

${GREEN}Usage:${NC} ./scripts/manage.sh <command> [options]

${GREEN}Commands:${NC}
  help              Show this help message
  clean             Remove build artifacts, cache, and virtual environment
  install           Create venv and install dependencies
  dev-install       Install with dev dependencies
  build             Build the project
  test              Run tests with coverage
  run               Run experiments
  lint              Run code quality checks (black, flake8, isort)
  format            Auto-format code (black, isort)
  type-check        Run mypy type checking
  version           Show current version
  version-bump      Bump patch version (e.g., 0.1.0 -> 0.1.1)
  version-minor     Bump minor version (e.g., 0.1.0 -> 0.2.0)
  version-major     Bump major version (e.g., 0.1.0 -> 1.0.0)
  release           Create a release tag with current version
  docs              Generate documentation

${GREEN}Examples:${NC}
  ./scripts/manage.sh clean
  ./scripts/manage.sh install
  ./scripts/manage.sh test
  ./scripts/manage.sh version-bump
  ./scripts/manage.sh release

EOF
}

cmd_clean() {
    print_header "Cleaning project"
    
    # Remove Python cache
    find "${PROJECT_ROOT}" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find "${PROJECT_ROOT}" -type f -name "*.pyc" -delete
    find "${PROJECT_ROOT}" -type f -name "*.pyo" -delete
    find "${PROJECT_ROOT}" -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    
    # Remove build artifacts
    rm -rf "${PROJECT_ROOT}/build" 2>/dev/null || true
    rm -rf "${PROJECT_ROOT}/dist" 2>/dev/null || true
    
    # Remove pytest cache
    rm -rf "${PROJECT_ROOT}/.pytest_cache" 2>/dev/null || true
    rm -rf "${PROJECT_ROOT}/.coverage" 2>/dev/null || true
    rm -rf "${PROJECT_ROOT}/htmlcov" 2>/dev/null || true
    
    # Remove mypy cache
    rm -rf "${PROJECT_ROOT}/.mypy_cache" 2>/dev/null || true
    
    print_success "Project cleaned"
}

cmd_install() {
    print_header "Installing project"
    ensure_venv
    
    pip install --upgrade pip setuptools wheel
    pip install -e .
    pip install -r requirements.txt
    
    print_success "Project installed"
}

cmd_dev_install() {
    print_header "Installing project with dev dependencies"
    ensure_venv
    
    pip install --upgrade pip setuptools wheel
    pip install -e ".[dev]"
    pip install -r requirements.txt
    
    print_success "Project installed with dev dependencies"
}

cmd_build() {
    print_header "Building project"
    ensure_venv
    
    python -m pip install build
    python -m build
    
    print_success "Build complete"
}

cmd_test() {
    print_header "Running tests"
    ensure_venv
    
    if ! command -v pytest &> /dev/null; then
        print_warning "pytest not installed, installing..."
        pip install pytest pytest-cov
    fi
    
    pytest -v --cov=experiments --cov-report=term-missing --cov-report=html
    print_success "Tests complete (coverage report in htmlcov/)"
}

cmd_run() {
    print_header "Running experiments"
    ensure_venv
    
    if [ -f "${PROJECT_ROOT}/experiments/run.py" ]; then
        python "${PROJECT_ROOT}/experiments/run.py"
    else
        print_error "experiments/run.py not found"
        return 1
    fi
}

cmd_lint() {
    print_header "Running code quality checks"
    ensure_venv
    
    if ! command -v black &> /dev/null; then
        print_warning "dev tools not installed, installing..."
        pip install black flake8 isort mypy
    fi
    
    print_header "Running black..."
    black --check "${PROJECT_ROOT}/experiments" || true
    
    print_header "Running flake8..."
    flake8 "${PROJECT_ROOT}/experiments" || true
    
    print_header "Running isort..."
    isort --check-only "${PROJECT_ROOT}/experiments" || true
}

cmd_format() {
    print_header "Formatting code"
    ensure_venv
    
    if ! command -v black &> /dev/null; then
        print_warning "dev tools not installed, installing..."
        pip install black isort
    fi
    
    black "${PROJECT_ROOT}/experiments"
    isort "${PROJECT_ROOT}/experiments"
    
    print_success "Code formatted"
}

cmd_type_check() {
    print_header "Running type checking"
    ensure_venv
    
    if ! command -v mypy &> /dev/null; then
        pip install mypy
    fi
    
    mypy "${PROJECT_ROOT}/experiments" || true
}

cmd_version() {
    local version=$(get_current_version)
    echo "Current version: ${version}"
}

cmd_version_bump() {
    local current=$(get_current_version)
    local new=$(increment_patch "${current}")
    
    print_header "Bumping patch version"
    echo "  ${current} → ${new}"
    
    set_version "${new}"
}

cmd_version_minor() {
    local current=$(get_current_version)
    local new=$(increment_minor "${current}")
    
    print_header "Bumping minor version"
    echo "  ${current} → ${new}"
    
    set_version "${new}"
}

cmd_version_major() {
    local current=$(get_current_version)
    local new=$(increment_major "${current}")
    
    print_header "Bumping major version"
    echo "  ${current} → ${new}"
    
    set_version "${new}"
}

cmd_release() {
    print_header "Creating release"
    
    local version=$(get_current_version)
    
    # Check if git is available
    if ! command -v git &> /dev/null; then
        print_error "git not found, cannot create release tag"
        return 1
    fi
    
    # Check for uncommitted changes
    if ! git -C "${PROJECT_ROOT}" diff-index --quiet HEAD --; then
        print_error "Uncommitted changes detected. Please commit all changes before release."
        return 1
    fi
    
    local tag="v${version}"
    
    # Check if tag already exists
    if git -C "${PROJECT_ROOT}" rev-parse "${tag}" >/dev/null 2>&1; then
        print_error "Tag ${tag} already exists"
        return 1
    fi
    
    git -C "${PROJECT_ROOT}" tag -a "${tag}" -m "Release ${version}"
    git -C "${PROJECT_ROOT}" push origin "${tag}"
    
    print_success "Release ${version} created and pushed"
}

cmd_docs() {
    print_header "Generating documentation"
    ensure_venv
    
    if ! command -v sphinx-build &> /dev/null; then
        print_warning "sphinx not installed, installing..."
        pip install sphinx
    fi
    
    if [ ! -d "${PROJECT_ROOT}/docs" ]; then
        mkdir -p "${PROJECT_ROOT}/docs"
        print_warning "docs/ directory created. Please configure Sphinx manually."
        return 1
    fi
    
    sphinx-build -b html "${PROJECT_ROOT}/docs" "${PROJECT_ROOT}/docs/_build/html"
    print_success "Documentation built in docs/_build/html/"
}

# Main command routing
main() {
    local cmd="${1:-help}"
    
    case "${cmd}" in
        help)
            cmd_help
            ;;
        clean)
            cmd_clean
            ;;
        install)
            cmd_install
            ;;
        dev-install)
            cmd_dev_install
            ;;
        build)
            cmd_build
            ;;
        test)
            cmd_test
            ;;
        run)
            cmd_run
            ;;
        lint)
            cmd_lint
            ;;
        format)
            cmd_format
            ;;
        type-check)
            cmd_type_check
            ;;
        version)
            cmd_version
            ;;
        version-bump|bump)
            cmd_version_bump
            ;;
        version-minor|minor)
            cmd_version_minor
            ;;
        version-major|major)
            cmd_version_major
            ;;
        release)
            cmd_release
            ;;
        docs)
            cmd_docs
            ;;
        *)
            print_error "Unknown command: ${cmd}"
            cmd_help
            exit 1
            ;;
    esac
}

main "$@"
