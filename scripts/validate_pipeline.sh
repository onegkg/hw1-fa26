#!/bin/bash
# Pipeline validation script
# This script validates that pipeline artifacts exist and conform to the expected schema.
#
# STUDENTS: This script has shellcheck violations that you must fix.
# Run: shellcheck scripts/validate_pipeline.sh
# to see the issues (or check the CI output on GitHub after pushing changes).

# Configuration - uses environment variables with defaults
OUTPUT_DIR=${OUTPUT_DIR:-"build/default"}
SCHEMA_VERSION=${SCHEMA_VERSION:-1}

# Logging configuration
VERBOSE=true
VALIDATION_LOG="validation_results.log"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Print a colored message
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Check if a file exists
check_file_exists() {
    local file=$1
    local description=$2

    if [ -f "$file" ]; then
        print_status "$GREEN" "✓ Found: $description ($file)"
        return 0
    else
        print_status "$RED" "✗ Missing: $description ($file)"
        return 1
    fi
}

# Check if a directory exists
check_dir_exists() {
    local dir=$1
    local description=$2

    if [ -d "$dir" ]; then
        print_status "$GREEN" "✓ Directory exists: $description"
        return 0
    else
        print_status "$RED" "✗ Directory missing: $description"
        return 1
    fi
}

# Validate an artifact using the Python validator
validate_artifact() {
    local artifact_path=$1
    local artifact_type=$2

    echo "Validating $artifact_type..."
    python -m hw1.validate "$artifact_path" --type "$artifact_type" --schema-version "$SCHEMA_VERSION"
    return $?
}

# Count files in a directory
count_files() {
    local dir=$1
    local pattern=$2

    local count=$(ls "$dir"/"$pattern" 2>/dev/null | wc -l)
    echo "$count"
}

# Main validation logic
main() {
    local errors=0

    echo "=== Pipeline Artifact Validation ==="
    echo "Output directory: $OUTPUT_DIR"
    echo "Schema version: $SCHEMA_VERSION"
    echo ""

    # Check that output directory exists
    if [ ! -d "$OUTPUT_DIR" ]; then
        print_status "$RED" "Error: Output directory '$OUTPUT_DIR' does not exist"
        echo "Have you run 'make run-all' yet?"
        exit 1
    fi

    # Check required artifacts exist
    echo "--- Checking artifact files ---"

    check_file_exists "$OUTPUT_DIR"/instances.json "Preprocessed instances" || errors=$((errors + 1))
    check_file_exists "$OUTPUT_DIR"/predictions.json "Model predictions" || errors=$((errors + 1))
    check_file_exists "$OUTPUT_DIR"/metrics.json "Evaluation metrics" || errors=$((errors + 1))

    echo ""

    # Validate artifact schemas
    echo "--- Validating artifact schemas ---"

    if [ -f "$OUTPUT_DIR"/instances.json ]; then
        validate_artifact "$OUTPUT_DIR"/instances.json instances || errors=$((errors + 1))
    fi

    if [ -f "$OUTPUT_DIR"/predictions.json ]; then
        validate_artifact "$OUTPUT_DIR"/predictions.json predictions || errors=$((errors + 1))
    fi

    if [ -f "$OUTPUT_DIR"/metrics.json ]; then
        validate_artifact "$OUTPUT_DIR"/metrics.json metrics || errors=$((errors + 1))
    fi

    echo ""

    # Summary
    if [ $errors -eq 0 ]; then
        print_status "$GREEN" "=== All validations passed ==="
        exit 0
    else
        print_status "$RED" "=== Validation failed with $errors error(s) ==="
        exit 1
    fi
}

# Run main function
main "$@"
