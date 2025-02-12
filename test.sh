#!/bin/bash

# Sample log data with a task URL
LOG="
2024-02-12 10:15:23 INFO Starting process
2024-02-12 10:15:24 INFO TASK_URL: https://example.com/tasks/123456
2024-02-12 10:15:25 INFO Processing complete
"

# Extract the task URL
TASK_URL=$(echo "$LOG" | perl -ne 'print $1 if /TASK_URL: (.*)/')

# Print the extracted URL
echo "Extracted Task URL: $TASK_URL"

# You can then use $TASK_URL in other commands
if [ ! -z "$TASK_URL" ]; then
    echo "Found task at: $TASK_URL"
    # Example: curl "$TASK_URL" to fetch the task
else
    echo "No task URL found in log"
fi