# HW1 Makefile - NLP Pipeline Automation

.PHONY: all clean test lint typecheck quality preprocess rule-based evaluate plot validate run-all ci

# Configuration
DATA_DIR ?= tests/fixtures
OUTPUT_DIR := build

# Let Python find the hw1 package in src/ (for `python -m hw1.<module>`)
export PYTHONPATH := $(CURDIR)/src

RUN_TAG ?= default
SCHEMA_VERSION ?= 1

# Artifact paths - currently hardcoded to "default" subdirectory
ARTIFACTS_DIR := $(OUTPUT_DIR)/$(RUN_TAG)
INSTANCES := $(ARTIFACTS_DIR)/instances.json
PREDICTIONS := $(ARTIFACTS_DIR)/predictions.json
METRICS := $(ARTIFACTS_DIR)/metrics.json
PLOT := $(ARTIFACTS_DIR)/evaluation_plot.png

# Default target
all: run-all

ci: quality all

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

shellcheck:
	shellcheck --severity=warning scripts/*.sh

# Combined quality checks
quality: lint typecheck shellcheck test

# Preprocess data
preprocess: $(INSTANCES)

$(INSTANCES): | $(ARTIFACTS_DIR)
	python -m hw1.dataset $(DATA_DIR) --output $(OUTPUT_DIR) --run-tag $(RUN_TAG) --schema-version $(SCHEMA_VERSION)

# Run rule-based classifier
rule-based: $(PREDICTIONS)

$(PREDICTIONS): $(INSTANCES)
	python -m hw1.validate $(INSTANCES) --type instances --schema-version $(SCHEMA_VERSION)
	python -m hw1.models --file $(INSTANCES) --output $(OUTPUT_DIR) --run-tag $(RUN_TAG) --schema-version $(SCHEMA_VERSION)

# Evaluate predictions
evaluate: $(METRICS)

$(METRICS): $(PREDICTIONS)
	python -m hw1.validate $(PREDICTIONS) --type predictions --instances $(INSTANCES) --schema-version $(SCHEMA_VERSION)
	python -m hw1.evaluation $(PREDICTIONS) --output $(OUTPUT_DIR) --run-tag $(RUN_TAG) --schema-version $(SCHEMA_VERSION)

# Generate plot
plot: $(PLOT)

$(PLOT): $(METRICS)
	python -m hw1.validate $(METRICS) --type metrics
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

