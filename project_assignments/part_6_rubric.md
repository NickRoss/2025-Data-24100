# Part 6 Grading Rubric

## Total Points: 50

---

## Linting (12 points)

| Item | Points |
|------|--------|
| pyproject.toml -- correct rules | 5 |
| format & check passes | 5 |
| pre-commit exists | 2 |

**Grading Notes:**
- Check that pyproject.toml has required ruff configuration
- Run `ruff check` and `ruff format --check` on original code
- Verify .pre-commit-config.yaml exists

---

## OpsFiles (2 points)

| Item | Points |
|------|--------|
| Dockerfile | 1 |
| Makefile | 1 |

**Grading Notes:**
- Dockerfile must exist and build successfully
- Makefile must exist with required targets (build, flask, db_create, db_load, db_clean_account, tests, autodocs)

---

## Directory / File (1 point)

| Item | Points |
|------|--------|
| Uses Logging | 1 |

**Grading Notes:**
- Application uses proper logging instead of print statements
- Check main application code (not test files)

---

## Code Execution (8 points)

| Item | Points |
|------|--------|
| db_clean_account works | 5 |
| db_clean_account accurate | 2 |
| No database committed | 1 |

**Grading Notes:**
- `make db_clean_account` executes without errors
- After running, accounts table should be empty (0 rows)
- Verify with: `sqlite3 data/stocks.db "SELECT COUNT(*) FROM accounts;"`
- .db files should not be in git repository

---

## Flask API Endpoints (6 points)

| Item | Points |
|------|--------|
| V1 endpoints (row_count, symbols) | 2 |
| V2 endpoints (year, open, close, high, low) | 2 |
| V3 endpoints (accounts, stocks, returns) | 2 |

**Grading Notes:**
- V1: Test row_count and symbols endpoints
- V2: Test year, open, close, high, low endpoints for symbols
- V3: Test account management, stock holdings, and portfolio returns calculation

---

## Tests (7 points)

| Item | Points |
|------|--------|
| Tests Run | 5 |
| Tests Complete | 2 |

**Grading Notes:**
- `make tests` executes without import/syntax errors
- All required tests (22-24 tests) are present and pass
- Tests cover v1, v2, and v3 API endpoints

---

## Autodocs (5 points)

| Item | Points |
|------|--------|
| Autodocs Run | 2 |
| Autodocs Complete | 3 |

**Grading Notes:**
- `make autodocs` starts without errors
- Documentation is generated and accessible on port 4040
- API endpoints are documented

---

## Additional Considerations (9 points)

| Item | Points |
|------|--------|
| DRY principle | 4 |
| README documents endpoints | 3 |
| No extraneous files | 2 |

**Grading Notes:**
- **DRY principle**: No significant code duplication, especially in v2 routes
  - Deduct 1-2 points for moderate duplication (50-100 lines)
  - Deduct 3-4 points for severe duplication (100+ lines)
- **README**: Should document all v1, v2, and v3 API endpoints
- **No extraneous files**: No build artifacts, cache files (__pycache__, .coverage, .pytest_cache), or logs committed

---

## Summary

| Category | Points |
|----------|--------|
| Linting | 12 |
| OpsFiles | 2 |
| Directory/File | 1 |
| Code Execution | 8 |
| Flask API Endpoints | 6 |
| Tests | 7 |
| Autodocs | 5 |
| Additional Considerations | 9 |
| **TOTAL** | **50** |

---

