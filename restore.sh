#!/bin/bash

# Check if a backup file name was provided
if [ -z "$1" ]; then
    echo "Usage: ./restore.sh <backup_file_name.tar.gz>"
    echo "Example: ./restore.sh lobe_postgres_data_20251216_183700.tar.gz"
    exit 1
fi

BACKUP_FILE="$1"

# Infer the volume name from the backup file name (e.g., extracts 'lobe_postgres_data')
# You'll need to adjust this if your file naming convention is different.
VOLUME_TO_RESTORE=$(echo "$BACKUP_FILE" | grep -oP '.*(?=_[0-9]{8}_[0-9]{6}\.tar\.gz)')

if [ -z "$VOLUME_TO_RESTORE" ]; then
    echo "ERROR: Could not infer the volume name from the file: $BACKUP_FILE"
    echo "Please ensure the file name follows the pattern: VOLUME_NAME_YYYYMMDD_HHMMSS.tar.gz"
    exit 1
fi

echo "Inferred Volume: $VOLUME_TO_RESTORE"
echo "Backup File: $BACKUP_FILE"

echo "Starting volume restore process for $VOLUME_TO_RESTORE..."
echo "=> Restoring data from $BACKUP_FILE into volume $VOLUME_TO_RESTORE..."

# Run a temporary container to extract the archive into the volume
docker run --rm \
  -v "$VOLUME_TO_RESTORE":/volume_data \
  -v "$BACKUP_DIR":/backup \
  ubuntu:latest \
  bash -c "rm -rf /volume_data/* && tar xzf /backup/$BACKUP_FILE -C /volume_data"
# NOTE: The 'rm -rf /volume_data/*' ensures the volume is empty before extracting,
# preventing merged or old data.

if [ $? -eq 0 ]; then
    echo "   [SUCCESS] Restore complete for volume $VOLUME_TO_RESTORE."
else
    echo "   [ERROR] Restore failed for volume $VOLUME_TO_RESTORE."
    exit 1
fi

echo "Restore process finished."