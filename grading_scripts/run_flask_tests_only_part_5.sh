#!/bin/bash

# Run ONLY Flask tests (assumes databases are already loaded)

API_KEY="${DATA_241_API_KEY:-test_grading_key_2024}"
RAW_DATA_DIR="/Users/nickross/data_grading/project_data"
FLASK_PORT=4000

export DATA_241_API_KEY="$API_KEY"
export RAW_DATA_DIR="$RAW_DATA_DIR"

echo "======================================================================"
echo "FLASK-ONLY TESTING (Sequential)"
echo "======================================================================"
echo "Testing Flask APIs - databases should already be loaded"
echo "Using API key: $API_KEY"
echo "Using port: $FLASK_PORT"
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

# Create temp directory for JSON results
results_dir=$(mktemp -d)
trap "rm -rf $results_dir" EXIT

start_time=$(date +%s)
total_failed=0

# Test each group
for group_num in 1 2 3 4 5 6 7; do
    group="2025-Data-24100-Group-${group_num}"

    if [ ! -d "$group" ]; then
        echo "⚠ Skipping $group - directory not found"
        continue
    fi

    echo "======================================================================"
    echo "Testing Flask API for $group"
    echo "======================================================================"

    cd "$group" || { echo "Failed to enter $group directory"; continue; }

    output_file="../part_4_${group}_flask_output.txt"
    > "$output_file"

    {
        # Start Flask server (make flask will handle build)
        echo "Starting Flask server for $group..."
        PYTHONUNBUFFERED=1 make flask < /dev/null > flask_output.log 2>&1 &
        FLASK_PID=$!

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
                total_failed=$((total_failed + 1))
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
                --api v3 \
                --key "$API_KEY" \
                --url "http://localhost:${FLASK_PORT}"

            AUTOGRADER_EXIT_CODE=$?

            # Capture JSON results for summary
            python3 ../flask_autograder.py \
                --api v1 \
                --api v2 \
                --api v3 \
                --key "$API_KEY" \
                --url "http://localhost:${FLASK_PORT}" \
                --json > "$results_dir/${group}_flask.json" 2>/dev/null

            if [ $AUTOGRADER_EXIT_CODE -eq 0 ]; then
                echo "✓ All Flask API tests passed for $group"
            else
                echo "✗ Some Flask API tests failed for $group"
                total_failed=$((total_failed + 1))
            fi
        else
            echo "✗ Flask server failed to start for $group"
            total_failed=$((total_failed + 1))
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

# Calculate elapsed time
end_time=$(date +%s)
elapsed=$((end_time - start_time))
minutes=$((elapsed / 60))
seconds=$((elapsed % 60))

echo ""
echo "======================================================================"
echo "FLASK TESTING COMPLETE"
echo "======================================================================"
echo "Total time: ${minutes}m ${seconds}s"
echo ""

echo "Individual Flask test logs created:"
for group_num in 1 2 3 4 5 6 7; do
    group="2025-Data-24100-Group-${group_num}"
    output_file="part_4_${group}_flask_output.txt"
    if [ -f "$output_file" ]; then
        file_size=$(wc -l < "$output_file")
        echo "  - $output_file (${file_size} lines)"
    fi
done

echo ""
if [ $total_failed -eq 0 ]; then
    echo "✓ All Flask tests passed!"
else
    echo "✗ $total_failed group(s) failed Flask testing"
fi

exit $total_failed
