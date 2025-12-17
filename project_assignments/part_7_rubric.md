# Part 7 Grading Rubric

## Total Points: 60

---

## Linting (10 points)

| Item | Points |
|------|--------|
| pyproject.toml -- correct rules | 4 |
| format & check passes | 4 |
| pre-commit exists | 2 |

**Grading Notes:**
- Check that pyproject.toml has required ruff configuration
- Run `ruff check` and `ruff format --check` on original code
- Verify .pre-commit-config.yaml exists and is properly configured
- No print statements allowed (must use logging)

---

## Docker Compose (5 points)

| Item | Points |
|------|--------|
| docker-compose.yml exists and valid | 2 |
| Defines flask-app and mcp-server services | 2 |
| Makefile uses docker compose commands | 1 |

**Grading Notes:**
- docker-compose.yml must be in repository root
- Must define at least two services: Flask app and MCP server
- All Makefile commands must use `docker compose` (not `docker run`)
- Environment variables (RAW_DATA_DIR, DATA_241_API_KEY) passed from host
- Port mappings defined in docker-compose.yml (not Makefile)

---

## Directory / File (2 points)

| Item | Points |
|------|--------|
| Uses Logging (no print statements) | 1 |
| No database committed | 1 |

**Grading Notes:**
- Application uses proper logging with appropriate levels
- Check main application code (not test files)
- .db files should not be in git repository

---

## Code Execution (8 points)

| Item | Points |
|------|--------|
| make db_clean works | 3 |
| make db_clean accurate | 2 |
| make start-all works | 3 |

**Grading Notes:**
- `make db_clean` executes without errors and loads fresh database
- After running, database should be populated with stock data
- `make start-all` starts both Flask app and MCP server successfully
- Services accessible on correct ports (Flask: 4000, MCP: 3000)

---

## Flask API Endpoints (12 points)

| Item | Points |
|------|--------|
| V1 endpoints working (row_count, symbols) | 2 |
| V2 endpoints working (year, prices) | 2 |
| V3 endpoints working (accounts, stocks, returns) | 3 |
| V4 endpoints working (back_test) | 5 |

**Grading Notes:**
- **V1**: Test row_count and symbols endpoints (2 endpoints)
- **V2**: Test year count and price queries (5 endpoints)
- **V3**: Test account CRUD, stock management, returns (6 endpoints)
- **V4**: Test backtesting endpoint with proper validation (5 points)
  - Full credit (5/5): Implementation correct, all tests pass
  - Partial credit (2/5): Critical bug requiring algorithm fix (e.g., broken date handling, incorrect calculations)
  - No credit (0/5): Missing endpoint or completely non-functional
  - Must validate: operator (LT, LTE), purchase_type (B, S), trading days (400 for invalid)
  - Must correctly implement shifted price comparisons
  - Must return proper JSON: `{"return": float, "num_observations": int}`
  - Performance: Requests complete in < 5 seconds (verify indexes)

---

## MCP Server Implementation (10 points)

| Item | Points |
|------|--------|
| MCP server starts and responds | 3 |
| Tool discovery (7 tools) | 3 |
| Tool invocation works | 4 |

**Grading Notes:**
- MCP server accessible on port 3000
- Exposes 7 required tools:
  1. `get_year_count` (V2 API)
  2. `list_accounts` (V3 API)
  3. `create_account` (V3 API)
  4. `get_account_stocks` (V3 API)
  5. `add_stock` (V3 API)
  6. `get_account_return` (V3 API)
  7. `back_test` (V4 API)
- Tools have proper descriptions and schemas
- Tools successfully communicate with Flask API
- Uses async/await patterns correctly

---

## Tests (7 points)

| Item | Points |
|------|--------|
| Tests Run (make tests) | 3 |
| All tests pass (23 tests) | 2 |
| Test 22 exists and tests V4 | 2 |

**Grading Notes:**
- `make tests` executes without import/syntax errors
- All 23 tests present and pass (includes test 22 for v4)
- Test 22 specifically tests `/api/v4/back_test` endpoint
- Tests validate both schema and exact values for backtesting

---

## Autodocs (3 points)

| Item | Points |
|------|--------|
| Autodocs Run | 1 |
| Autodocs Complete | 2 |

**Grading Notes:**
- `make autodocs` starts without errors
- Documentation is generated and accessible on port 4040
- All API endpoints documented (v1, v2, v3, v4)

---

## Additional Considerations (3 points)

| Item | Points |
|------|--------|
| README documents all endpoints | 1 |
| No extraneous files | 1 |
| Code quality (DRY, clean) | 1 |

**Grading Notes:**
- **README**: Documents all v1, v2, v3, and v4 API endpoints
- **No extraneous files**: No build artifacts, cache files, logs committed
- **Code quality**:
  - Follows DRY principle
  - No excessive code duplication
  - Clean separation of concerns
  - No extraneous/unused code

---

## Summary

| Category | Points |
|----------|--------|
| Linting | 10 |
| Docker Compose | 5 |
| Directory/File | 2 |
| Code Execution | 8 |
| Flask API Endpoints | 12 |
| MCP Server Implementation | 10 |
| Tests | 7 |
| Autodocs | 3 |
| Additional Considerations | 3 |
| **TOTAL** | **60** |

---

## Key Part 7 Requirements

### V4 API Backtesting
- Accepts POST requests with JSON body containing:
  - `value_1`, `value_2`: Price targets (e.g., "O1", "C2")
  - `operator`: "LT" or "LTE" only
  - `purchase_type`: "B" (buy) or "S" (sell/short) only
  - `start_date`, `end_date`: YYYY-MM-DD format
- Returns: `{"return": <float>, "num_observations": <int>}`
- Validates trading days (400 for weekends/holidays)
- Only includes observations where all required historical dates exist
- Performance: Indexed queries complete in < 5 seconds

### MCP Server
- Runs on port 3000 using HTTP/SSE transport
- Uses async/await patterns (FastMCP or similar)
- Exposes 7 tools (1 from v2, 5 from v3, 1 from v4)
- Tools communicate with Flask API via HTTP
- Proper error handling and timeouts

### Docker Compose
- All commands use `docker compose` (not `docker run`)
- Both services defined in docker-compose.yml
- Environment variables passed from host
- Port mappings in docker-compose.yml

---
