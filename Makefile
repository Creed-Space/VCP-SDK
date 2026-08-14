PYTHON ?= python3
CARGO_AUDIT ?= cargo audit

.PHONY: validate repository review-ledger schemas conformance conformance-coverage schema-sync python coverage rust webmcp artifacts property performance-smoke performance-full examples packages audits all

validate: repository schemas conformance

repository:
	$(PYTHON) -m ruff check scripts
	$(PYTHON) -m ruff format --check scripts
	$(PYTHON) scripts/validate_repo.py
	$(PYTHON) scripts/validate_review_ledger.py

review-ledger:
	$(PYTHON) scripts/validate_review_ledger.py

schemas:
	npm run validate:schemas --silent

conformance:
	$(PYTHON) scripts/generate_conformance_coverage.py --check
	$(PYTHON) conformance/runners/run_all.py

conformance-coverage:
	$(PYTHON) scripts/generate_conformance_coverage.py

schema-sync:
	@test -n "$(SPEC)" || (echo "Set SPEC=/path/to/VCP-Spec" >&2; exit 2)
	$(PYTHON) scripts/check_schema_sync.py --spec "$(SPEC)" --sdk .

python:
	cd python && $(PYTHON) -m ruff check src tests
	cd python && $(PYTHON) -m mypy src/vcp
	cd python && $(PYTHON) -m pytest -q
	cd python && $(PYTHON) -m build
	cd python && $(PYTHON) ../scripts/normalize_python_sdist.py dist/*.tar.gz
	cd python && $(PYTHON) -m twine check dist/*

coverage:
	cd python && $(PYTHON) -m pytest -q --cov=vcp --cov-branch --cov-report=json:coverage.json
	$(PYTHON) scripts/check_critical_coverage.py python/coverage.json --output python/critical-coverage.json

rust:
	cd rust && cargo fmt --all -- --check
	cd rust && cargo clippy --workspace --all-targets --all-features -- -D warnings
	cd rust && cargo test --workspace --all-features
	cd rust && RUSTDOCFLAGS='-D warnings' cargo doc --workspace --all-features --no-deps

webmcp:
	cd webmcp && npm run check
	cd webmcp && npm test
	cd webmcp && npm run prepack
	cd webmcp && npm pack --dry-run

artifacts:
	$(PYTHON) scripts/verify_artifacts.py

property:
	cd python && $(PYTHON) -m pytest -q tests/property
	cd rust && cargo test -p vcp-core --test property
	cd webmcp && npx vitest run tests/property.test.ts

performance-smoke:
	$(PYTHON) scripts/run_performance.py --profile smoke --output performance-results/local-smoke.json

performance-full:
	$(PYTHON) scripts/run_performance.py --profile full --output performance-results/local-full.json
	cd rust && cargo bench -p vcp-core --bench core_performance

examples:
	for example in examples/python/*.py; do PYTHONPATH=python/src $(PYTHON) "$$example"; done
	cd rust && cargo run --quiet -p vcp-core --example parse_token
	cd rust && cargo run --quiet -p vcp-core --example sign_and_verify
	cd rust && cargo run --quiet -p vcp-core --example verify_bundle

packages:
	cd rust && cargo package -p vcp-core --allow-dirty --locked
	cd rust && cargo package -p vcp-cli --allow-dirty --locked --config 'patch.crates-io.vcp-core.path="vcp-core"'
	cd rust && cargo package -p vcp-wasm --allow-dirty --locked --config 'patch.crates-io.vcp-core.path="vcp-core"'

audits:
	npm audit --audit-level=moderate
	cd python && $(PYTHON) -m pip_audit --requirement requirements-dev.lock
	cd rust && $(CARGO_AUDIT) --file Cargo.lock
	cd webmcp && npm audit --audit-level=moderate

all: validate python rust webmcp examples packages audits
