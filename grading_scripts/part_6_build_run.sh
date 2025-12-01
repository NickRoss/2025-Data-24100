#!/bin/bash

# Part 6 Build and Run Script
# Consolidated script for database, Flask, pytest tests, and autodocs testing

# Parse command line arguments
SINGLE_GROUP=""
DB_ONLY=false
FLASK_ONLY=false
TESTS_ONLY=false
AUTODOCS_ONLY=false

print_help() {
    echo "Usage: $0 [-g GROUP_NUMBER] [--db-only | --flask-only | --tests-only | --autodocs-only]"
    echo ""
    echo "Options:"
    echo "  -g GROUP_NUMBER       Test only a specific group (e.g., -g 1 for Group-1)"
    echo "  --db-only             Run only database tests"
    echo "  --flask-only          Run only Flask API tests"
    echo "  --tests-only          Run only student pytest tests"
    echo "  --autodocs-only       Run only autodocs tests"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run all tests for all groups"
    echo "  $0 -g 6               # Run all tests for Group-6 only"
    echo "  $0 --db-only          # Run only DB tests for all groups"
    echo "  $0 -g 6 --flask-only  # Run only Flask tests for Group-6"
    exit 0
}

while [[ $# -gt 0 ]]; do
    case $1 in
        -g|--group)
            SINGLE_GROUP="$2"
            shift 2
            ;;
        --db-only)
            DB_ONLY=true
            shift
            ;;
        --flask-only)
            FLASK_ONLY=true
            shift
            ;;
        --tests-only)
            TESTS_ONLY=true
            shift
            ;;
        --autodocs-only)
            AUTODOCS_ONLY=true
            shift
            ;;
        -h|--help)
            print_help
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Check for conflicting options
exclusive_count=0
[ "$DB_ONLY" = true ] && exclusive_count=$((exclusive_count + 1))
[ "$FLASK_ONLY" = true ] && exclusive_count=$((exclusive_count + 1))
[ "$TESTS_ONLY" = true ] && exclusive_count=$((exclusive_count + 1))
[ "$AUTODOCS_ONLY" = true ] && exclusive_count=$((exclusive_count + 1))

if [ $exclusive_count -gt 1 ]; then
    echo "Error: Can only specify one of --db-only, --flask-only, --tests-only, or --autodocs-only"
    exit 1
fi

# Configuration
API_KEY="${DATA_241_API_KEY:-test_grading_key_2024}"
RAW_DATA_DIR="/Users/nickross/data_grading/project_data"
FLASK_PORT=4000
AUTODOCS_PORT=4040

export DATA_241_API_KEY="$API_KEY"
export RAW_DATA_DIR="$RAW_DATA_DIR"

# Find all group directories
GROUP_DIRS=()
if [ -n "$SINGLE_GROUP" ]; then
    group_dir="2025-Data-24100-Group-${SINGLE_GROUP}"
    if [ -d "$group_dir" ]; then
        GROUP_DIRS=("$group_dir")
    else
        echo "✗ ERROR: Group directory $group_dir not found"
        exit 1
    fi
else
    for dir in 2025-Data-24100-Group-*; do
        if [ -d "$dir" ]; then
            GROUP_DIRS+=("$dir")
        fi
    done
fi

