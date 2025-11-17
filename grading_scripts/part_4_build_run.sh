#!/bin/bash

# Part 4 Autograder - Unified script for DB and Flask testing
# Supports parallel DB testing and sequential Flask testing

# Parse command line arguments
SINGLE_GROUP=""
FLASK_ONLY=false
DB_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -g|--group)
            SINGLE_GROUP="$2"
            shift 2
            ;;
        --flask-only)
            FLASK_ONLY=true
            shift
            ;;
        --db-only)
            DB_ONLY=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [-g|--group GROUP_NUMBER] [--flask-only|--db-only]"
            echo ""
            echo "Options:"
            echo "  -g, --group NUMBER    Test only a specific group (e.g., -g 1 for Group-1)"
            echo "  --flask-only          Run only Flask tests (assumes DB already loaded)"
            echo "  --db-only             Run only DB tests (parallel execution)"
            echo "  -h, --help            Show this help message"
            echo ""
            echo "Default behavior (no flags): Run both DB tests (parallel) and Flask tests (sequential)"
            echo ""
            echo "Examples:"
            echo "  $0                    # Run DB + Flask for all groups"
            echo "  $0 -g 1               # Run DB + Flask for Group-1 only"
            echo "  $0 --db-only          # Run DB tests for all groups (parallel)"
            echo "  $0 --flask-only       # Run Flask tests for all groups (sequential, assumes DB loaded)"
            echo "  $0 -g 1 --db-only     # Run DB tests for Group-1 only"
            echo "  $0 -g 1 --flask-only  # Run Flask tests for Group-1 only"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Validate flags
if [ "$FLASK_ONLY" = true ] && [ "$DB_ONLY" = true ]; then
    echo "Error: Cannot use both --flask-only and --db-only flags together"
    exit 1
fi

# Configuration
API_KEY="${DATA_241_API_KEY:-test_grading_key_2024}"
RAW_DATA_DIR="/Users/nickross/data_grading/project_data"
FLASK_PORT=4000

export DATA_241_API_KEY="$API_KEY"
export RAW_DATA_DIR="$RAW_DATA_DIR"

# Output files
summary_file="part_4_summary.md"
> "$summary_file"

# Print configuration
echo "======================================================================"
echo "PART 4 AUTOGRADER"
echo "======================================================================"
if [ -n "$SINGLE_GROUP" ]; then
    echo "Target: Group-${SINGLE_GROUP}"
else
    echo "Target: All groups"
fi

if [ "$DB_ONLY" = true ]; then
    echo "Mode: Database tests only (parallel execution)"
elif [ "$FLASK_ONLY" = true ]; then
    echo "Mode: Flask tests only (sequential execution)"
else
    echo "Mode: Database tests (parallel) + Flask tests (sequential)"
fi

echo "Using API key: $API_KEY"
echo "Using RAW_DATA_DIR: $RAW_DATA_DIR"
echo ""

# Determine which groups to test
if [ -n "$SINGLE_GROUP" ]; then
    GROUP_DIRS=("2025-Data-24100-Group-${SINGLE_GROUP}")
    if [ ! -d "${GROUP_DIRS[0]}" ]; then
        echo "✗ ERROR: Directory ${GROUP_DIRS[0]} does not exist"
        exit 1
    fi
else
    GROUP_DIRS=()
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

echo "Found ${#GROUP_DIRS[@]} group(s) to test:"
for group in "${GROUP_DIRS[@]}"; do
    echo "  - $group"
done
echo ""

# ======================================================================
# PHASE 1: DATABASE TESTS (PARALLEL)
# ======================================================================
if [ "$FLASK_ONLY" = false ]; then
    echo "======================================================================"
    echo "PHASE 1: PARALLEL DATABASE TESTING"
    echo "======================================================================"
    echo ""

    db_start_time=$(date +%s)
    db_pids=()

    for group in "${GROUP_DIRS[@]}"; do
        output_file="part_4_${group}_db_output.txt"

        (
            cd "$group" || exit 1
            echo "[$(date '+%H:%M:%S')] Starting DB tests for $group..." | tee "../$output_file"
            python3 ../db_commands_tester.py --repo-dir . --keep-loaded 2>&1 | tee -a "../$output_file"
            exit_code=$?
            echo "[$(date '+%H:%M:%S')] DB tests for $group completed with exit code: $exit_code" | tee -a "../$output_file"
            exit $exit_code
        ) &

        db_pids+=($!)
    done

    # Wait for all DB tests to complete
    echo "Waiting for all database tests to complete..."
    db_failed=0
    for pid in "${db_pids[@]}"; do
        if ! wait $pid; then
            db_failed=$((db_failed + 1))
        fi
    done

    db_end_time=$(date +%s)
    db_elapsed=$((db_end_time - db_start_time))
    db_minutes=$((db_elapsed / 60))
    db_seconds=$((db_elapsed % 60))

    echo ""
    echo "======================================================================"
    echo "PHASE 1 COMPLETE"
    echo "======================================================================"
    echo "Total time: ${db_minutes}m ${db_seconds}s"
    echo ""

    if [ $db_failed -eq 0 ]; then
        echo "✓ All database tests passed!"
    else
        echo "✗ $db_failed group(s) had database test failures"
    fi

    echo ""
    echo "Individual DB test logs:"
    for group in "${GROUP_DIRS[@]}"; do
        output_file="part_4_${group}_db_output.txt"
        if [ -f "$output_file" ]; then
            timing=$(grep "db_load completed in" "$output_file" | head -1)
            echo "  - $output_file"
            if [ -n "$timing" ]; then
                echo "    $timing"
            fi
        fi
    done
    echo ""
