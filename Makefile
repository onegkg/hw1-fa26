# HW1 Makefile - NLP Pipeline Automation
#
# STUDENTS: You must modify this Makefile to:
# 1. Uncomment and use RUN_TAG and SCHEMA_VERSION variables
# 2. Pass --run-tag $(RUN_TAG) and --schema-version $(SCHEMA_VERSION) to CLI commands
#
# Currently the pipeline uses hardcoded "default" paths. After your changes,
# running: make run-all RUN_TAG=experiment1 SCHEMA_VERSION=2
# should produce artifacts in build/experiment1/ with schema v2 format.

.PHONY: all clean test lint typecheck quality preprocess rule-based evaluate plot validate run-all

# Configuration
DATA_DIR ?= tests/fixtures
OUTPUT_DIR := build

# Let Python find the hw1 package in src/ (for `python -m hw1.<module>`)
export PYTHONPATH := $(CURDIR)/src

# TODO: Uncomment these variables and pass them to the CLI commands below
# RUN_TAG ?= default
# SCHEMA_VERSION ?= 1

# Artifact paths - currently hardcoded to "default" subdirectory
# TODO: Update these to use $(RUN_TAG) instead of "default"
ARTIFACTS_DIR := $(OUTPUT_DIR)/default
INSTANCES := $(ARTIFACTS_DIR)/instances.json
PREDICTIONS := $(ARTIFACTS_DIR)/predictions.json
METRICS := $(ARTIFACTS_DIR)/metrics.json
PLOT := $(ARTIFACTS_DIR)/evaluation_plot.png

# Default target
all: run-all

# Clean build artifacts
clean:
	rm -rf $(OUTPUT_DIR)
	rm -rf .mypy_cache .ruff_cache .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Run unit tests
test:
	pytest tests/ -v

# Run linter
lint:
	ruff check src/

# Run type checker
typecheck:
	mypy

# Combined quality checks
quality: lint typecheck

# Preprocess data
# TODO: Add --run-tag $(RUN_TAG) --schema-version $(SCHEMA_VERSION)
preprocess: $(INSTANCES)

$(INSTANCES): | $(ARTIFACTS_DIR)
	python -m hw1.dataset $(DATA_DIR) --output $(OUTPUT_DIR)

# Run rule-based classifier
# TODO: Add --run-tag $(RUN_TAG) --schema-version $(SCHEMA_VERSION)
rule-based: $(PREDICTIONS)

$(PREDICTIONS): $(INSTANCES)
	python -m hw1.validate $(INSTANCES) --type instances
	python -m hw1.models --file $(INSTANCES) --output $(OUTPUT_DIR)

# Evaluate predictions
# TODO: Add --run-tag $(RUN_TAG) --schema-version $(SCHEMA_VERSION)
evaluate: $(METRICS)

$(METRICS): $(PREDICTIONS)
	python -m hw1.validate $(PREDICTIONS) --type predictions --instances $(INSTANCES)
	python -m hw1.evaluation $(PREDICTIONS) --output $(OUTPUT_DIR)

# Generate plot
plot: $(PLOT)

$(PLOT): $(METRICS)
	python -m hw1.utils $(METRICS) --output $(PLOT)

# Validate pipeline artifacts
validate:
	OUTPUT_DIR=$(ARTIFACTS_DIR) bash scripts/validate_pipeline.sh

# Run entire pipeline
run-all: clean preprocess rule-based evaluate plot validate
	@echo "Pipeline completed successfully!"

# Create artifacts directory
$(ARTIFACTS_DIR):
	mkdir -p $(ARTIFACTS_DIR)
