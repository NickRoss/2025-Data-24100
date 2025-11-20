#!/usr/bin/env python3
"""
Flask API Autograder - Modular testing for different API versions.

This script tests Flask API endpoints and validates responses.
It assumes the Flask server is already running (typically via part_X_build_run.sh).

Usage:
    python flask_autograder.py --api v1 --key YOUR_KEY
    python flask_autograder.py --api v1 --api v2 --url http://localhost:5000
"""

import argparse
import logging
import os
import sys
import time
import warnings

import requests
from jsonschema import Draft7Validator

# Suppress urllib3 header parsing warnings (they're noisy and we handle the responses fine)
warnings.filterwarnings("ignore", message=".*Failed to parse headers.*")
warnings.filterwarnings("ignore", module="urllib3")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Suppress urllib3 connection/response warnings - they log header issues as WARNING
logging.getLogger("urllib3.connection").setLevel(logging.ERROR)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)

# Track if we've seen header issues (to report once per test run)
_header_issues_detected = False

# Expected test counts for each API version (fixed, doesn't change based on failures)
EXPECTED_TEST_COUNTS = {
    "v1": 7,  # 3 endpoint tests + 4 auth tests
    "v2": 18,  # 4 valid years + 4 invalid years + 5 price types + 1 invalid symbol + 4 auth
    "v3": 31,  # See detailed breakdown in run_v3_tests
}

# Schema Definitions
API_SCHEMAS = {
    # Part 2 / v1 schemas
    "row_count": {
        "type": "object",
        "required": ["row_count"],
        "properties": {"row_count": {"type": "integer", "minimum": 0}},
        "additionalProperties": False,
    },
    "unique_nyse_stock_count": {
        "type": "object",
        "required": ["unique_nyse_stock_count"],
        "properties": {"unique_nyse_stock_count": {"type": "integer", "minimum": 0}},
        "additionalProperties": False,
    },
    "unique_nasdaq_stock_count": {
        "type": "object",
        "required": ["unique_nasdaq_stock_count"],
        "properties": {"unique_nasdaq_stock_count": {"type": "integer", "minimum": 0}},
        "additionalProperties": False,
    },
    # Part 3 / v2 schemas
    "v2_year_count": {
        "type": "object",
        "required": ["year", "count"],
        "properties": {
            "year": {"type": "integer", "minimum": 2010, "maximum": 2020},
            "count": {"type": "integer", "minimum": 0},
        },
        "additionalProperties": False,
    },
    "v2_open_price_info": {
        "type": "object",
        "required": ["symbol", "price_info"],
        "properties": {
            "symbol": {"type": "string", "minLength": 1},
            "price_info": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["date", "open"],
                    "properties": {
                        "date": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
                        "open": {"type": "number"},
                    },
                    "additionalProperties": False,
                },
            },
        },
        "additionalProperties": False,
    },
    "v2_close_price_info": {
        "type": "object",
        "required": ["symbol", "price_info"],
        "properties": {
            "symbol": {"type": "string", "minLength": 1},
            "price_info": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["date", "close"],
                    "properties": {
                        "date": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
                        "close": {"type": "number"},
                    },
                    "additionalProperties": False,
                },
            },
        },
        "additionalProperties": False,
    },
    "v2_high_price_info": {
        "type": "object",
        "required": ["symbol", "price_info"],
        "properties": {
            "symbol": {"type": "string", "minLength": 1},
            "price_info": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["date", "high"],
                    "properties": {
                        "date": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
                        "high": {"type": "number"},
                    },
                    "additionalProperties": False,
                },
            },
        },
        "additionalProperties": False,
    },
    "v2_low_price_info": {
        "type": "object",
        "required": ["symbol", "price_info"],
        "properties": {
            "symbol": {"type": "string", "minLength": 1},
            "price_info": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["date", "low"],
                    "properties": {
                        "date": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
                        "low": {"type": "number"},
                    },
                    "additionalProperties": False,
                },
            },
        },
        "additionalProperties": False,
    },
    "v2_high_low_price_info": {
        "type": "object",
        "required": ["symbol", "price_info"],
        "properties": {
            "symbol": {"type": "string", "minLength": 1},
            "price_info": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["date", "high_low"],
                    "properties": {
                        "date": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
                        "high_low": {"type": "number"},
                    },
                    "additionalProperties": False,
                },
            },
        },
        "additionalProperties": False,
    },
    # Part 5 / v3 schemas
    "v3_accounts_list": {
        "type": "array",
        "items": {
            "type": "object",
            "required": ["account_id", "name"],
            "properties": {
                "account_id": {"type": "integer"},
                "name": {"type": "string", "minLength": 1},
            },
            "additionalProperties": False,
        },
    },
    "v3_account_created": {
        "type": "object",
        "required": ["account_id"],
        "properties": {"account_id": {"type": "integer", "minimum": 1}},
        "additionalProperties": False,
    },
    "v3_account_deleted": {
        "type": "object",
        "required": ["account_id"],
        "properties": {"account_id": {"type": "integer"}},
        "additionalProperties": False,
    },
    "v3_account_details": {
        "type": "object",
        "required": ["account_id", "name", "stock_holdings"],
        "properties": {
            "account_id": {"type": "integer"},
            "name": {"type": "string", "minLength": 1},
            "stock_holdings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": [
                        "symbol",
                        "purchase_date",
                        "sale_date",
                        "number_of_shares",
                    ],
                    "properties": {
                        "symbol": {"type": "string", "minLength": 1},
                        "purchase_date": {
                            "type": "string",
                            "pattern": r"^\d{4}-\d{2}-\d{2}$",
                        },
                        "sale_date": {
                            "type": "string",
                            "pattern": r"^\d{4}-\d{2}-\d{2}$",
                        },
                        "number_of_shares": {"type": "integer", "minimum": 1},
                    },
                    "additionalProperties": False,
                },
            },
        },
        "additionalProperties": False,
    },
    "v3_stock_holdings": {
        "type": "object",
        "required": ["symbol", "holdings"],
        "properties": {
            "symbol": {"type": "string", "minLength": 1},
            "holdings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": [
                        "account_id",
                        "purchase_date",
                        "sale_date",
                        "number_of_shares",
                    ],
                    "properties": {
                        "account_id": {"type": "integer"},
                        "purchase_date": {
                            "type": "string",
                            "pattern": r"^\d{4}-\d{2}-\d{2}$",
                        },
                        "sale_date": {
                            "type": "string",
                            "pattern": r"^\d{4}-\d{2}-\d{2}$",
                        },
                        "number_of_shares": {"type": "integer", "minimum": 1},
                    },
                    "additionalProperties": False,
                },
            },
        },
        "additionalProperties": False,
    },
    "v3_account_return": {
        "type": "object",
        "required": ["account_id", "return"],
        "properties": {"account_id": {"type": "integer"}, "return": {"type": "number"}},
        "additionalProperties": False,
    },
}


