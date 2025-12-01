#!/usr/bin/env python3
"""
Database Commands Tester - Tests make db_* commands for Part 4.

This script tests the database management commands and validates
database structure and content.

Usage:
    python db_commands_tester.py --repo-dir /path/to/repo
"""

import argparse
import json
import logging
import os
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class DatabaseCommandsTester:
    """Test harness for database management commands."""

    def __init__(self, repo_dir: str, json_output: bool = False, keep_loaded: bool = False):
        """
        Initialize the tester.

        Args:
            repo_dir: Path to the repository to test
            json_output: If True, output results as JSON instead of logs
            keep_loaded: If True, skip cleanup tests and leave database loaded
        """
        self.repo_dir = Path(repo_dir).resolve()
        self.json_output = json_output
        self.keep_loaded = keep_loaded
        self.test_results = {"passed": 0, "failed": 0, "total": 0}
        self.db_path = None  # Will be discovered during tests
        self.errors = []
        self.db_load_time = None  # Track db_load execution time

    def run_make_command(self, command: str, should_succeed: bool = True) -> tuple[bool, str, str, float]:
        """
        Run a make command in the repository directory.

        Args:
            command: Make command to run (e.g., 'db_create')
            should_succeed: Whether the command is expected to succeed

        Returns:
            Tuple of (success, stdout, stderr, elapsed_time_seconds)
        """
        try:
            start_time = time.time()
            result = subprocess.run(
                ["make", command],
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                timeout=900,  # 15 minute timeout for database operations
            )
            elapsed_time = time.time() - start_time

            success = (result.returncode == 0) == should_succeed
            return success, result.stdout, result.stderr, elapsed_time

        except subprocess.TimeoutExpired:
            elapsed_time = 900.0
            logger.error(f"Command 'make {command}' timed out after 900 seconds")
            return False, "", "Timeout", elapsed_time
        except Exception as e:
            logger.error(f"Failed to run 'make {command}': {e}")
            return False, "", str(e), 0.0

    def find_database_file(self) -> Path | None:
        """
        Find the SQLite database file in the repository.

        Returns:
            Path to database file, or None if not found
        """
        # Common locations where students might put the database
        possible_names = ["stocks.db", "stock.db", "data.db", "database.db"]
        possible_dirs = [
            self.repo_dir,
            self.repo_dir / "data",
            self.repo_dir / "db",
            self.repo_dir / "database",
            self.repo_dir / "src",
            self.repo_dir / "app",
        ]

        for directory in possible_dirs:
            if not directory.exists():
                continue
            for name in possible_names:
                db_file = directory / name
                if db_file.exists() and db_file.suffix == ".db":
                    return db_file

        # Recursive search as fallback (excluding .venv)
        for db_file in self.repo_dir.rglob("*.db"):
            if ".venv" not in str(db_file) and "site-packages" not in str(db_file):
                return db_file

        return None

    def verify_database_schema(self, db_path: Path) -> tuple[bool, list[str]]:
        """
        Verify the database has the correct schema.

        Args:
            db_path: Path to the database file

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Check if 'stocks' table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='stocks'"
            )
            if not cursor.fetchone():
                issues.append("Table 'stocks' does not exist")
                conn.close()
                return False, issues

            # Get table schema
            cursor.execute("PRAGMA table_info(stocks)")
            columns = cursor.fetchall()

            if not columns:
                issues.append("Table 'stocks' has no columns")
                conn.close()
                return False, issues

            # Expected columns (we're flexible about exact names/types, but check for basics)
            column_names = [col[1].lower() for col in columns]

            # Check for essential columns (flexible naming)
            essential_patterns = [
                ['symbol', 'stock', 'ticker'],  # Symbol/stock identifier
                ['date', 'time'],  # Date column
                ['open'],  # Open price
                ['close'],  # Close price
                ['high'],  # High price
                ['low'],  # Low price
            ]

            for patterns in essential_patterns:
                found = any(
                    any(pattern in col for pattern in patterns)
                    for col in column_names
                )
                if not found:
                    issues.append(f"Missing column matching patterns: {patterns}")

            conn.close()
            return len(issues) == 0, issues

        except sqlite3.Error as e:
            issues.append(f"Database error: {e}")
            return False, issues
        except Exception as e:
            issues.append(f"Unexpected error: {e}")
            return False, issues

    def get_row_count(self, db_path: Path) -> int | None:
        """
        Get the total row count from the stocks table.

        Args:
            db_path: Path to the database file

        Returns:
            Row count, or None if error
        """
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM stocks")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except sqlite3.Error as e:
            logger.error(f"Database error getting row count: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting row count: {e}")
            return None

    def get_year_counts(self, db_path: Path) -> dict[int, int] | None:
        """
        Get row counts per year from the database.

        Args:
            db_path: Path to the database file

        Returns:
            Dictionary of year -> count, or None if error
        """
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Try to find the date column (might be named differently)
            cursor.execute("PRAGMA table_info(stocks)")
            columns = cursor.fetchall()
            date_column = None

            for col in columns:
                col_name = col[1].lower()
                if 'date' in col_name or 'time' in col_name:
                    date_column = col[1]
                    break

            if not date_column:
                logger.warning("Could not find date column in stocks table")
                conn.close()
                return None

            # Get counts per year
            query = f"""
                SELECT
                    CAST(strftime('%Y', {date_column}) AS INTEGER) as year,
                    COUNT(*) as count
                FROM stocks
                GROUP BY year
                ORDER BY year
            """
            cursor.execute(query)
            results = cursor.fetchall()

            year_counts = {row[0]: row[1] for row in results}
            conn.close()
            return year_counts

        except sqlite3.Error as e:
            logger.error(f"Database error getting year counts: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting year counts: {e}")
            return None

    def check_pandas_usage(self) -> tuple[bool, list[str]]:
        """
        Check for prohibited pandas usage in the codebase.

        Returns:
            Tuple of (is_clean, list_of_violations)
        """
        violations = []

        # Search for prohibited patterns
        prohibited_patterns = [
            ("read_sql", "pandas read_sql is prohibited"),
            ("DataFrame.from_sql", "pandas DataFrame.from_sql is prohibited"),
            ("pd.read_sql", "pd.read_sql is prohibited"),
        ]

        python_files = list(self.repo_dir.rglob("*.py"))
        # Exclude venv and common library directories
        python_files = [
            f for f in python_files
            if not any(exclude in str(f) for exclude in ['.venv', 'site-packages', '__pycache__'])
        ]

        for py_file in python_files:
            try:
                content = py_file.read_text()
                for pattern, message in prohibited_patterns:
                    if pattern in content:
                        violations.append(f"{py_file.name}: {message}")
            except Exception as e:
                logger.debug(f"Could not read {py_file}: {e}")

        return len(violations) == 0, violations

    def check_db_not_committed(self) -> bool:
        """
        Check if database files are committed to git.

        Returns:
            True if database files are NOT committed (good), False if they are committed (bad)
        """
        # First, check if .gitignore exists and warn if not
        gitignore_path = self.repo_dir / ".gitignore"
        if not gitignore_path.exists():
            logger.warning(".gitignore file not found (recommended to have one)")
        else:
            # Check if .gitignore has database patterns
            try:
                gitignore_content = gitignore_path.read_text().lower()
                db_patterns = ["*.db", "stocks.db", "stock.db", ".db", "data/"]
                if not any(pattern in gitignore_content for pattern in db_patterns):
                    logger.warning(".gitignore does not contain database file patterns (recommended)")
            except Exception as e:
                logger.warning(f"Could not read .gitignore: {e}")

        # Now check if database files are actually committed to git
        try:
            # Check if this is a git repository
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                logger.warning("Not a git repository - skipping git commit check")
                return True  # Pass if not a git repo

            # Check for committed .db files
            result = subprocess.run(
                ["git", "ls-files", "*.db"],
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                timeout=5
            )

            committed_db_files = result.stdout.strip().split('\n') if result.stdout.strip() else []

            if committed_db_files:
                logger.error(f"Database files are committed to git: {', '.join(committed_db_files)}")
                return False

            return True

        except subprocess.TimeoutExpired:
            logger.warning("Git check timed out")
            return True  # Don't fail on timeout
        except Exception as e:
            logger.warning(f"Could not check git status: {e}")
            return True  # Don't fail on error

    def test_command(self, test_name: str, test_func: Any) -> bool:
        """
        Run a single test and track results.

        Args:
            test_name: Name of the test
            test_func: Function to run (should return bool)

        Returns:
            True if test passed
        """
        self.test_results["total"] += 1

        if not self.json_output:
            logger.info(f"Testing: {test_name}")

        try:
            success = test_func()

            if success:
                self.test_results["passed"] += 1
                if not self.json_output:
                    logger.info(f"✓ PASSED: {test_name}")
            else:
                self.test_results["failed"] += 1
                if not self.json_output:
                    logger.error(f"✗ FAILED: {test_name}")

            return success

        except Exception as e:
            self.test_results["failed"] += 1
            self.errors.append(f"{test_name}: {str(e)}")
            if not self.json_output:
                logger.error(f"✗ FAILED: {test_name} - {e}")
            return False

    def run_all_tests(self) -> bool:
        """
        Run all database command tests.

        Returns:
            True if all tests passed
        """
        if not self.json_output:
            logger.info("=" * 70)
            logger.info("RUNNING DATABASE COMMAND TESTS (Part 4)")
            logger.info("=" * 70)
            logger.info(f"Repository: {self.repo_dir}\n")

        all_passed = True

        # Test 1: Clean up any existing database
        if not self.json_output:
            logger.info("\n--- Initial Cleanup ---")

        def cleanup_test():
            # Try to remove existing database (don't fail if it doesn't exist)
            success, stdout, stderr, elapsed = self.run_make_command("db_rm", should_succeed=True)
            # This should not fail even if DB doesn't exist, but we won't count it as a test
            return True

        self.test_command("Initial cleanup (make db_rm)", cleanup_test)

        # Test 2: Create database
        if not self.json_output:
            logger.info("\n--- Testing Database Creation ---")

        def create_test():
            success, stdout, stderr, elapsed = self.run_make_command("db_create", should_succeed=True)
            if not success:
                self.errors.append(f"db_create failed: {stderr}")
            return success

        all_passed = self.test_command("Create database (make db_create)", create_test) and all_passed

        # Test 3: Verify database file exists
        def file_exists_test():
            self.db_path = self.find_database_file()
            if not self.db_path:
                self.errors.append("Database file not found after db_create")
                return False
            if not self.json_output:
                logger.info(f"  Found database at: {self.db_path}")
            return True

        all_passed = self.test_command("Database file exists", file_exists_test) and all_passed

        # Test 4: Verify database schema
        def schema_test():
            if not self.db_path:
                return False
            is_valid, issues = self.verify_database_schema(self.db_path)
            if not is_valid:
                self.errors.extend(issues)
            return is_valid

        all_passed = self.test_command("Database schema is correct", schema_test) and all_passed

        # Test 5: db_create should fail if database already exists
        if not self.json_output:
            logger.info("\n--- Testing Duplicate Creation Error ---")

        def duplicate_create_test():
            success, stdout, stderr, elapsed = self.run_make_command("db_create", should_succeed=False)
            if not success:
                self.errors.append("db_create should error when database already exists")
            return success

        all_passed = self.test_command("db_create errors on existing DB", duplicate_create_test) and all_passed

        # Test 6: Load data into database
        if not self.json_output:
            logger.info("\n--- Testing Database Load ---")

        def load_test():
            success, stdout, stderr, elapsed = self.run_make_command("db_load", should_succeed=True)
            self.db_load_time = elapsed
            if not success:
                self.errors.append(f"db_load failed: {stderr}")
            else:
                if not self.json_output:
                    logger.info(f"  db_load completed in {elapsed:.2f} seconds")
            return success

        all_passed = self.test_command("Load data (make db_load)", load_test) and all_passed

        # Test 7: Verify data was loaded (row count > 0)
        def data_loaded_test():
            if not self.db_path:
                return False
            row_count = self.get_row_count(self.db_path)
            if row_count is None:
                self.errors.append("Could not get row count from database")
                return False
            if row_count == 0:
                self.errors.append("Database has 0 rows after db_load")
                return False
            if not self.json_output:
                logger.info(f"  Database has {row_count:,} rows")
            return True

        all_passed = self.test_command("Data loaded into database", data_loaded_test) and all_passed

        # Test 8: Get year counts for validation
        if not self.json_output:
            logger.info("\n--- Validating Data Distribution ---")

        year_counts = None
        if self.db_path:
            year_counts = self.get_year_counts(self.db_path)
            if year_counts and not self.json_output:
                logger.info("  Year counts:")
                for year in sorted(year_counts.keys()):
                    logger.info(f"    {year}: {year_counts[year]:,} rows")

        # Skip cleanup tests if keep_loaded flag is set
        if not self.keep_loaded:
            # Test 9: Delete database
            if not self.json_output:
                logger.info("\n--- Testing Database Removal ---")

            def remove_test():
                success, stdout, stderr, elapsed = self.run_make_command("db_rm", should_succeed=True)
                if not success:
                    self.errors.append(f"db_rm failed: {stderr}")
                return success

            all_passed = self.test_command("Remove database (make db_rm)", remove_test) and all_passed

            # Test 10: Verify database file was deleted
            def removed_test():
                if self.db_path and self.db_path.exists():
                    self.errors.append("Database file still exists after db_rm")
                    return False
                return True

            all_passed = self.test_command("Database file removed", removed_test) and all_passed

            # Test 11: Test db_clean (should work from fresh state)
            if not self.json_output:
                logger.info("\n--- Testing Database Clean (Fresh State) ---")

            def clean_test():
                success, stdout, stderr, elapsed = self.run_make_command("db_clean", should_succeed=True)
                if not success:
                    self.errors.append(f"db_clean failed: {stderr}")
                return success

            all_passed = self.test_command("Clean database (make db_clean)", clean_test) and all_passed

            # Test 12: Verify database exists and has data after clean
            def clean_data_test():
                self.db_path = self.find_database_file()
                if not self.db_path:
                    self.errors.append("Database file not found after db_clean")
                    return False
                row_count = self.get_row_count(self.db_path)
                if row_count is None or row_count == 0:
                    self.errors.append("Database empty after db_clean")
                    return False
                if not self.json_output:
                    logger.info(f"  Database has {row_count:,} rows after clean")
                return True

            all_passed = self.test_command("Database populated after db_clean", clean_data_test) and all_passed
        else:
            if not self.json_output:
                logger.info("\n--- Skipping cleanup tests (--keep-loaded flag set) ---")
                logger.info("  Database left loaded for subsequent Flask testing")

        # Test 13: Check for prohibited pandas usage
        if not self.json_output:
            logger.info("\n--- Code Quality Checks ---")

        def pandas_test():
            is_clean, violations = self.check_pandas_usage()
            if not is_clean:
                self.errors.extend(violations)
            return is_clean

        all_passed = self.test_command("No prohibited pandas usage", pandas_test) and all_passed

        # Test 14: Check database not committed to git
        def db_not_committed_test():
            result = self.check_db_not_committed()
            if not result:
                self.errors.append("Database files are committed to git repository")
            return result

        all_passed = self.test_command("Database files not committed to git", db_not_committed_test) and all_passed

        # Print summary
        self.print_summary(year_counts)

        return all_passed

    def print_summary(self, year_counts: dict[int, int] | None = None) -> None:
        """Print a summary of test results."""
        total = self.test_results["total"]
        passed = self.test_results["passed"]
        failed = self.test_results["failed"]

        if self.json_output:
            # Output JSON format for parsing by other scripts
            result = {
                "total_tests": total,
                "passed": passed,
                "failed": failed,
                "all_passed": failed == 0 and total > 0,
                "errors": self.errors,
                "year_counts": year_counts,
                "db_path": str(self.db_path) if self.db_path else None,
                "db_load_time_seconds": self.db_load_time,
            }
            print(json.dumps(result, indent=2))
            return

        logger.info("\n" + "=" * 70)
        logger.info("DATABASE TESTS SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Total tests: {total}")
        logger.info(f"Passed: {passed}")
        logger.info(f"Failed: {failed}")

        if self.errors:
            logger.info("\nErrors/Issues:")
            for error in self.errors:
                logger.info(f"  - {error}")

        if failed == 0 and total > 0:
            logger.info("\n✓ ALL DATABASE TESTS PASSED!")
        elif total > 0:
            logger.warning(f"\n✗ {failed} DATABASE TEST(S) FAILED")
        else:
            logger.info("\nNo tests were run")


def main():
    """Main entry point for the database commands tester."""
    parser = argparse.ArgumentParser(
        description="Database Commands Tester - Test make db_* commands",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test database commands in a repository
  python db_commands_tester.py --repo-dir ./2025-Data-24100-Group-1

  # Output JSON for script parsing
  python db_commands_tester.py --repo-dir ./Group-1 --json

  # Enable debug logging
  python db_commands_tester.py --repo-dir ./Group-1 --debug
        """,
    )

    parser.add_argument(
        "--repo-dir",
        required=True,
        help="Path to the repository to test",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format (for script parsing)",
    )

    parser.add_argument(
        "--keep-loaded",
        action="store_true",
        help="Skip cleanup tests and leave database loaded for Flask testing",
    )

    args = parser.parse_args()

    # Configure logging level
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)

    # If JSON output is requested, suppress all logging
    if args.json:
        logging.getLogger().setLevel(logging.CRITICAL)

    # Verify repository directory exists
    repo_path = Path(args.repo_dir)
    if not repo_path.exists():
        logger.error(f"Repository directory does not exist: {repo_path}")
        sys.exit(1)

    if not repo_path.is_dir():
        logger.error(f"Not a directory: {repo_path}")
        sys.exit(1)

    # Create tester and run tests
    tester = DatabaseCommandsTester(repo_dir=str(repo_path), json_output=args.json, keep_loaded=args.keep_loaded)

    try:
        all_passed = tester.run_all_tests()

        # Exit with appropriate code
        sys.exit(0 if all_passed else 1)

    except KeyboardInterrupt:
        logger.warning("\nTests interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"Unexpected error during testing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
