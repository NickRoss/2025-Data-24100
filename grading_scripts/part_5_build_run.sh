#!/bin/bash

# Part 5 Build and Run Script
# Consolidated script for database and Flask testing

# Parse command line arguments
SINGLE_GROUP=""
DB_ONLY=false
FLASK_ONLY=false

print_help() {
    echo "Usage: $0 [-g GROUP_NUMBER] [--db-only | --flask-only]"
    echo ""
    echo "Options:"
    echo "  -g GROUP_NUMBER    Test only a specific group (e.g., -g 1 for Group-1)"
    echo "                     Tests both DB and Flask for that group"
    echo "  --db-only          Run only database tests (parallel for all groups, sequential for single group)"
    echo "  --flask-only       Run only Flask tests (sequential)"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                 # Run DB tests (parallel) + Flask tests (sequential) for all groups"
    echo "  $0 -g 6            # Run DB + Flask tests for Group-6 only"
    echo "  $0 --db-only       # Run only DB tests for all groups (parallel)"
    echo "  $0 --flask-only    # Run only Flask tests for all groups (sequential)"
    echo "  $0 -g 6 --db-only  # Run only DB tests for Group-6"
    echo "  $0 -g 6 --flask-only # Run only Flask tests for Group-6"
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
if [ "$DB_ONLY" = true ] && [ "$FLASK_ONLY" = true ]; then
    echo "Error: Cannot specify both --db-only and --flask-only"
    exit 1
fi

# Configuration
API_KEY="${DATA_241_API_KEY:-test_grading_key_2024}"
RAW_DATA_DIR="/Users/nickross/data_grading/project_data"
FLASK_PORT=4000

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
# DATABASE TESTING FUNCTIONS
# ============================================================================

run_db_test_single() {
    local group=$1
    local output_file="part_5_${group}_db_output.txt"

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
        local output_file="part_5_${group}_db_output.txt"

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
        local output_file="part_5_${group}_db_output.txt"

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
        local timing=$(grep -o "db_load completed in [0-9.]*s" "$output_file" | head -1 | grep -o "[0-9.]*s" || echo "N/A")

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
        local output_file="part_5_${group}_db_output.txt"
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
    local output_file="part_5_${group}_flask_output.txt"

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
        local output_file="part_5_${group}_flask_output.txt"

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
        local output_file="part_5_${group}_flask_output.txt"
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
echo "Part 5 Build and Run"
echo "========================================================================"
echo "Configuration:"
echo "  API Key: $API_KEY"
echo "  RAW_DATA_DIR: $RAW_DATA_DIR"
echo "  Flask Port: $FLASK_PORT"
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
else
    echo "Phase: Database + Flask testing"
fi
echo ""

# Execute based on options
overall_status=0

if [ "$FLASK_ONLY" = false ]; then
    # Run database tests
    if [ -n "$SINGLE_GROUP" ]; then
        # Single group - run sequentially
        if ! run_db_test_single "${GROUP_DIRS[0]}"; then
            overall_status=1
        fi
    else
        # Multiple groups - run in parallel
        if ! run_db_tests_parallel; then
            overall_status=1
        fi
    fi

    echo ""
fi

if [ "$DB_ONLY" = false ]; then
    # Run Flask tests
    if [ -n "$SINGLE_GROUP" ]; then
        # Single group
        if ! run_flask_test_single "${GROUP_DIRS[0]}"; then
            overall_status=1
        fi
    else
        # Multiple groups - run sequentially
        if ! run_flask_tests_sequential; then
            overall_status=1
        fi
    fi
fi

# Final summary
echo ""
echo "========================================================================"
echo "FINAL SUMMARY"
echo "========================================================================"

if [ $overall_status -eq 0 ]; then
    echo "✓ ALL TESTS PASSED"
else
    echo "✗ SOME TESTS FAILED"
fi

echo ""
echo "Check individual log files for detailed results:"
if [ "$DB_ONLY" = false ]; then
    echo "  - Flask logs: part_5_*_flask_output.txt"
fi
if [ "$FLASK_ONLY" = false ]; then
    echo "  - DB logs: part_5_*_db_output.txt"
fi
echo ""

exit $overall_status