class FlaskAPITester:
    """Test harness for Flask API endpoints."""

    def __init__(
        self,
        base_url: str = "http://localhost:4000",
        api_key: str | None = None,
        json_output: bool = False,
    ):
        """
        Initialize the tester.

        Args:
            base_url: Base URL for the Flask application
            api_key: API key for authentication
            json_output: If True, output results as JSON instead of logs
        """
        self.base_url = base_url
        self.api_key = api_key
        self.json_output = json_output
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "total": 0,
            "expected_total": 0,  # Expected number of tests (fixed)
        }
        # Track results by API version
        self.results_by_version = {
            "v1": {"passed": 0, "failed": 0, "total": 0},
            "v2": {"passed": 0, "failed": 0, "total": 0},
            "v3": {"passed": 0, "failed": 0, "total": 0},
        }
        self.current_api_version = (
            None  # Track which API version is currently being tested
        )
        self.endpoint_data = {}  # Store actual data returned from endpoints
        self.return_calculations = {}  # Store return calculations for reporting

    def calculate_expected_return(self, holdings: list[dict]) -> float:
        """
        Calculate the expected return for a list of stock holdings.

        Args:
            holdings: List of holdings with symbol, purchase_date, sale_date, number_of_shares

        Returns:
            Expected return as a float, or None if calculation fails
        """
        total_return = 0.0

        for holding in holdings:
            symbol = holding["symbol"]
            purchase_date = holding["purchase_date"]
            sale_date = holding["sale_date"]
            shares = holding["number_of_shares"]

            # Get purchase price (open on purchase date)
            purchase_data, purchase_status, _ = self.make_request(
                f"/api/v2/open/{symbol}", use_api_key=True
            )

            if purchase_status != 200 or not purchase_data:
                logger.debug(
                    f"Failed to get purchase price for {symbol} on {purchase_date}"
                )
                return None

            # Find the purchase date price
            purchase_price = None
            for price_point in purchase_data.get("price_info", []):
                if price_point.get("date") == purchase_date:
                    purchase_price = price_point.get("open")
                    break

            if purchase_price is None:
                logger.debug(f"No purchase price found for {symbol} on {purchase_date}")
                return None

            # Get sale price (close on sale date)
            sale_data, sale_status, _ = self.make_request(
                f"/api/v2/close/{symbol}", use_api_key=True
            )

            if sale_status != 200 or not sale_data:
                logger.debug(f"Failed to get sale price for {symbol} on {sale_date}")
                return None

            # Find the sale date price
            sale_price = None
            for price_point in sale_data.get("price_info", []):
                if price_point.get("date") == sale_date:
                    sale_price = price_point.get("close")
                    break

            if sale_price is None:
                logger.debug(f"No sale price found for {symbol} on {sale_date}")
                return None

            # Calculate return for this holding
            holding_return = (sale_price - purchase_price) * shares
            total_return += holding_return

            logger.debug(
                f"{symbol}: bought {shares} @ ${purchase_price:.2f} on {purchase_date}, "
                f"sold @ ${sale_price:.2f} on {sale_date}, "
                f"return = ${holding_return:.2f}"
            )

        return total_return

    def make_request(
        self,
        endpoint: str,
        method: str = "GET",
        use_api_key: bool = True,
        custom_api_key: str | None = None,
        expected_status_codes: list[int] | None = None,
        json_data: dict | None = None,
    ) -> tuple[dict | None, int, float]:
        """
        Make an HTTP request to the specified endpoint.

        Args:
            endpoint: API endpoint to call
            method: HTTP method (default: GET)
            use_api_key: Whether to include the API key in headers
            custom_api_key: Custom API key to use (overrides default)
            expected_status_codes: List of expected status codes
            json_data: JSON data to send in request body (for POST/DELETE)

        Returns:
            Tuple of (response_data, status_code, elapsed_time_ms)
        """
        if expected_status_codes is None:
            expected_status_codes = [200]

        headers = {"Content-Type": "application/json"}

        if use_api_key:
            key = custom_api_key if custom_api_key else self.api_key
            if key:
                headers["DATA-241-API-KEY"] = key

        url = f"{self.base_url}{endpoint}"

        try:
            start_time = time.time()
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(
                    url, headers=headers, json=json_data, timeout=10
                )
            elif method == "DELETE":
                response = requests.delete(
                    url, headers=headers, json=json_data, timeout=10
                )
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None, 500, 0.0
            elapsed_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            # Check for malformed headers (silently track for summary)
            global _header_issues_detected
            if (
                not _header_issues_detected
                and hasattr(response, "raw")
                and hasattr(response.raw, "_original_response")
            ):
                raw_response = response.raw._original_response
                if hasattr(raw_response, "msg") and hasattr(
                    raw_response.msg, "defects"
                ):
                    if raw_response.msg.defects:
                        _header_issues_detected = True

            # Try to parse JSON response for successful requests
            # 204 No Content should not have a body
            if response.status_code in [200, 201]:
                try:
                    return response.json(), response.status_code, elapsed_time
                except ValueError:
                    logger.debug(f"Response is not valid JSON: {response.text[:100]}")
                    return None, response.status_code, elapsed_time
            elif response.status_code == 204:
                # 204 No Content - should not have a body
                return None, response.status_code, elapsed_time

            return None, response.status_code, elapsed_time

        except requests.exceptions.ConnectionError:
            logger.error(
                f"Connection error: Could not connect to {self.base_url}. "
                "Is the Flask server running?"
            )
            return None, 503, 0.0
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for {url}")
            return None, 504, 0.0
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None, 500, 0.0

    def validate_response(self, data: dict, schema: dict) -> tuple[bool, list[str]]:
        """
        Validate response data against a JSON schema.

        Args:
            data: Response data to validate
            schema: JSON schema to validate against

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        validator = Draft7Validator(schema)
        errors = list(validator.iter_errors(data))

        if not errors:
            return True, []

        # Collect unique error messages
        unique_errors = set()
        for error in errors:
            # Create path string for context
            path_parts = [str(p) for p in error.path if not str(p).isdigit()]
            base_path = ".".join(path_parts) if path_parts else "root"
            error_msg = f"{base_path}: {error.message}"
            unique_errors.add(error_msg)

        # Limit to 5 errors for readability
        error_list = sorted(unique_errors)
        if len(error_list) > 5:
            error_list = error_list[:5]
            error_list.append("... (additional errors omitted)")

        return False, error_list

    def test_endpoint(
        self,
        endpoint: str,
        method: str = "GET",
        schema: dict | None = None,
        use_api_key: bool = True,
        custom_api_key: str | None = None,
        expected_status_codes: list[int] | None = None,
        test_name: str = "",
        endpoint_key: str | None = None,
        json_data: dict | None = None,
    ) -> tuple[bool, dict | None]:
        """
        Test a single endpoint.

        Args:
            endpoint: API endpoint to test
            method: HTTP method (GET, POST, DELETE)
            schema: JSON schema for validation (optional)
            use_api_key: Whether to include API key
            custom_api_key: Custom API key for testing
            expected_status_codes: Expected HTTP status codes
            test_name: Name/description of the test
            endpoint_key: Key to store endpoint data under (for summary reporting)
            json_data: JSON data to send in request body

        Returns:
            Tuple of (success, response_data)
        """
        if expected_status_codes is None:
            expected_status_codes = [200]

        self.test_results["total"] += 1
        # Track by API version if set
        if self.current_api_version:
            self.results_by_version[self.current_api_version]["total"] += 1

        display_name = test_name or f"{method} {endpoint}"

        if not self.json_output:
            logger.info(f"Testing: {display_name}")

        data, status_code, elapsed_time = self.make_request(
            endpoint,
            method=method,
            use_api_key=use_api_key,
            custom_api_key=custom_api_key,
            expected_status_codes=expected_status_codes,
            json_data=json_data,
        )

        # Check status code
        if status_code not in expected_status_codes:
            if not self.json_output:
                logger.error(
                    f"✗ FAILED: {display_name} - "
                    f"Expected status {expected_status_codes}, got {status_code} ({elapsed_time:.0f}ms)"
                )
            self.test_results["failed"] += 1
            if self.current_api_version:
                self.results_by_version[self.current_api_version]["failed"] += 1
            return False, data

        # If we only care about status code (no schema validation needed), return success
        # 204 No Content should not have a body, so no schema validation
        if status_code == 204 or (status_code not in [200, 201]) or schema is None:
            if not self.json_output:
                logger.info(
                    f"✓ PASSED: {display_name} - Status {status_code} ({elapsed_time:.0f}ms)"
                )
            self.test_results["passed"] += 1
            if self.current_api_version:
                self.results_by_version[self.current_api_version]["passed"] += 1
            return True, data

        # Validate response schema
        if data is None:
            if not self.json_output:
                logger.error(
                    f"✗ FAILED: {display_name} - No response data received ({elapsed_time:.0f}ms)"
                )
            self.test_results["failed"] += 1
            if self.current_api_version:
                self.results_by_version[self.current_api_version]["failed"] += 1
            return False, None

        is_valid, errors = self.validate_response(data, schema)

        if not is_valid:
            if not self.json_output:
                logger.error(
                    f"✗ FAILED: {display_name} - Schema validation errors ({elapsed_time:.0f}ms):"
                )
                for error in errors:
                    logger.error(f"  - {error}")
            self.test_results["failed"] += 1
            if self.current_api_version:
                self.results_by_version[self.current_api_version]["failed"] += 1
            return False, data

        # Success! Store data if endpoint_key provided
        if endpoint_key and data:
            self.endpoint_data[endpoint_key] = data

        if not self.json_output:
            # Truncate long responses to first 60 characters
            data_str = str(data)
            if len(data_str) > 60:
                data_str = data_str[:60] + "..."
            logger.info(f"✓ PASSED: {display_name} - {data_str} ({elapsed_time:.0f}ms)")
        self.test_results["passed"] += 1
        if self.current_api_version:
            self.results_by_version[self.current_api_version]["passed"] += 1
        return True, data

    def run_v1_tests(self) -> bool:
        """
        Run v1 API endpoint tests (Part 2).

        Tests:
        - /api/v1/row_count (with valid API key)
        - /api/v1/unique_nyse_stock_count (with valid API key)
        - /api/v1/unique_nasdaq_stock_count (with valid API key)
        - Authentication on row_count (401 for missing/invalid keys)
        - Authentication on NYSE endpoint (401 for missing key)
        - Authentication on NASDAQ endpoint (401 for missing key)

        Returns:
            True if all tests passed, False otherwise
        """
        # Set current API version
        self.current_api_version = "v1"

        # Set expected test count for v1
        self.test_results["expected_total"] += EXPECTED_TEST_COUNTS["v1"]

        if not self.json_output:
            logger.info("=" * 70)
            logger.info("RUNNING V1 API TESTS (Part 2)")
            logger.info("=" * 70)

        all_passed = True

        # Test 1: row_count endpoint
        if not self.json_output:
            logger.info("\n--- Testing /api/v1/row_count ---")
        success, _ = self.test_endpoint(
            "/api/v1/row_count",
            schema=API_SCHEMAS["row_count"],
            test_name="Row count with valid API key",
            endpoint_key="row_count",
        )
        all_passed = all_passed and success

        # Test 2: unique_nyse_stock_count endpoint
        if not self.json_output:
            logger.info("\n--- Testing /api/v1/unique_nyse_stock_count ---")
        success, _ = self.test_endpoint(
            "/api/v1/unique_nyse_stock_count",
            schema=API_SCHEMAS["unique_nyse_stock_count"],
            test_name="NYSE unique stock count with valid API key",
            endpoint_key="unique_nyse_stock_count",
        )
        all_passed = all_passed and success

        # Test 3: unique_nasdaq_stock_count endpoint
        if not self.json_output:
            logger.info("\n--- Testing /api/v1/unique_nasdaq_stock_count ---")
        success, _ = self.test_endpoint(
            "/api/v1/unique_nasdaq_stock_count",
            schema=API_SCHEMAS["unique_nasdaq_stock_count"],
            test_name="NASDAQ unique stock count with valid API key",
            endpoint_key="unique_nasdaq_stock_count",
        )
        all_passed = all_passed and success

        # Test 4: Authentication - missing API key on row_count
        if not self.json_output:
            logger.info("\n--- Testing authentication (missing API key) ---")
        success, _ = self.test_endpoint(
            "/api/v1/row_count",
            use_api_key=False,
            expected_status_codes=[401],
            test_name="Row count without API key (should return 401)",
        )
        all_passed = all_passed and success

        # Test 5: Authentication - invalid API key on row_count
        if not self.json_output:
            logger.info("\n--- Testing authentication (invalid API key) ---")
        success, _ = self.test_endpoint(
            "/api/v1/row_count",
            custom_api_key="INVALID_KEY_12345",
            expected_status_codes=[401],
            test_name="Row count with invalid API key (should return 401)",
        )
        all_passed = all_passed and success

        # Test 6: Authentication - missing API key on NYSE endpoint
        success, _ = self.test_endpoint(
            "/api/v1/unique_nyse_stock_count",
            use_api_key=False,
            expected_status_codes=[401],
            test_name="NYSE count without API key (should return 401)",
        )
        all_passed = all_passed and success

        # Test 7: Authentication - missing API key on NASDAQ endpoint
        success, _ = self.test_endpoint(
            "/api/v1/unique_nasdaq_stock_count",
            use_api_key=False,
            expected_status_codes=[401],
            test_name="NASDAQ count without API key (should return 401)",
        )
        all_passed = all_passed and success

        return all_passed

    def run_v2_tests(self) -> bool:
        """
        Run v2 API endpoint tests (Part 3).

        Tests:
        - /api/v2/{YEAR} for multiple valid years (2010, 2015, 2019, 2020)
        - /api/v2/{YEAR} for multiple invalid years (2009, 2021, 1980, 2025)
        - /api/v2/open/{SYMBOL} with valid symbol
        - /api/v2/close/{SYMBOL} with valid symbol
        - /api/v2/high/{SYMBOL} with valid symbol
        - /api/v2/low/{SYMBOL} with valid symbol
        - /api/v2/high_low/{SYMBOL} with valid symbol
        - Invalid symbol tests (404)
        - Authentication tests (401 for missing/invalid keys)

        Returns:
            True if all tests passed, False otherwise
        """
        # Set current API version
        self.current_api_version = "v2"

        # Set expected test count for v2
        self.test_results["expected_total"] += EXPECTED_TEST_COUNTS["v2"]

        if not self.json_output:
            logger.info("=" * 70)
            logger.info("RUNNING V2 API TESTS (Part 3)")
            logger.info("=" * 70)

        all_passed = True

        # Valid years to test (2010-2020)
        valid_years = [2010, 2015, 2019, 2020]  # Start, middle, recent, end
        # Invalid years to test
        invalid_years = [
            2009,
            2021,
            1980,
            2025,
        ]  # Before range, after range, far before, far after

        # Test symbols - try common ones that should exist in the data
        test_symbols = ["AAPL", "IBM", "MSFT"]  # Common stocks likely in data

        # Test 1-4: /api/v2/{YEAR} with multiple valid years
        if not self.json_output:
            logger.info("\n--- Testing /api/v2/{YEAR} with valid years ---")
        for year in valid_years:
            success, data = self.test_endpoint(
                f"/api/v2/{year}",
                schema=API_SCHEMAS["v2_year_count"],
                test_name=f"Year count for {year} with valid API key",
                endpoint_key=f"v2_year_{year}",
            )
            all_passed = all_passed and success

            # Verify year matches what was requested
            if success and data and data.get("year") != year:
                if not self.json_output:
                    logger.error(
                        f"✗ FAILED: Year mismatch for /api/v2/{year} - "
                        f"expected {year}, got {data.get('year')}"
                    )
                all_passed = False

        # Test 5-8: /api/v2/{YEAR} with multiple invalid years (should return 404)
        if not self.json_output:
            logger.info("\n--- Testing /api/v2/{YEAR} with invalid years ---")
        for year in invalid_years:
            success, _ = self.test_endpoint(
                f"/api/v2/{year}",
                expected_status_codes=[404],
                test_name=f"Year count for invalid year {year} (should return 404)",
            )
            all_passed = all_passed and success

        # Test 9-13: Price endpoints for valid symbols
        price_endpoints = [
            ("open", "v2_open_price_info", "Open prices"),
            ("close", "v2_close_price_info", "Close prices"),
            ("high", "v2_high_price_info", "High prices"),
            ("low", "v2_low_price_info", "Low prices"),
            ("high_low", "v2_high_low_price_info", "High-Low difference"),
        ]

        if not self.json_output:
            logger.info("\n--- Testing /api/v2/{TYPE}/{SYMBOL} endpoints ---")

        for price_type, schema_key, description in price_endpoints:
            # Try each test symbol until one works
            symbol_tested = None
            for symbol in test_symbols:
                if not self.json_output:
                    logger.info(f"  Testing /api/v2/{price_type}/{symbol}...")

                success, data = self.test_endpoint(
                    f"/api/v2/{price_type}/{symbol}",
                    schema=API_SCHEMAS[schema_key],
                    test_name=f"{description} for {symbol} with valid API key",
                    endpoint_key=f"v2_{price_type}_{symbol}",
                )

                if success:
                    symbol_tested = symbol
                    # Verify symbol matches and price_info is non-empty
                    if data:
                        if data.get("symbol") != symbol:
                            if not self.json_output:
                                logger.error(
                                    f"✗ FAILED: Symbol mismatch for /api/v2/{price_type}/{symbol} - "
                                    f"expected {symbol}, got {data.get('symbol')}"
                                )
                            all_passed = False
                        elif (
                            not data.get("price_info")
                            or len(data.get("price_info", [])) == 0
                        ):
                            if not self.json_output:
                                logger.warning(
                                    f"⚠ WARNING: Empty price_info for /api/v2/{price_type}/{symbol}"
                                )
                    break  # Found a working symbol, move to next endpoint type

            if symbol_tested:
                all_passed = all_passed and True
            else:
                # None of the test symbols worked - this is a failure
                if not self.json_output:
                    logger.error(
                        f"✗ FAILED: None of the test symbols ({test_symbols}) "
                        f"worked for /api/v2/{price_type}/ endpoint"
                    )
                all_passed = False

        # Test 14: Invalid symbol (should return 404)
        if not self.json_output:
            logger.info("\n--- Testing /api/v2/open/{SYMBOL} with invalid symbol ---")
        success, _ = self.test_endpoint(
            "/api/v2/open/INVALID_SYMBOL_XYZ123",
            expected_status_codes=[404],
            test_name="Open prices for invalid symbol (should return 404)",
        )
        all_passed = all_passed and success

        # Test 15: Authentication - missing API key on /api/v2/{YEAR}
        if not self.json_output:
            logger.info("\n--- Testing v2 authentication (missing API key) ---")
        success, _ = self.test_endpoint(
            f"/api/v2/{valid_years[0]}",
            use_api_key=False,
            expected_status_codes=[401],
            test_name="Year count without API key (should return 401)",
        )
        all_passed = all_passed and success

        # Test 16: Authentication - invalid API key on /api/v2/{YEAR}
        success, _ = self.test_endpoint(
            f"/api/v2/{valid_years[0]}",
            custom_api_key="INVALID_KEY_12345",
            expected_status_codes=[401],
            test_name="Year count with invalid API key (should return 401)",
        )
        all_passed = all_passed and success

        # Test 17: Authentication - missing API key on price endpoint
        # Use the first symbol that worked, or just use the first test symbol
        test_symbol = test_symbols[0]
        success, _ = self.test_endpoint(
            f"/api/v2/open/{test_symbol}",
            use_api_key=False,
            expected_status_codes=[401],
            test_name="Open prices without API key (should return 401)",
        )
        all_passed = all_passed and success

        # Test 18: Authentication - invalid API key on price endpoint
        success, _ = self.test_endpoint(
            f"/api/v2/open/{test_symbol}",
            custom_api_key="INVALID_KEY_12345",
            expected_status_codes=[401],
            test_name="Open prices with invalid API key (should return 401)",
        )
        all_passed = all_passed and success

        return all_passed

    def run_v3_tests(self) -> bool:
        """
        Run v3 API endpoint tests (Part 5).

        Tests account creation, stock holdings, and return calculations.
        This test suite creates test data and cleans up after itself.

        Returns:
            True if all tests passed, False otherwise
        """
        # Set current API version
        self.current_api_version = "v3"

        # Set expected test count for v3
        self.test_results["expected_total"] += EXPECTED_TEST_COUNTS["v3"]

        if not self.json_output:
            logger.info("=" * 70)
            logger.info("RUNNING V3 API TESTS (Part 5)")
            logger.info("=" * 70)

        all_passed = True

        # Store created account IDs for cleanup
        created_account_ids = []

        # Test 1: GET /api/v3/accounts - should return list (possibly empty)
        if not self.json_output:
            logger.info("\n--- Testing GET /api/v3/accounts (list accounts) ---")
        success, initial_accounts = self.test_endpoint(
            "/api/v3/accounts",
            schema=API_SCHEMAS["v3_accounts_list"],
            test_name="List all accounts (initial state)",
            endpoint_key="v3_accounts_initial",
        )
        all_passed = all_passed and success

        # Count initial accounts to avoid conflicts
        initial_account_count = len(initial_accounts) if initial_accounts else 0

        # Test 2-4: POST /api/v3/accounts - create test accounts
        if not self.json_output:
            logger.info("\n--- Testing POST /api/v3/accounts (create accounts) ---")

        test_account_names = ["TestAccount1", "TestAccount2", "TestAccount3"]
        for account_name in test_account_names:
            success, data = self.test_endpoint(
                "/api/v3/accounts",
                method="POST",
                json_data={"name": account_name},
                schema=API_SCHEMAS["v3_account_created"],
                expected_status_codes=[201],
                test_name=f"Create account '{account_name}'",
            )
            all_passed = all_passed and success
            if success and data:
                created_account_ids.append(data.get("account_id"))

        # Test 5: POST /api/v3/accounts - duplicate name (should return 409)
        if not self.json_output:
            logger.info("\n--- Testing POST /api/v3/accounts with duplicate name ---")
        success, _ = self.test_endpoint(
            "/api/v3/accounts",
            method="POST",
            json_data={"name": test_account_names[0]},
            expected_status_codes=[409],
            test_name=f"Create duplicate account '{test_account_names[0]}' (should return 409)",
        )
        all_passed = all_passed and success

        # Test 6: GET /api/v3/accounts - verify accounts were created
        if not self.json_output:
            logger.info("\n--- Testing GET /api/v3/accounts (verify creation) ---")
        success, accounts_list = self.test_endpoint(
            "/api/v3/accounts",
            schema=API_SCHEMAS["v3_accounts_list"],
            test_name="List all accounts (after creation)",
            endpoint_key="v3_accounts_after_creation",
        )
        all_passed = all_passed and success

        # Verify the accounts we created are in the list
        if success and accounts_list and created_account_ids:
            found_accounts = sum(
                1
                for acc in accounts_list
                if acc.get("account_id") in created_account_ids
            )
            if found_accounts != len(created_account_ids):
                if not self.json_output:
                    logger.error(
                        f"✗ FAILED: Expected {len(created_account_ids)} created accounts in list, "
                        f"found {found_accounts}"
                    )
                all_passed = False

        # Test 7-9: GET /api/v3/accounts/<id> - get account details (empty holdings initially)
        if not self.json_output:
            logger.info("\n--- Testing GET /api/v3/accounts/<id> (account details) ---")

        if created_account_ids:
            for i, account_id in enumerate(
                created_account_ids[:2]
            ):  # Test first 2 accounts
                success, account_details = self.test_endpoint(
                    f"/api/v3/accounts/{account_id}",
                    schema=API_SCHEMAS["v3_account_details"],
                    test_name=f"Get details for account {account_id}",
                    endpoint_key=f"v3_account_{account_id}_details",
                )
                all_passed = all_passed and success

                # Verify stock_holdings is initially empty
                if success and account_details:
                    if len(account_details.get("stock_holdings", [])) != 0:
                        if not self.json_output:
                            logger.warning(
                                f"⚠ WARNING: New account {account_id} has non-empty stock_holdings"
                            )

        # Test 10: GET /api/v3/accounts/<invalid_id> - should return 404
        if not self.json_output:
            logger.info("\n--- Testing GET /api/v3/accounts/<id> with invalid ID ---")
        success, _ = self.test_endpoint(
            "/api/v3/accounts/999999",
            expected_status_codes=[404],
            test_name="Get account with invalid ID (should return 404)",
        )
        all_passed = all_passed and success

        # Test 11-14: POST /api/v3/stocks - add stocks to accounts
        if not self.json_output:
            logger.info(
                "\n--- Testing POST /api/v3/stocks (add stocks to accounts) ---"
            )

        # Use common stocks that should exist and valid trading dates
        test_stocks = [
            {
                "account_id": created_account_ids[0] if created_account_ids else 1,
                "symbol": "AAPL",
                "purchase_date": "2015-01-05",
                "sale_date": "2015-12-31",
                "number_of_shares": 100,
            },
            {
                "account_id": created_account_ids[0] if created_account_ids else 1,
                "symbol": "MSFT",
                "purchase_date": "2016-06-01",
                "sale_date": "2016-12-30",
                "number_of_shares": 50,
            },
            {
                "account_id": created_account_ids[1]
                if len(created_account_ids) > 1
                else 1,
                "symbol": "IBM",
                "purchase_date": "2017-03-15",
                "sale_date": "2017-09-29",
                "number_of_shares": 75,
            },
        ]

        for stock in test_stocks:
            success, _ = self.test_endpoint(
                "/api/v3/stocks",
                method="POST",
                json_data=stock,
                expected_status_codes=[201],
                test_name=f"Add {stock['number_of_shares']} shares of {stock['symbol']} to account {stock['account_id']}",
            )
            all_passed = all_passed and success

        # Test 15: POST /api/v3/stocks with invalid date (should return 400)
        if not self.json_output:
            logger.info("\n--- Testing POST /api/v3/stocks with invalid date ---")
        success, _ = self.test_endpoint(
            "/api/v3/stocks",
            method="POST",
            json_data={
                "account_id": created_account_ids[0] if created_account_ids else 1,
                "symbol": "AAPL",
                "purchase_date": "2015-12-19",  # Not a trading day (Saturday)
                "sale_date": "2015-12-31",
                "number_of_shares": 10,
            },
            expected_status_codes=[400],
            test_name="Add stock with invalid purchase date (should return 400)",
        )
        all_passed = all_passed and success

        # Test 16: GET /api/v3/accounts/<id> - verify stocks were added
        if not self.json_output:
            logger.info(
                "\n--- Testing GET /api/v3/accounts/<id> (verify stocks added) ---"
            )

        if created_account_ids:
            success, account_with_stocks = self.test_endpoint(
                f"/api/v3/accounts/{created_account_ids[0]}",
                schema=API_SCHEMAS["v3_account_details"],
                test_name=f"Get details for account {created_account_ids[0]} (with stocks)",
                endpoint_key=f"v3_account_{created_account_ids[0]}_with_stocks",
            )
            all_passed = all_passed and success

            # Verify stock_holdings is not empty
            if success and account_with_stocks:
                holdings_count = len(account_with_stocks.get("stock_holdings", []))
                if holdings_count < 2:  # We added 2 stocks to first account
                    if not self.json_output:
                        logger.error(
                            f"✗ FAILED: Expected at least 2 stock holdings for account {created_account_ids[0]}, "
                            f"found {holdings_count}"
                        )
                    all_passed = False

        # Test 17-18: GET /api/v3/stocks/<symbol> - get stock holdings across accounts
        if not self.json_output:
            logger.info(
                "\n--- Testing GET /api/v3/stocks/<symbol> (stock holdings) ---"
            )

        for symbol in ["AAPL", "MSFT"]:
            success, stock_holdings = self.test_endpoint(
                f"/api/v3/stocks/{symbol}",
                schema=API_SCHEMAS["v3_stock_holdings"],
                test_name=f"Get holdings for {symbol}",
                endpoint_key=f"v3_stock_holdings_{symbol}",
            )
            all_passed = all_passed and success

            # Verify symbol matches
            if success and stock_holdings:
                if stock_holdings.get("symbol") != symbol:
                    if not self.json_output:
                        logger.error(
                            f"✗ FAILED: Symbol mismatch for /api/v3/stocks/{symbol} - "
                            f"expected {symbol}, got {stock_holdings.get('symbol')}"
                        )
                    all_passed = False

        # Test 19: GET /api/v3/stocks/<symbol> with symbol that has no holdings
        success, empty_holdings = self.test_endpoint(
            "/api/v3/stocks/INVALIDSTOCKSYMBOLXYZ",
            schema=API_SCHEMAS["v3_stock_holdings"],
            test_name="Get holdings for stock with no holdings",
        )
        all_passed = all_passed and success
        if success and empty_holdings:
            if len(empty_holdings.get("holdings", [])) != 0:
                if not self.json_output:
                    logger.warning(
                        "⚠ WARNING: Expected empty holdings list for non-existent stock symbol"
                    )

        # Test 20-21: GET /api/v3/accounts/return/<id> - calculate return
        if not self.json_output:
            logger.info(
                "\n--- Testing GET /api/v3/accounts/return/<id> (calculate return) ---"
            )

        if created_account_ids:
            for idx, account_id in enumerate(
                created_account_ids[:2]
            ):  # Test first 2 accounts
                success, return_data = self.test_endpoint(
                    f"/api/v3/accounts/return/{account_id}",
                    schema=API_SCHEMAS["v3_account_return"],
                    test_name=f"Calculate return for account {account_id}",
                    endpoint_key=f"v3_account_{account_id}_return",
                )
                all_passed = all_passed and success

                # Verify account_id matches
                if success and return_data:
                    if return_data.get("account_id") != account_id:
                        if not self.json_output:
                            logger.error(
                                f"✗ FAILED: Account ID mismatch for return calculation - "
                                f"expected {account_id}, got {return_data.get('account_id')}"
                            )
                        all_passed = False

                    # Calculate expected return and compare
                    reported_return = return_data.get("return")

                    # Get the holdings for this account
                    account_holdings = []
                    if idx == 0:
                        # First account has AAPL and MSFT
                        account_holdings = [
                            stock
                            for stock in test_stocks
                            if stock["account_id"] == account_id
                        ]
                    elif idx == 1 and len(created_account_ids) > 1:
                        # Second account has IBM
                        account_holdings = [
                            stock
                            for stock in test_stocks
                            if stock["account_id"] == account_id
                        ]

                    if account_holdings:
                        expected_return = self.calculate_expected_return(
                            account_holdings
                        )

                        # Store for reporting
                        self.return_calculations[account_id] = {
                            "reported": reported_return,
                            "expected": expected_return,
                            "holdings": account_holdings,
                        }

                        if expected_return is not None:
                            # Allow for small floating point differences (0.01 tolerance)
                            if abs(reported_return - expected_return) > 0.01:
                                if not self.json_output:
                                    logger.warning(
                                        f"⚠ WARNING: Return calculation mismatch for account {account_id}:\n"
                                        f"  Reported: ${reported_return:.2f}\n"
                                        f"  Expected: ${expected_return:.2f}\n"
                                        f"  Difference: ${abs(reported_return - expected_return):.2f}"
                                    )
                            else:
                                if not self.json_output:
                                    logger.info(
                                        f"✓ Return calculation correct: ${reported_return:.2f}"
                                    )
                        else:
                            if not self.json_output:
                                logger.warning(
                                    f"⚠ Could not calculate expected return (data unavailable)\n"
                                    f"  Reported return: ${reported_return:.2f}"
                                )

        # Test 22: GET /api/v3/accounts/return/<invalid_id> - should return 404
        if not self.json_output:
            logger.info(
                "\n--- Testing GET /api/v3/accounts/return/<id> with invalid ID ---"
            )
        success, _ = self.test_endpoint(
            "/api/v3/accounts/return/999999",
            expected_status_codes=[404],
            test_name="Calculate return for invalid account ID (should return 404)",
        )
        all_passed = all_passed and success

        # Test 23-24: DELETE /api/v3/stocks - remove stocks from accounts
        if not self.json_output:
            logger.info("\n--- Testing DELETE /api/v3/stocks (remove stocks) ---")

        # Delete one of the stocks we added
        if test_stocks:
            stock_to_delete = test_stocks[0]
            success, _ = self.test_endpoint(
                "/api/v3/stocks",
                method="DELETE",
                json_data=stock_to_delete,
                expected_status_codes=[204],
                test_name=f"Remove {stock_to_delete['number_of_shares']} shares of {stock_to_delete['symbol']} from account {stock_to_delete['account_id']}",
            )
            all_passed = all_passed and success

        # Test 25: DELETE /api/v3/stocks with non-matching data (should return 404)
        success, _ = self.test_endpoint(
            "/api/v3/stocks",
            method="DELETE",
            json_data={
                "account_id": created_account_ids[0] if created_account_ids else 1,
                "symbol": "AAPL",
                "purchase_date": "2015-01-05",
                "sale_date": "2099-12-31",  # Wrong date
                "number_of_shares": 100,
            },
            expected_status_codes=[404],
            test_name="Remove stock with non-matching data (should return 404)",
        )
        all_passed = all_passed and success

        # Test 26-27: DELETE /api/v3/accounts - delete accounts
        if not self.json_output:
            logger.info("\n--- Testing DELETE /api/v3/accounts (delete accounts) ---")

        if created_account_ids:
            for account_id in created_account_ids:
                success, _ = self.test_endpoint(
                    "/api/v3/accounts",
                    method="DELETE",
                    json_data={"account_id": account_id},
                    expected_status_codes=[204],
                    test_name=f"Delete account {account_id}",
                )
                all_passed = all_passed and success

        # Test 28: DELETE /api/v3/accounts with non-existent ID (should return 404)
        success, _ = self.test_endpoint(
            "/api/v3/accounts",
            method="DELETE",
            json_data={"account_id": 999999},
            expected_status_codes=[404],
            test_name="Delete non-existent account (should return 404)",
        )
        all_passed = all_passed and success

        # Test 29: GET /api/v3/accounts - verify accounts were deleted
        if not self.json_output:
            logger.info("\n--- Testing GET /api/v3/accounts (verify deletion) ---")
        success, final_accounts = self.test_endpoint(
            "/api/v3/accounts",
            schema=API_SCHEMAS["v3_accounts_list"],
            test_name="List all accounts (after deletion)",
            endpoint_key="v3_accounts_final",
        )
        all_passed = all_passed and success

        # Verify deleted accounts are not in the list
        if success and final_accounts and created_account_ids:
            found_deleted = sum(
                1
                for acc in final_accounts
                if acc.get("account_id") in created_account_ids
            )
            if found_deleted > 0:
                if not self.json_output:
                    logger.error(
                        f"✗ FAILED: Found {found_deleted} deleted account(s) still in the list"
                    )
                all_passed = False

        # Test 30-33: Authentication tests
        if not self.json_output:
            logger.info("\n--- Testing v3 authentication ---")

        # Test without API key
        success, _ = self.test_endpoint(
            "/api/v3/accounts",
            use_api_key=False,
            expected_status_codes=[401],
            test_name="List accounts without API key (should return 401)",
        )
        all_passed = all_passed and success

        # Test with invalid API key
        success, _ = self.test_endpoint(
            "/api/v3/accounts",
            custom_api_key="INVALID_KEY_12345",
            expected_status_codes=[401],
            test_name="List accounts with invalid API key (should return 401)",
        )
        all_passed = all_passed and success

        # Test POST without API key
        success, _ = self.test_endpoint(
            "/api/v3/accounts",
            method="POST",
            json_data={"name": "TestAccount"},
            use_api_key=False,
            expected_status_codes=[401],
            test_name="Create account without API key (should return 401)",
        )
        all_passed = all_passed and success

        # Test stocks endpoint without API key
        success, _ = self.test_endpoint(
            "/api/v3/stocks/AAPL",
            use_api_key=False,
            expected_status_codes=[401],
            test_name="Get stock holdings without API key (should return 401)",
        )
        all_passed = all_passed and success

        return all_passed

    def run_tests(self, apis_to_test: list[str]) -> bool:
        """
        Run selected API tests.

        Args:
            apis_to_test: List of API versions to test (e.g., ['v1', 'v2'])

        Returns:
            True if all tests passed, False otherwise
        """
        if not self.json_output:
            logger.info(f"Testing APIs: {', '.join(apis_to_test)}")
            logger.info(f"Base URL: {self.base_url}")
            logger.info(f"API Key: {'Set' if self.api_key else 'Not Set'}\n")

        all_passed = True

        if "v1" in apis_to_test:
            all_passed = self.run_v1_tests() and all_passed

        if "v2" in apis_to_test:
            all_passed = self.run_v2_tests() and all_passed

        if "v3" in apis_to_test:
            all_passed = self.run_v3_tests() and all_passed

        # Print summary
        self.print_summary()

        return all_passed

    def print_summary(self) -> None:
        """Print a summary of test results."""
        global _header_issues_detected

        total = self.test_results["total"]
        passed = self.test_results["passed"]
        failed = self.test_results["failed"]
        expected_total = self.test_results["expected_total"]

        if self.json_output:
            # Output JSON format for parsing by other scripts
            import json

            result = {
                "total_tests": expected_total,  # Use expected total for consistency
                "tests_run": total,  # How many actually ran
                "passed": passed,
                "failed": failed,
                "skipped": expected_total - total,  # Tests that didn't run
                "all_passed": failed == 0 and total == expected_total,
                "header_issues": _header_issues_detected,
                "endpoint_data": self.endpoint_data,
                "results_by_version": self.results_by_version,
                "return_calculations": self.return_calculations,
            }
            print(json.dumps(result, indent=2))
            return

        logger.info("\n" + "=" * 70)
        logger.info("TEST SUMMARY")
        logger.info("=" * 70)

        # Show results by API version
        logger.info("\nResults by API Version:")
        for version in ["v1", "v2", "v3"]:
            version_results = self.results_by_version[version]
            if version_results["total"] > 0:
                expected = EXPECTED_TEST_COUNTS[version]
                logger.info(
                    f"  {version.upper()}: {version_results['passed']}/{expected} passed "
                    f"({version_results['failed']} failed)"
                )

        # Show return calculation results if we have them
        if self.return_calculations:
            logger.info("\nReturn Calculation Results:")
            for account_id, calc_data in self.return_calculations.items():
                reported = calc_data["reported"]
                expected = calc_data["expected"]
                holdings = calc_data["holdings"]

                logger.info(f"\n  Account {account_id}:")
                logger.info(f"    Holdings:")
                for holding in holdings:
                    logger.info(
                        f"      - {holding['symbol']}: {holding['number_of_shares']} shares, "
                        f"{holding['purchase_date']} → {holding['sale_date']}"
                    )
                logger.info(f"    Reported return: ${reported:.2f}")
                if expected is not None:
                    logger.info(f"    Expected return: ${expected:.2f}")
                    diff = abs(reported - expected)
                    if diff > 0.01:
                        logger.info(f"    ⚠ Difference: ${diff:.2f}")
                    else:
                        logger.info(f"    ✓ Correct!")
                else:
                    logger.info(f"    Expected return: Could not calculate")

        logger.info(f"\nOverall:")
        logger.info(f"  Expected tests: {expected_total}")
        logger.info(f"  Tests run: {total}")
        logger.info(f"  Passed: {passed}")
        logger.info(f"  Failed: {failed}")

        skipped = expected_total - total
        if skipped > 0:
            logger.info(f"  Skipped: {skipped} (due to early failures)")

        # Report header issues if detected
        if _header_issues_detected:
            logger.info("\n⚠ CODE QUALITY ISSUE:")
            logger.info(
                "  HTTP response headers are malformed (likely 'Content Type' instead of 'Content-Type')"
            )
            logger.info(
                "  This violates HTTP standards but responses were processed successfully"
            )

        if failed == 0 and total == expected_total:
            logger.info("\n✓ ALL TESTS PASSED!")
        elif total == 0:
            logger.info("\nNo tests were run")
        else:
            logger.warning(f"\n✗ {failed} TEST(S) FAILED")
            if skipped > 0:
                logger.warning(f"  ({skipped} test(s) skipped due to early failures)")


def main():
    """Main entry point for the autograder."""
    parser = argparse.ArgumentParser(
        description="Flask API Autograder - Test Flask endpoints",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test v1 endpoints (Part 2)
  python flask_autograder.py --api v1

  # Test multiple API versions
  python flask_autograder.py --api v1 --api v2

  # Use custom URL and API key
  python flask_autograder.py --api v1 --url http://localhost:5000 --key my_key

  # Enable debug logging
  python flask_autograder.py --api v1 --debug
        """,
    )

    parser.add_argument(
        "--url",
        default="http://localhost:4000",
        help="Base URL for the Flask application (default: http://localhost:4000)",
    )

    parser.add_argument(
        "--key",
        default=None,
        help="API key for authentication (default: read from DATA_241_API_KEY env var)",
    )

    parser.add_argument(
        "--api",
        action="append",
        choices=["v1", "v2", "v3"],
        help="Specify which API version to test (can be used multiple times). "
        "Default: v1",
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

    args = parser.parse_args()

    # Configure logging level
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)

    # If JSON output is requested, suppress all logging
    if args.json:
        logging.getLogger().setLevel(logging.CRITICAL)

    # Get API key
    api_key = args.key or os.environ.get("DATA_241_API_KEY")

    if not api_key:
        logger.error(
            "Error: API key not provided. Set DATA_241_API_KEY environment "
            "variable or use --key option"
        )
        sys.exit(1)

    # Determine which APIs to test
    test_apis = args.api if args.api else ["v1"]

    # Create tester and run tests
    tester = FlaskAPITester(base_url=args.url, api_key=api_key, json_output=args.json)

    try:
        all_passed = tester.run_tests(test_apis)

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
