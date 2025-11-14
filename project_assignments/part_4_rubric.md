## Part 4 Rubric

### Part 4 Rubric Grading Task List

## Repository organization
- [ ] Proper hash in Canvas
- [ ] Review Commits -- Everything a PR on Main (no direct commits to main)
- [ ] README with basic info & up to date (includes DB setup instructions)

## File organization

- [ ] `README.md` with basic info & up to date
  - Should document how to set up and use the database
  - Should explain the new make commands (db_create, db_load, db_rm, db_clean, db_interactive)
- [ ] General Hygiene (no unnecessary files, directories, no name, v2, etc.)
- [ ] `pyproject.toml` - properly configured
- [ ] `Dockerfile` - properly configured (includes SQLite system library if needed)
- [ ] `Makefile` - has all commands including new DB management commands
- [ ] Database file (`stocks.db`) is in `.gitignore` (not committed to repo)
- [ ] `db_manage.py` exists and is properly structured

## Code execution

- [ ] `make db_create` creates database and `stocks` table
  - Raises error if database already exists
  - Creates table in mounted volume location
- [ ] `make db_load` loads data from ZIP files to database
  - Does not use pandas for loading
- [ ] `make db_rm` deletes database file
- [ ] `make db_clean` deletes and recreates database (no error if doesn't exist)
- [ ] `make db_interactive` opens interactive SQLite session
- [ ] `make flask` starts Flask server
  - Server starts in < 10 seconds
  - All responses take < 2 seconds
- [ ] All previous endpoints (v1, v2) still work correctly
- [ ] Output Correct for all endpoints

## Code quality

- [ ] No pandas used for database operations (no pandas.read_sql, no DataFrame loading)
- [ ] SQL queries are written explicitly (not using pandas abstractions)
- [ ] No global DataFrame variables
- [ ] No global connection variables
- [ ] Proper separation of concerns (database logic separated from route logic)
- [ ] Database operations use appropriate abstractions
- [ ] Indexes added to `stocks` table for performance
- [ ] Comments exist and make sense
- [ ] Code follows DRY principle
- [ ] No extraneous/unused code

## Documentation and non-code quality

- [ ] README clearly explains database setup process
- [ ] README documents all new make commands and their purposes
- [ ] Code comments explain complex logic or database operations
- [ ] Function docstrings present where appropriate
- [ ] Consistent code style and abstraction levels throughout

## Grader Instructions for getting code and verifying branches

1. Clone the repo locally.
2. Verify that there are no commits directly to the main branch. You can do this by either clicking on the main repo page the link which says something like `12 commits`, or you can just go to `https://github.com/[ORG]/[REPO]/commits/main/` to see the commit history. Look to make sure that _everything_ is "Merge pull request #..." and not a direct commit. The initial commit into the repo may be a single commit.
3. Use the commit hash provided by the students in canvas. To checkout at a single location type in, at the command line, in the repository directory: `git checkout COMMIT HASH`.
4. You will be in a detached head state. If you want to verify you are at the correct location, type in `git log -1 --format=%H` which should display the last commit. `git status` should mention that head is detached and the tree is clean.

## Part 4 Rubric

| Category | Criteria | Points |
|----------|----------|---------|
| Proper Submission (hash/PR/etc.) & Main Readme | | 5 |
| Directory / File | General Hygiene (no unnecessary files, directories, no name, v2, etc.) | 5 |
| | pyproject.toml | 5 |
| | Dockerfile | 5 |
| | Makefile (has all commands) | 5 |
| Database Operations | Works as expected | 10 |
| Code Execution | Code Run -> generates output | 20 |
| | Output Correct (API) | 10 |
| Code Quality | Comments exist (make sense) followed code instructions | 5 |
| Other | | |
| **Total** | | **70** |
