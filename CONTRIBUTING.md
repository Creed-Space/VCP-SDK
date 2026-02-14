# Contributing to VCP-SDK

Thank you for your interest in contributing to the Value-Context Protocol. This guide covers everything you need to get started.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Specification Changes](#specification-changes)

---

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](./CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [conduct@creedspace.com](mailto:conduct@creedspace.com).

---

## Getting Started

1. **Fork the repository** and clone your fork locally
2. **Create a branch** from `main` for your changes
3. **Set up the development environment** for the SDK(s) you're working on
4. **Make your changes** with appropriate tests
5. **Submit a pull request** against `main`

---

## Development Setup

### Python SDK

```bash
cd python
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e ".[dev]"
pytest tests/
```

Requires Python 3.10+.

### Rust SDK

```bash
cd rust
cargo build
cargo test
cargo clippy -- -D warnings
```

Requires Rust 1.70+ (2021 edition).

### TypeScript / WebMCP SDK

```bash
cd webmcp
npm install
npm run check   # Type checking
npm run build   # Compile to dist/
```

Requires Node.js 18+.

---

## Making Changes

### Branch Naming

| Prefix | Use Case |
|:---|:---|
| `feat/` | New features |
| `fix/` | Bug fixes |
| `docs/` | Documentation changes |
| `spec/` | Specification amendments |
| `refactor/` | Code refactoring |
| `test/` | Test additions or fixes |

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(python): add CSM-1 R-line parsing for personal state
fix(rust): correct identity token namespace validation
docs: update newcomer guide with v1.1 examples
spec: propose UVC registry extension for custom namespaces
```

### Testing

- **All changes must include tests.** Untested code will not be merged.
- Run the full test suite for the SDK(s) you've modified before submitting.
- Cross-SDK changes should be validated against the JSON schemas in `schemas/`.

---

## Pull Request Process

1. **Ensure all tests pass** in the relevant SDK(s)
2. **Update documentation** if your change affects public APIs or behavior
3. **Reference any related issues** in your PR description
4. **Describe your changes clearly** — what, why, and how
5. **Keep PRs focused** — one logical change per pull request
6. A maintainer will review your PR and may request changes

### PR Template

```markdown
## Summary
- Brief description of changes

## Motivation
- Why is this change needed?

## Testing
- How were these changes tested?

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Passes all existing tests
- [ ] Conforms to coding standards
```

---

## Coding Standards

### Python

- **Formatter:** Ruff
- **Type hints:** Required on all public functions
- **Style:** PEP 8, enforced via `ruff check`
- **Docstrings:** Google style for public API

### Rust

- **Formatter:** `rustfmt`
- **Linter:** `clippy` with `-D warnings`
- **Documentation:** `///` doc comments on public items
- **Unsafe:** Avoid unless absolutely necessary; document rationale

### TypeScript

- **Strict mode:** `strict: true` in `tsconfig.json`
- **Style:** Consistent with existing codebase
- **Types:** Explicit types on public exports; avoid `any`

---

## Specification Changes

Changes to the VCP specification (`specs/`) follow a more rigorous process:

1. **Open a discussion issue** describing the proposed change and its motivation
2. **Draft an amendment** following the format in `specs/VCP_SPECIFICATION_v1.1_AMENDMENTS.md`
3. **Include rationale** for why the change is necessary and how it affects existing implementations
4. **Update all three SDKs** to reflect the specification change, or clearly note what remains to be implemented
5. **Update JSON schemas** in `schemas/` to match the new specification

Specification changes require approval from a core maintainer.

---

## Questions?

Open a [discussion](https://github.com/Creed-Space/VCP-SDK/discussions) or reach out to the maintainers — we're happy to help.

Thank you for helping build the future of portable AI context.