fi

# ======================================================================
# PHASE 2: FLASK TESTS (SEQUENTIAL)
# ======================================================================
if [ "$DB_ONLY" = false ]; then
    if [ "$FLASK_ONLY" = false ]; then
        echo "======================================================================"
        echo "PHASE 2: SEQUENTIAL FLASK TESTING"
        echo "======================================================================"
    else
        echo "======================================================================"
        echo "FLASK TESTING (assumes databases already loaded)"
        echo "======================================================================"
    fi
    echo ""

    # Function to wait for Flask to be ready
    wait_for_flask() {
        local max_wait=60
        local wait_count=0

        while ! curl -s http://localhost:${FLASK_PORT}/api/v1/row_count >/dev/null 2>&1 && \
              ! curl -s http://localhost:${FLASK_PORT}/api/v2/2019 >/dev/null 2>&1; do
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

    # Function to stop all running containers
    stop_containers() {
        docker ps -q | xargs -r docker stop >/dev/null 2>&1
    }

    flask_start_time=$(date +%s)
    flask_failed=0

    # Create temp directory for JSON results
    results_dir=$(mktemp -d)
    trap "rm -rf $results_dir" EXIT

    # Test each group sequentially
    for group in "${GROUP_DIRS[@]}"; do
        echo "======================================================================"
        echo "Testing Flask API for $group"
        echo "======================================================================"

        cd "$group" || { echo "Failed to enter $group directory"; continue; }

        output_file="../part_4_${group}_flask_output.txt"
        > "$output_file"

        {
            # Build Docker image
            image_name=$(echo "$group" | tr '[:upper:]' '[:lower:]')
            echo "Building Docker image for $group..."
            if docker build -q . -t "$image_name" 2>&1; then
                echo "✓ Docker build successful for $group"
            else
                echo "✗ Docker build failed for $group"
                cd ..
                flask_failed=$((flask_failed + 1))
                continue
            fi

            # Start Flask server
            echo "Starting Flask server for $group..."
            PYTHONUNBUFFERED=1 make flask < /dev/null > flask_output.log 2>&1 &
            FLASK_PID=$!

            # Give Docker time to start
            sleep 3

            # Check if process is still running
            if ! kill -0 $FLASK_PID 2>/dev/null; then
                echo "⚠ Warning: make flask process died quickly. Checking for running containers..."
                if docker ps --format '{{.Names}}' | grep -q "data241"; then
                    echo "✓ Found running Docker container"
                else
                    echo "✗ No container found running"
                    cat flask_output.log
                    cd ..
                    flask_failed=$((flask_failed + 1))
                    continue
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
                    --key "$API_KEY" \
                    --url "http://localhost:${FLASK_PORT}"

                AUTOGRADER_EXIT_CODE=$?

                # Capture JSON results for summary
                python3 ../flask_autograder.py \
                    --api v1 \
                    --api v2 \
                    --key "$API_KEY" \
                    --url "http://localhost:${FLASK_PORT}" \
                    --json > "$results_dir/${group}_flask.json" 2>/dev/null

                if [ $AUTOGRADER_EXIT_CODE -eq 0 ]; then
                    echo "✓ All Flask API tests passed for $group"
                else
                    echo "✗ Some Flask API tests failed for $group"
                    flask_failed=$((flask_failed + 1))
                fi
            else
                echo "✗ Flask server failed to start for $group"
                flask_failed=$((flask_failed + 1))
            fi

            # Stop Flask server
            echo "Stopping Flask server..."
            if [ ! -z "$FLASK_PID" ]; then
                kill $FLASK_PID 2>/dev/null
                wait $FLASK_PID 2>/dev/null
            fi

            # Stop any Docker containers
            stop_containers

            # Clean up log file
            rm -f flask_output.log

            echo ""
        } 2>&1 | tee "$output_file"

        cd ..
    done

    flask_end_time=$(date +%s)
    flask_elapsed=$((flask_end_time - flask_start_time))
    flask_minutes=$((flask_elapsed / 60))
    flask_seconds=$((flask_elapsed % 60))

    echo ""
    echo "======================================================================"
    if [ "$FLASK_ONLY" = false ]; then
        echo "PHASE 2 COMPLETE"
    else
        echo "FLASK TESTING COMPLETE"
    fi
    echo "======================================================================"
    echo "Total time: ${flask_minutes}m ${flask_seconds}s"
    echo ""

    if [ $flask_failed -eq 0 ]; then
        echo "✓ All Flask tests passed!"
    else
        echo "✗ $flask_failed group(s) failed Flask testing"
    fi

    echo ""
    echo "Individual Flask test logs:"
    for group in "${GROUP_DIRS[@]}"; do
        output_file="part_4_${group}_flask_output.txt"
        if [ -f "$output_file" ]; then
            file_size=$(wc -l < "$output_file" 2>/dev/null || echo "0")
            echo "  - $output_file (${file_size} lines)"
        fi
    done
    echo ""
fi

# ======================================================================
# GENERATE SUMMARY TABLE
# ======================================================================
echo "======================================================================"
echo "GENERATING SUMMARY"
echo "======================================================================"
echo ""

# Generate markdown summary table
RESULTS_DIR="$results_dir" python3 << 'PYTHON_SCRIPT' > "$summary_file"
import json
import os
import sys
from pathlib import Path

results_dir = os.environ.get('RESULTS_DIR', '')

# Collect all results
results = []

# Find all group directories
group_dirs = sorted([d for d in Path('.').glob('2025-Data-24100-Group-*') if d.is_dir()])

for group_path in group_dirs:
    group_name = group_path.name

    # Load Flask results from JSON (if available)
    flask_data = {}
    if results_dir:
        flask_json = Path(results_dir) / f"{group_name}_flask.json"
        if flask_json.exists():
            try:
                with open(flask_json) as f:
                    flask_data = json.load(f)
            except Exception as e:
                print(f"Error reading {flask_json}: {e}", file=sys.stderr)

    # Load DB results from log file
    db_data = {}
    db_file = Path(f"part_4_{group_name}_db_output.txt")
    if db_file.exists():
        try:
            content = db_file.read_text()

            # Extract test results
            if 'ALL DATABASE TESTS PASSED' in content:
                db_data['all_passed'] = True
            else:
                db_data['all_passed'] = False

            # Extract test counts
            for line in content.split('\n'):
                if line.startswith('INFO - Total tests:'):
                    db_data['total_tests'] = int(line.split(':')[1].strip())
                elif line.startswith('INFO - Passed:'):
                    db_data['passed'] = int(line.split(':')[1].strip())
                elif line.startswith('INFO - Failed:'):
                    db_data['failed'] = int(line.split(':')[1].strip())
                elif 'db_load completed in' in line:
                    parts = line.split('db_load completed in')
                    if len(parts) > 1:
                        time_str = parts[1].strip().split()[0]
                        db_data['db_load_time'] = float(time_str)
        except Exception as e:
            print(f"Error reading {db_file}: {e}", file=sys.stderr)

    results.append({
        'group': group_name,
        'flask': flask_data,
        'db': db_data
    })

if not results:
    print("# Part 4 Summary\n\nNo results found.")
    sys.exit(0)

# Print markdown table
print("# Part 4 Autograder Summary\n")
print("## Overall Results\n")
print("| Group | Status | DB Tests | Flask Tests | V1 API | V2 API | db_load Time | Issues |")
print("|-------|--------|----------|-------------|--------|--------|--------------|--------|")

for result in results:
    group = result['group']
    flask_data = result.get('flask', {})
    db_data = result.get('db', {})

    # Determine overall status
    flask_passed = flask_data.get('all_passed', False) if flask_data else None
    db_passed = db_data.get('all_passed', False) if db_data else None

    # If either test was run, check if it passed
    if flask_passed is not None and db_passed is not None:
        all_passed = flask_passed and db_passed
    elif flask_passed is not None:
        all_passed = flask_passed
    elif db_passed is not None:
        all_passed = db_passed
    else:
        all_passed = False

    status = "✅ PASS" if all_passed else "❌ FAIL"

    # DB tests
    if db_data and 'total_tests' in db_data:
        db_tests = f"{db_data.get('passed', 0)}/{db_data.get('total_tests', 0)}"
    else:
        db_tests = "N/A"

    # Flask tests
    if flask_data and 'total_tests' in flask_data:
        flask_tests = f"{flask_data.get('passed', 0)}/{flask_data.get('total_tests', 0)}"
    else:
        flask_tests = "N/A"

    # V1 and V2 status
    endpoint_data = flask_data.get('endpoint_data', {})
    v1_passed = any(key in endpoint_data for key in ['row_count', 'unique_nyse_stock_count', 'unique_nasdaq_stock_count'])
    v2_passed = any(key.startswith('v2_year_') or key.startswith('v2_open_') or
                    key.startswith('v2_close_') or key.startswith('v2_high_') or
                    key.startswith('v2_low_') or key.startswith('v2_high_low_')
                    for key in endpoint_data.keys())

    v1_status = "✓" if v1_passed else "✗" if flask_data else "N/A"
    v2_status = "✓" if v2_passed else "✗" if flask_data else "N/A"

    # Get db_load time
    db_load_time = db_data.get('db_load_time')
    if db_load_time is not None:
        db_load_str = f"{db_load_time:.1f}s"
    else:
        db_load_str = "N/A"

    # Collect issues
    issues = []
    if flask_passed is False:
        issues.append("Flask API")
    if db_passed is False:
        issues.append("DB commands")
    if flask_data.get('header_issues', False):
        issues.append("HTTP headers")

    issues_str = ", ".join(issues) if issues else "None"

    print(f"| {group} | {status} | {db_tests} | {flask_tests} | {v1_status} | {v2_status} | {db_load_str} | {issues_str} |")

# Data consistency section (only if Flask tests were run)
flask_results_exist = any(r.get('flask') for r in results)

if flask_results_exist:
    print("\n## Data Validation\n")

    # Collect data from passing groups
    row_counts = set()
    year_counts_map = {}  # year -> set of counts

    for result in results:
        if result.get('flask', {}).get('all_passed', False):
            endpoint_data = result['flask'].get('endpoint_data', {})

            # V1 row count
            rc = endpoint_data.get('row_count', {}).get('row_count')
            if rc is not None:
                row_counts.add(rc)

            # V2 year counts
            for key, value in endpoint_data.items():
                if key.startswith('v2_year_'):
                    year = key.replace('v2_year_', '')
                    if isinstance(value, dict) and 'count' in value:
                        if year not in year_counts_map:
                            year_counts_map[year] = set()
                        year_counts_map[year].add(value['count'])

    # Check consistency
    v1_consistent = len(row_counts) <= 1
    v2_consistent = all(len(counts) <= 1 for counts in year_counts_map.values())

    if v1_consistent and v2_consistent:
        print("✅ **All groups that passed returned consistent data values**")
    else:
        print("⚠️ **Warning: Groups returned different values**")
        if not v1_consistent:
            print(f"- V1 row counts vary: {sorted(row_counts)}")
        if not v2_consistent:
            for year, counts in year_counts_map.items():
                if len(counts) > 1:
                    print(f"- Year {year} counts vary: {sorted(counts)}")

    if row_counts or year_counts_map:
        print(f"\n**Expected Values (from passing groups):**")
        if len(row_counts) == 1:
            print(f"- Total row count (v1): {list(row_counts)[0]:,}")

        if year_counts_map:
            print(f"\n**Year Counts:**")
            for year in sorted(year_counts_map.keys()):
                counts = year_counts_map[year]
                if len(counts) == 1:
                    print(f"- Year {year}: {list(counts)[0]:,} rows")

PYTHON_SCRIPT

echo "Summary table saved to: $summary_file"
echo ""

# Display the summary table
if [ -f "$summary_file" ]; then
    echo "======================================================================"
    echo "SUMMARY TABLE"
    echo "======================================================================"
    echo ""
    cat "$summary_file"
fi

# Determine overall exit code
overall_failed=0
if [ "$FLASK_ONLY" = false ] && [ -n "${db_failed+x}" ]; then
    overall_failed=$((overall_failed + db_failed))
fi
if [ "$DB_ONLY" = false ] && [ -n "${flask_failed+x}" ]; then
    overall_failed=$((overall_failed + flask_failed))
fi

echo ""
echo "======================================================================"
echo "FINAL RESULT"
echo "======================================================================"
if [ $overall_failed -eq 0 ]; then
    echo "✓ ALL TESTS PASSED!"
    exit 0
else
    echo "✗ $overall_failed GROUP(S) FAILED"
    exit 1
fi