if [ ${#GROUP_DIRS[@]} -eq 0 ]; then
    echo "✗ ERROR: No group directories found"
    exit 1
fi

# ============================================================================
# PRE-CHECK: DATABASE NOT COMMITTED
# ============================================================================

check_db_not_committed() {
    local group=$1
    # local output_file="part_6_${group}_precheck_output.txt"

    cd "$group" || return 1

    # echo "Checking if database is committed to git..." > "../$output_file"

    # Check if it's a git repo
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        echo "⚠ WARNING: Not a git repository"
        cd ..
        return 0
    fi

    # Check for committed .db files
    local committed_files=$(git ls-files "*.db" 2>/dev/null)

    if [ -n "$committed_files" ]; then
        echo "✗ FAIL: Database files are committed to git:"
        echo "$committed_files"
        cd ..
        return 1
    else
        echo "✓ PASS: No database files committed to git"
        cd ..
        return 0
    fi
}

run_precheck_all() {
    echo "======================================================================"
    echo "PRE-CHECK: DATABASE NOT COMMITTED TO REPOSITORY"
    echo "======================================================================"
    echo "Verifying that database files are not committed to git"
    echo ""

    local failed=0

    for group in "${GROUP_DIRS[@]}"; do
        echo "Checking $group..."
        if ! check_db_not_committed "$group"; then
            failed=$((failed + 1))
        fi
    done

    echo ""
    echo "======================================================================"
    echo "PRE-CHECK COMPLETE"
    echo "======================================================================"

    if [ $failed -eq 0 ]; then
        echo "✓ All groups passed pre-check"
    else
        echo "⚠ $failed group(s) have database files committed"
    fi

    echo ""
    return $failed
}

# ============================================================================
# DATABASE TESTING FUNCTIONS
# ============================================================================

run_db_test_single() {
    local group=$1
    local output_file="part_6_${group}_db_output.txt"

    echo "======================================================================"
    echo "DATABASE TESTING: $group"
    echo "======================================================================"

    cd "$group" || return 1
    python3 ../db_commands_tester.py --repo-dir . --keep-loaded 2>&1 | tee "../$output_file"
    local exit_code=$?
    cd ..

    return $exit_code
}

run_db_tests_parallel() {
    echo "======================================================================"
    echo "PHASE 1: PARALLEL DATABASE TESTING"
    echo "======================================================================"
    echo "This will create and load databases for all groups in parallel"
    echo "Using API key: $API_KEY"
    echo "Using RAW_DATA_DIR: $RAW_DATA_DIR"
    echo ""

    echo "Found ${#GROUP_DIRS[@]} groups to test:"
    for group in "${GROUP_DIRS[@]}"; do
        echo "  - $group"
    done
    echo ""

    # Track start time
    local start_time=$(date +%s)

    # Run all groups in parallel
    echo "Starting parallel database testing..."
    echo ""

    local pids=()
    for group in "${GROUP_DIRS[@]}"; do
        local output_file="part_6_${group}_db_output.txt"

        (
            cd "$group" || exit 1
            echo "[$(date '+%H:%M:%S')] Starting DB tests for $group..." | tee "../$output_file"
            python3 ../db_commands_tester.py --repo-dir . --keep-loaded 2>&1 | tee -a "../$output_file"
            exit_code=$?
            echo "[$(date '+%H:%M:%S')] DB tests for $group completed with exit code: $exit_code" | tee -a "../$output_file"
            exit $exit_code
        ) &

        pids+=($!)
    done

    # Wait for all background jobs
    echo "Waiting for all database tests to complete..."
    local failed=0
    for pid in "${pids[@]}"; do
        if ! wait $pid; then
            failed=$((failed + 1))
        fi
    done

    # Calculate elapsed time
    local end_time=$(date +%s)
    local elapsed=$((end_time - start_time))
    local minutes=$((elapsed / 60))
    local seconds=$((elapsed % 60))

    echo ""
    echo "======================================================================"
    echo "PHASE 1 COMPLETE"
    echo "======================================================================"
    echo "Total time: ${minutes}m ${seconds}s"
    echo ""

    if [ $failed -eq 0 ]; then
        echo "✓ All database tests passed!"
    else
        echo "✗ $failed group(s) had database test failures"
    fi

    # Generate summary table
    echo ""
    echo "======================================================================"
    echo "DATABASE TEST SUMMARY"
    echo "======================================================================"
    echo ""

    printf "%-35s | %-12s | %-15s | %-s\n" "Group" "Status" "db_load Time" "Issues"
    printf "%-35s-+-%-12s-+-%-15s-+-%-s\n" "-----------------------------------" "------------" "---------------" "-------------------"

    for group in "${GROUP_DIRS[@]}"; do
        local output_file="part_6_${group}_db_output.txt"

        if [ ! -f "$output_file" ]; then
            printf "%-35s | %-12s | %-15s | %s\n" "$group" "❓ No log" "N/A" "Log file not found"
            continue
        fi

        # Check if tests passed
        local status
        if grep -q "✓ ALL DATABASE TESTS PASSED" "$output_file"; then
            status="✓ PASS"
        elif grep -q "✗.*DATABASE TEST.* FAILED" "$output_file"; then
            status="✗ FAIL"
        elif grep -q "make:.*Error" "$output_file"; then
            status="✗ FAIL"
        else
            status="❓ UNKNOWN"
        fi

        # Extract timing
        local timing=$(grep -o "db_load completed in [0-9.]*" "$output_file" | head -1 | grep -o "[0-9.]*" || echo "N/A")
        if [ "$timing" != "N/A" ]; then
            timing="${timing}s"
        fi

        # Extract issues/errors
        local issues=""
        if grep -q "Error" "$output_file" || grep -q "ERROR" "$output_file"; then
            local error_count=$(grep -c -i "error" "$output_file" || echo "0")
            issues="$error_count error(s)"
        fi

        if grep -q "Traceback" "$output_file"; then
            if [ -n "$issues" ]; then
                issues="$issues, Exception"
            else
                issues="Exception"
            fi
        fi

        if [ -z "$issues" ]; then
            issues="-"
        fi

        printf "%-35s | %-12s | %-15s | %s\n" "$group" "$status" "$timing" "$issues"
    done

    echo ""
    echo "Individual DB test logs:"
    for group in "${GROUP_DIRS[@]}"; do
        local output_file="part_6_${group}_db_output.txt"
        if [ -f "$output_file" ]; then
            echo "  - $output_file"
        fi
    done

    echo ""
    echo "Databases are now loaded and ready for Flask testing."

    return $failed
}

# ============================================================================
# FLASK TESTING FUNCTIONS
# ============================================================================

wait_for_flask() {
    local max_wait=60
    local wait_count=0

    while ! curl -s http://localhost:${FLASK_PORT}/api/v2/2019 >/dev/null 2>&1; do
        sleep 1
        wait_count=$((wait_count + 1))
        if [ $wait_count -ge $max_wait ]; then
            echo "Flask server did not start within $max_wait seconds"
            return 1
        fi
        if [ $((wait_count % 10)) -eq 0 ]; then
            echo "  Still waiting... ($wait_count seconds elapsed)"
        fi
    done
    return 0
}

stop_containers() {
    docker ps -q | xargs -r docker stop >/dev/null 2>&1
}

run_flask_test_single() {
    local group=$1
    local output_file="part_6_${group}_flask_output.txt"

    echo "======================================================================"
    echo "FLASK API TESTING: $group"
    echo "======================================================================"

    cd "$group" || return 1

    # Clean accounts table before testing V3 APIs
    echo "Cleaning accounts table for $group..."
    if make db_clean_account > /dev/null 2>&1; then
        echo "✓ Accounts table cleaned"
    else
        echo "⚠ Warning: db_clean_account failed (might not be implemented)"
    fi

    # Start Flask server
    echo "Starting Flask server for $group..."
    PYTHONUNBUFFERED=1 make flask < /dev/null > flask_output.log 2>&1 &
    local FLASK_PID=$!

    # Give Docker time to start
    sleep 3

    # Check if the process is still running
    if ! kill -0 $FLASK_PID 2>/dev/null; then
        echo "⚠ Warning: make flask process died quickly. Checking for running containers..."
        if docker ps --format '{{.Names}}' | grep -q "data241"; then
            echo "✓ Found running Docker container"
        else
            echo "✗ No container found running"
            cat flask_output.log
            cd ..
            return 1
        fi
    fi

    # Wait for Flask to be ready
    echo "Waiting for Flask to be ready..."
    if wait_for_flask; then
        echo "✓ Flask server is ready"

        # Run the autograder
        echo ""
        echo "--- Running Flask API tests for $group ---"

        python3 ../flask_autograder.py \
            --api v1 \
            --api v2 \
            --api v3 \
            --key "$API_KEY" \
            --url "http://localhost:${FLASK_PORT}" > "../$output_file" 2>&1

        local exit_code=$?

        if [ $exit_code -eq 0 ]; then
            echo "✓ All Flask API tests passed for $group"
        else
            echo "✗ Some Flask API tests failed for $group"
        fi
    else
        echo "✗ Flask server failed to start for $group"
        exit_code=1
    fi

    # Stop Flask server
    echo "Stopping Flask server..."
    if [ ! -z "$FLASK_PID" ]; then
        kill $FLASK_PID 2>/dev/null
        wait $FLASK_PID 2>/dev/null
    fi

    stop_containers
    rm -f flask_output.log

    cd ..
    return $exit_code
}

run_flask_tests_sequential() {
    echo "======================================================================"
    echo "PHASE 2: SEQUENTIAL FLASK TESTING"
    echo "======================================================================"
    echo "Testing Flask APIs for all groups sequentially"
    echo "Using API key: $API_KEY"
    echo ""

    local start_time=$(date +%s)
    local total_failed=0

    for group in "${GROUP_DIRS[@]}"; do
        if ! run_flask_test_single "$group"; then
            total_failed=$((total_failed + 1))
        fi
        echo ""
    done

    # Calculate elapsed time
    local end_time=$(date +%s)
    local elapsed=$((end_time - start_time))
    local minutes=$((elapsed / 60))
    local seconds=$((elapsed % 60))

    echo "======================================================================"
    echo "PHASE 2 COMPLETE"
    echo "======================================================================"
    echo "Total time: ${minutes}m ${seconds}s"
    echo ""

    if [ $total_failed -eq 0 ]; then
        echo "✓ All Flask tests passed!"
    else
        echo "✗ $total_failed group(s) had Flask test failures"
    fi

    # Generate summary table
    echo ""
    echo "======================================================================"
    echo "FLASK TEST SUMMARY"
    echo "======================================================================"
    echo ""

    printf "%-35s | %-12s | %-10s | %-10s | %-10s | %-s\n" "Group" "Status" "V1 Tests" "V2 Tests" "V3 Tests" "Total"
    printf "%-35s-+-%-12s-+-%-10s-+-%-10s-+-%-10s-+-%-s\n" "-----------------------------------" "------------" "----------" "----------" "----------" "----------"

    for group in "${GROUP_DIRS[@]}"; do
        local output_file="part_6_${group}_flask_output.txt"

        if [ ! -f "$output_file" ]; then
            printf "%-35s | %-12s | %-10s | %-10s | %-10s | %s\n" "$group" "❓ No log" "N/A" "N/A" "N/A" "N/A"
            continue
        fi

        # Extract test results using regex
        local v1_passed=$(grep "V1:" "$output_file" | grep -o "[0-9]\+/[0-9]\+ passed" | grep -o "^[0-9]\+" || echo "0")
        local v1_total=$(grep "V1:" "$output_file" | grep -o "[0-9]\+/[0-9]\+ passed" | grep -o "/[0-9]\+" | tr -d '/' || echo "0")
        local v2_passed=$(grep "V2:" "$output_file" | grep -o "[0-9]\+/[0-9]\+ passed" | grep -o "^[0-9]\+" || echo "0")
        local v2_total=$(grep "V2:" "$output_file" | grep -o "[0-9]\+/[0-9]\+ passed" | grep -o "/[0-9]\+" | tr -d '/' || echo "0")
        local v3_passed=$(grep "V3:" "$output_file" | grep -o "[0-9]\+/[0-9]\+ passed" | grep -o "^[0-9]\+" || echo "0")
        local v3_total=$(grep "V3:" "$output_file" | grep -o "[0-9]\+/[0-9]\+ passed" | grep -o "/[0-9]\+" | tr -d '/' || echo "0")

        local total_passed=$(grep "Passed:" "$output_file" | tail -1 | grep -o "[0-9]\+" || echo "0")
        local total_tests=$(grep "Tests run:" "$output_file" | tail -1 | grep -o "[0-9]\+" || echo "0")

        # Determine status
        local status
        if grep -q "✓ All Flask API tests passed" "$output_file"; then
            status="✓ PASS"
        elif [ "$total_passed" -eq "$total_tests" ] && [ "$total_tests" -gt 0 ]; then
            status="✓ PASS"
        else
            status="✗ FAIL"
        fi

        printf "%-35s | %-12s | %-10s | %-10s | %-10s | %s\n" \
            "$group" "$status" "$v1_passed/$v1_total" "$v2_passed/$v2_total" "$v3_passed/$v3_total" "$total_passed/$total_tests"
    done

    echo ""
    echo "Individual Flask test logs:"
    for group in "${GROUP_DIRS[@]}"; do
        local output_file="part_6_${group}_flask_output.txt"
        if [ -f "$output_file" ]; then
            echo "  - $output_file"
        fi
    done

    return $total_failed
}

# ============================================================================
# STUDENT PYTEST TESTS
# ============================================================================

run_pytest_test_single() {
    local group=$1
    local output_file="part_6_${group}_pytest_output.txt"

    echo "======================================================================"
    echo "STUDENT PYTEST TESTING: $group"
    echo "======================================================================"

    cd "$group" || return 1

    # Check if tests directory/file exists
    if [ ! -d "test" ] && [ ! -d "tests" ] && [ ! -f "test.py" ]; then
        echo "⚠ WARNING: No test directory or file found" | tee "../$output_file"
        cd ..
        return 1
    fi

    # Run the student's tests
    echo "Running pytest for $group..."
    if make tests > "../$output_file" 2>&1; then
        echo "✓ Pytest tests passed for $group"
        local exit_code=0
    else
        echo "✗ Pytest tests failed for $group"
        local exit_code=1
    fi

    cd ..
    return $exit_code
}

run_pytest_tests_sequential() {
    echo "======================================================================"
    echo "PHASE 3: SEQUENTIAL STUDENT PYTEST TESTING"
    echo "======================================================================"
    echo "Running student pytest tests for all groups sequentially"
    echo ""

    local start_time=$(date +%s)
    local total_failed=0

    for group in "${GROUP_DIRS[@]}"; do
        if ! run_pytest_test_single "$group"; then
            total_failed=$((total_failed + 1))
        fi
        echo ""
    done

    # Calculate elapsed time
    local end_time=$(date +%s)
    local elapsed=$((end_time - start_time))
    local minutes=$((elapsed / 60))
    local seconds=$((elapsed % 60))

    echo "======================================================================"
    echo "PHASE 3 COMPLETE"
    echo "======================================================================"
    echo "Total time: ${minutes}m ${seconds}s"
    echo ""

    if [ $total_failed -eq 0 ]; then
        echo "✓ All student pytest tests passed!"
    else
        echo "✗ $total_failed group(s) had pytest test failures"
    fi

    # Generate summary table
    echo ""
    echo "======================================================================"
    echo "STUDENT PYTEST TEST SUMMARY"
    echo "======================================================================"
    echo ""

    printf "%-35s | %-12s | %-15s | %-15s | %-s\n" "Group" "Status" "Tests Passed" "Coverage %" "Issues"
    printf "%-35s-+-%-12s-+-%-15s-+-%-15s-+-%-s\n" "-----------------------------------" "------------" "---------------" "---------------" "-------------------"

    for group in "${GROUP_DIRS[@]}"; do
        local output_file="part_6_${group}_pytest_output.txt"

        if [ ! -f "$output_file" ]; then
            printf "%-35s | %-12s | %-15s | %-15s | %s\n" "$group" "❓ No log" "N/A" "N/A" "Log file not found"
            continue
        fi

        # Check if tests passed
        local status
        if grep -q "failed\|FAILED\|ERROR" "$output_file"; then
            status="✗ FAIL"
        elif grep -q "passed\|PASSED" "$output_file"; then
            status="✓ PASS"
        else
            status="❓ UNKNOWN"
        fi

        # Extract test counts
        local test_info=$(grep -E "[0-9]+ passed" "$output_file" | tail -1 | grep -o "[0-9]\+ passed" || echo "N/A")

        # Extract coverage percentage
        local coverage=$(grep "TOTAL" "$output_file" | grep -o "[0-9]\+%" | tail -1 || echo "N/A")

        # Extract issues
        local issues=""
        if grep -q "FAILED" "$output_file"; then
            local fail_count=$(grep -c "FAILED" "$output_file" || echo "0")
            issues="${fail_count} failed"
        fi

        if grep -q "ERROR" "$output_file"; then
            local error_count=$(grep -c "ERROR" "$output_file" || echo "0")
            if [ -n "$issues" ]; then
                issues="$issues, ${error_count} errors"
            else
                issues="${error_count} errors"
            fi
        fi

        if [ -z "$issues" ]; then
            issues="-"
        fi

        printf "%-35s | %-12s | %-15s | %-15s | %s\n" "$group" "$status" "$test_info" "$coverage" "$issues"
    done

    echo ""
    echo "Individual pytest test logs:"
    for group in "${GROUP_DIRS[@]}"; do
        local output_file="part_6_${group}_pytest_output.txt"
        if [ -f "$output_file" ]; then
            echo "  - $output_file"
        fi
    done

    return $total_failed
}

# ============================================================================
# AUTODOCS TESTING
# ============================================================================

wait_for_autodocs() {
    local max_wait=30
    local wait_count=0

    while ! curl -s http://localhost:${AUTODOCS_PORT}/ >/dev/null 2>&1; do
        sleep 1
        wait_count=$((wait_count + 1))
        if [ $wait_count -ge $max_wait ]; then
            echo "Autodocs server did not start within $max_wait seconds"
            return 1
        fi
        if [ $((wait_count % 5)) -eq 0 ]; then
            echo "  Still waiting... ($wait_count seconds elapsed)"
        fi
    done
    return 0
}

run_autodocs_test_single() {
    local group=$1
    local output_file="part_6_${group}_autodocs_output.txt"

    echo "======================================================================"
    echo "AUTODOCS TESTING: $group"
    echo "======================================================================"

    cd "$group" || return 1

    # Start autodocs server
    echo "Starting autodocs server for $group..."
    make autodocs < /dev/null > autodocs_output.log 2>&1 &
    local AUTODOCS_PID=$!

    # Give it time to start
    sleep 3

    # Check if the process is still running
    if ! kill -0 $AUTODOCS_PID 2>/dev/null; then
        echo "✗ autodocs process died quickly" | tee "../$output_file"
        cat autodocs_output.log >> "../$output_file"
        cd ..
        return 1
    fi

    # Wait for autodocs to be ready
    echo "Waiting for autodocs to be ready..."
    if wait_for_autodocs; then
        echo "✓ Autodocs server is ready" | tee "../$output_file"

        # Test that we can access the autodocs
        echo "" | tee -a "../$output_file"
        echo "--- Testing autodocs pages ---" | tee -a "../$output_file"

        local exit_code=0

        # Test index page
        if curl -s http://localhost:${AUTODOCS_PORT}/ | grep -q "html"; then
            echo "✓ Index page accessible" | tee -a "../$output_file"
        else
            echo "✗ Index page not accessible" | tee -a "../$output_file"
            exit_code=1
        fi

        # Test about page
        if curl -s http://localhost:${AUTODOCS_PORT}/about/ | grep -q "html"; then
            echo "✓ About page accessible" | tee -a "../$output_file"
        else
            echo "✗ About page not accessible" | tee -a "../$output_file"
            exit_code=1
        fi

        # Test docs page
        if curl -s http://localhost:${AUTODOCS_PORT}/docs/ | grep -q "html"; then
            echo "✓ Docs page accessible" | tee -a "../$output_file"
        else
            echo "✗ Docs page not accessible" | tee -a "../$output_file"
            exit_code=1
        fi

        # Check for route documentation coverage
        echo "" | tee -a "../$output_file"
        echo "--- Checking for route documentation ---" | tee -a "../$output_file"

        local docs_content=$(curl -s http://localhost:${AUTODOCS_PORT}/docs/)

        # Check for v1 routes
        local v1_routes=("row_count" "unique_nyse_stock_count" "unique_nasdaq_stock_count")
        local missing_v1=0
        for route in "${v1_routes[@]}"; do
            if echo "$docs_content" | grep -qi "$route"; then
                echo "  ✓ Found v1 route: $route" | tee -a "../$output_file"
            else
                echo "  ⚠ Missing v1 route: $route" | tee -a "../$output_file"
                missing_v1=$((missing_v1 + 1))
            fi
        done

        # Check for v2/v3 presence (at least some routes should be documented)
        if echo "$docs_content" | grep -qi "v2\|year\|symbol"; then
            echo "  ✓ Found v2 route documentation" | tee -a "../$output_file"
        else
            echo "  ⚠ No v2 route documentation found" | tee -a "../$output_file"
        fi

        if echo "$docs_content" | grep -qi "v3\|account\|stock"; then
            echo "  ✓ Found v3 route documentation" | tee -a "../$output_file"
        else
            echo "  ⚠ No v3 route documentation found" | tee -a "../$output_file"
        fi

        # Check for test documentation
        if echo "$docs_content" | grep -qi "test"; then
            echo "  ✓ Found test documentation" | tee -a "../$output_file"
        else
            echo "  ⚠ No test documentation found" | tee -a "../$output_file"
        fi

        if [ $exit_code -eq 0 ]; then
            echo "" | tee -a "../$output_file"
            echo "✓ Autodocs tests passed for $group" | tee -a "../$output_file"
        else
            echo "" | tee -a "../$output_file"
            echo "✗ Some autodocs tests failed for $group" | tee -a "../$output_file"
        fi
    else
        echo "✗ Autodocs server failed to start for $group" | tee "../$output_file"
        exit_code=1
    fi

    # Stop autodocs server
    echo "Stopping autodocs server..."
    if [ ! -z "$AUTODOCS_PID" ]; then
        kill $AUTODOCS_PID 2>/dev/null
        wait $AUTODOCS_PID 2>/dev/null
    fi

    rm -f autodocs_output.log

    cd ..
    return $exit_code
}

run_autodocs_tests_sequential() {
    echo "======================================================================"
    echo "PHASE 4: SEQUENTIAL AUTODOCS TESTING"
    echo "======================================================================"
    echo "Testing autodocs for all groups sequentially"
    echo ""

    local start_time=$(date +%s)
    local total_failed=0

    for group in "${GROUP_DIRS[@]}"; do
        if ! run_autodocs_test_single "$group"; then
            total_failed=$((total_failed + 1))
        fi
        echo ""
    done

    # Calculate elapsed time
    local end_time=$(date +%s)
    local elapsed=$((end_time - start_time))
    local minutes=$((elapsed / 60))
    local seconds=$((elapsed % 60))

    echo "======================================================================"
    echo "PHASE 4 COMPLETE"
    echo "======================================================================"
    echo "Total time: ${minutes}m ${seconds}s"
    echo ""

    if [ $total_failed -eq 0 ]; then
        echo "✓ All autodocs tests passed!"
    else
        echo "✗ $total_failed group(s) had autodocs test failures"
    fi

    # Generate summary table
    echo ""
    echo "======================================================================"
    echo "AUTODOCS TEST SUMMARY"
    echo "======================================================================"
    echo ""

    printf "%-35s | %-12s | %-15s | %-s\n" "Group" "Status" "Pages" "Issues"
    printf "%-35s-+-%-12s-+-%-15s-+-%-s\n" "-----------------------------------" "------------" "---------------" "-------------------"

    for group in "${GROUP_DIRS[@]}"; do
        local output_file="part_6_${group}_autodocs_output.txt"

        if [ ! -f "$output_file" ]; then
            printf "%-35s | %-12s | %-15s | %s\n" "$group" "❓ No log" "N/A" "Log file not found"
            continue
        fi

        # Check if tests passed
        local status
        if grep -q "✓ Autodocs tests passed" "$output_file"; then
            status="✓ PASS"
        else
            status="✗ FAIL"
        fi

        # Count accessible pages
        local pages_ok=$(grep -c "page accessible" "$output_file" 2>/dev/null || echo "0")
        pages_ok=$(echo "$pages_ok" | tr -d '\n' | head -1)
        local pages_info="${pages_ok}/3"

        # Extract issues
        local issues=""
        local warnings=$(grep -c "⚠ Missing" "$output_file" 2>/dev/null || echo "0")
        warnings=$(echo "$warnings" | tr -d '\n' | head -1)
        if [ "$warnings" -gt 0 ] 2>/dev/null; then
            issues="${warnings} warnings"
        fi

        if [ -z "$issues" ]; then
            issues="-"
        fi

        printf "%-35s | %-12s | %-15s | %s\n" "$group" "$status" "$pages_info" "$issues"
    done

    echo ""
    echo "Individual autodocs test logs:"
    for group in "${GROUP_DIRS[@]}"; do
        local output_file="part_6_${group}_autodocs_output.txt"
        if [ -f "$output_file" ]; then
            echo "  - $output_file"
        fi
    done

    return $total_failed
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

echo "========================================================================"
echo "Part 6 Build and Run"
echo "========================================================================"
echo "Configuration:"
echo "  API Key: $API_KEY"
echo "  RAW_DATA_DIR: $RAW_DATA_DIR"
echo "  Flask Port: $FLASK_PORT"
echo "  Autodocs Port: $AUTODOCS_PORT"
echo ""

if [ -n "$SINGLE_GROUP" ]; then
    echo "Mode: Single group testing (Group-${SINGLE_GROUP})"
else
    echo "Mode: All groups testing (${#GROUP_DIRS[@]} groups found)"
fi

if [ "$DB_ONLY" = true ]; then
    echo "Phase: Database testing only"
elif [ "$FLASK_ONLY" = true ]; then
    echo "Phase: Flask testing only"
elif [ "$TESTS_ONLY" = true ]; then
    echo "Phase: Student pytest testing only"
elif [ "$AUTODOCS_ONLY" = true ]; then
    echo "Phase: Autodocs testing only"
else
    echo "Phase: All tests (Pre-check + Database + Flask + Pytest + Autodocs)"
fi
echo ""

# Execute based on options
overall_status=0
precheck_failed=0
db_failed=0
flask_failed=0
pytest_failed=0
autodocs_failed=0

# Pre-check: Database not committed
if [ "$DB_ONLY" = false ] && [ "$FLASK_ONLY" = false ] && [ "$TESTS_ONLY" = false ] && [ "$AUTODOCS_ONLY" = false ]; then
    if ! run_precheck_all; then
        precheck_failed=1
        overall_status=1
    fi
    echo ""
fi

# Database tests
if [ "$FLASK_ONLY" = false ] && [ "$TESTS_ONLY" = false ] && [ "$AUTODOCS_ONLY" = false ]; then
    # Run database tests
    if [ -n "$SINGLE_GROUP" ]; then
        # Single group - run sequentially
        if ! run_db_test_single "${GROUP_DIRS[0]}"; then
            db_failed=1
            overall_status=1
        fi
    else
        # Multiple groups - run in parallel
        if ! run_db_tests_parallel; then
            db_failed=1
            overall_status=1
        fi
    fi

    echo ""
fi

# Flask tests
if [ "$DB_ONLY" = false ] && [ "$TESTS_ONLY" = false ] && [ "$AUTODOCS_ONLY" = false ]; then
    # Run Flask tests
    if [ -n "$SINGLE_GROUP" ]; then
        # Single group
        if ! run_flask_test_single "${GROUP_DIRS[0]}"; then
            flask_failed=1
            overall_status=1
        fi
    else
        # Multiple groups - run sequentially
        if ! run_flask_tests_sequential; then
            flask_failed=1
            overall_status=1
        fi
    fi

    echo ""
fi

# Student pytest tests
if [ "$DB_ONLY" = false ] && [ "$FLASK_ONLY" = false ] && [ "$AUTODOCS_ONLY" = false ]; then
    # Run pytest tests sequentially
    if ! run_pytest_tests_sequential; then
        pytest_failed=1
        overall_status=1
    fi

    echo ""
fi

# Autodocs tests
if [ "$DB_ONLY" = false ] && [ "$FLASK_ONLY" = false ] && [ "$TESTS_ONLY" = false ]; then
    # Run autodocs tests sequentially
    if ! run_autodocs_tests_sequential; then
        autodocs_failed=1
        overall_status=1
    fi
fi

# Final summary
echo ""
echo "========================================================================"
echo "FINAL SUMMARY"
echo "========================================================================"

if [ "$DB_ONLY" = false ] && [ "$FLASK_ONLY" = false ] && [ "$TESTS_ONLY" = false ] && [ "$AUTODOCS_ONLY" = false ]; then
    echo "Pre-check (DB not committed): $([ $precheck_failed -eq 0 ] && echo "✓ PASS" || echo "⚠ WARNINGS")"
fi

if [ "$FLASK_ONLY" = false ] && [ "$TESTS_ONLY" = false ] && [ "$AUTODOCS_ONLY" = false ]; then
    echo "Database tests:               $([ $db_failed -eq 0 ] && echo "✓ PASS" || echo "✗ FAIL")"
fi

if [ "$DB_ONLY" = false ] && [ "$TESTS_ONLY" = false ] && [ "$AUTODOCS_ONLY" = false ]; then
    echo "Flask API tests:              $([ $flask_failed -eq 0 ] && echo "✓ PASS" || echo "✗ FAIL")"
fi

if [ "$DB_ONLY" = false ] && [ "$FLASK_ONLY" = false ] && [ "$AUTODOCS_ONLY" = false ]; then
    echo "Student pytest tests:         $([ $pytest_failed -eq 0 ] && echo "✓ PASS" || echo "✗ FAIL")"
fi

if [ "$DB_ONLY" = false ] && [ "$FLASK_ONLY" = false ] && [ "$TESTS_ONLY" = false ]; then
    echo "Autodocs tests:               $([ $autodocs_failed -eq 0 ] && echo "✓ PASS" || echo "✗ FAIL")"
fi

echo ""

if [ $overall_status -eq 0 ]; then
    echo "✓ ALL TESTS PASSED"
else
    echo "✗ SOME TESTS FAILED"
    if [ $precheck_failed -ne 0 ]; then
        echo "  - Pre-check warnings: $precheck_failed group(s)"
    fi
    if [ $db_failed -ne 0 ]; then
        echo "  - Database failures: $db_failed group(s)"
    fi
    if [ $flask_failed -ne 0 ]; then
        echo "  - Flask failures: $flask_failed group(s)"
    fi
    if [ $pytest_failed -ne 0 ]; then
        echo "  - Pytest failures: $pytest_failed group(s)"
    fi
    if [ $autodocs_failed -ne 0 ]; then
        echo "  - Autodocs failures: $autodocs_failed group(s)"
    fi
fi

echo ""
echo "Check individual log files for detailed results:"
echo "  - Pre-check logs: part_6_*_precheck_output.txt"
if [ "$FLASK_ONLY" = false ] && [ "$TESTS_ONLY" = false ] && [ "$AUTODOCS_ONLY" = false ]; then
    echo "  - DB logs: part_6_*_db_output.txt"
fi
if [ "$DB_ONLY" = false ] && [ "$TESTS_ONLY" = false ] && [ "$AUTODOCS_ONLY" = false ]; then
    echo "  - Flask logs: part_6_*_flask_output.txt"
fi
if [ "$DB_ONLY" = false ] && [ "$FLASK_ONLY" = false ] && [ "$AUTODOCS_ONLY" = false ]; then
    echo "  - Pytest logs: part_6_*_pytest_output.txt"
fi
if [ "$DB_ONLY" = false ] && [ "$FLASK_ONLY" = false ] && [ "$TESTS_ONLY" = false ]; then
    echo "  - Autodocs logs: part_6_*_autodocs_output.txt"
fi
echo ""

exit $overall_status
