## Part 5 Rubric

### Part 5 Rubric Grading Task List

## Repository organization
- [ ] Proper hash in Canvas
- [ ] Review Commits -- Everything a PR on Main (no direct commits to main)
- [ ] README with basic info & up to date (includes v3 endpoint documentation)

## File organization

- [ ] `README.md` with basic info & up to date
  - Should document all v3 endpoints
  - Should explain account system functionality
  - Should document linting and pre-commit setup
- [ ] General Hygiene (no unnecessary files, directories, no name, v2, etc.)
- [ ] `pyproject.toml` - properly configured (includes ruff configuration)
- [ ] `Dockerfile` - properly configured
- [ ] `Makefile` - has all commands including `db_clean_account`
- [ ] `.pre-commit-config.yaml` exists in repo (or `pre-commit-config.yaml` as specified)
- [ ] Database file (`stocks.db`) is in `.gitignore` (not committed to repo)
- [ ] `db_manage.py` updated with new table creation

## Code execution

- [ ] `make db_create` creates `accounts` and `stocks_owned` tables
- [ ] `make db_clean_account` resets accounts and stocks_owned tables (maintains structure, deletes rows)
- [ ] `make flask` starts Flask server
  - All responses take < 5 seconds
- [ ] All previous endpoints (v1, v2) still work correctly
- [ ] v3 endpoints work correctly:
  - GET `/api/v3/accounts` - lists all accounts
  - POST `/api/v3/accounts` - creates account (201) or returns 409 if exists
  - DELETE `/api/v3/accounts` - deletes account (204) or returns 404
  - GET `/api/v3/accounts/<int>` - lists stocks for account (404 if doesn't exist)
  - GET `/api/v3/stocks/<symbol>` - lists holdings for symbol
  - POST `/api/v3/stocks` - adds stock to account (201) or 400 if invalid date
  - DELETE `/api/v3/stocks` - removes stock from account (204) or 404
  - GET `/api/v3/accounts/return/<int>` - calculates return (404 if doesn't exist)
- [ ] Authentication works for v3 endpoints (401 if invalid/missing API key)
- [ ] Date validation works (400 if purchase_date or sale_date not valid trading days)
- [ ] Return calculation is correct
- [ ] Output Correct for all endpoints

## Code quality

- [ ] Code passes `ruff` check using pyproject.toml configuration
- [ ] Pre-commit hook can be installed and runs successfully
- [ ] No `print` statements (uses logging instead)
- [ ] Appropriate logging levels used throughout
- [ ] Proper separation of concerns
- [ ] Code follows DRY principle
- [ ] No extraneous/unused code
- [ ] Indexes added for performance (if needed)
- [ ] Comments exist and make sense
- [ ] All previous Part IV feedback addressed

## Documentation and non-code quality

- [ ] README clearly documents all v3 endpoints with examples
- [ ] README explains account system and how it works
- [ ] README documents linting setup and pre-commit hooks
- [ ] Code docstrings present and meaningful (not low-effort like "This is the doc string")
- [ ] Docstrings explain purpose and functionality
- [ ] Code comments explain complex logic
- [ ] Consistent code style and abstraction levels throughout
- [ ] All documentation is up to date

## Grader Instructions for getting code and verifying branches

1. Clone the repo locally.
2. Verify that there are no commits directly to the main branch. You can do this by either clicking on the main repo page the link which says something like `12 commits`, or you can just go to `https://github.com/[ORG]/[REPO]/commits/main/` to see the commit history. Look to make sure that _everything_ is "Merge pull request #..." and not a direct commit. The initial commit into the repo may be a single commit.
3. Use the commit hash provided by the students in canvas. To checkout at a single location type in, at the command line, in the repository directory: `git checkout COMMIT HASH`.
4. You will be in a detached head state. If you want to verify you are at the correct location, type in `git log -1 --format=%H` which should display the last commit. `git status` should mention that head is detached and the tree is clean.

## Part 5 Rubric

| Rubric | Responsibility | Points |
|--------|----------------|--------|
| Proper hash in Canvas | Nick | 2 |
| Review Commits – Everything a PR on Main | Nick | 2 |
| README with basic info & up to date | Victoria | 5 |
| pyproject.toml – correct rules | Jihee | 3 |
| format & check passes | Jihee | 5 |
| pre-commit exists | Jihee | 2 |
| Directory / File | | |
| General Hygiene (no unnecessary files, directories, no name, v2, etc.) | Victoria | 5 |
| pyproject.toml | Nick | 5 |
| Dockerfile | Nick | 5 |
| Makefile (has all commands) | Nick | 5 |
| no print statements | Victoria | 3 |
| Uses Logging | Victoria | 3 |
| Code Execution | | |
| Code Run -> generates output | Nick | 20 |
| Output Correct | Nick | 11 |
| Code Quality | | |
| Comments exist and make sense | Victoria | 5 |
| Other | | |
| **Total** | | **81** |
