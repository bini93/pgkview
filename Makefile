.PHONY: dev test lint clean install

# Set up development environment (venv + all dependencies)
dev:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -e ".[dev]"
	@echo ""
	@echo "Done. Activate with: source .venv/bin/activate"

# Run the test suite
test:
	.venv/bin/pytest

# Install the tool for personal use via pipx (editable)
install:
	pipx install --editable .

# Remove build artefacts and the venv
clean:
	rm -rf .venv __pycache__ dist src/pkgview.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +
