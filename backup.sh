#!/bin/bash

VOLUME_NAMES=("lobe_postgres_data" "lobe_minio_data")

# Load .env
ENV_FILE=".env"
if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
fi

# Create the backup directory if it doesn't exist
mkdir -p $BACKUP_DIR
if [ $? -ne 0 ]; then
    echo "ERROR: Could not create backup directory $BACKUP_DIR. Exiting."
    exit 1
fi

# Loop through each volume and create a compressed archive
for VOLUME in "${VOLUME_NAMES[@]}"; do
    BACKUP_FILENAME="${VOLUME}_$(date +%Y%m%d_%H%M%S).tar.gz"
    echo "=> Backing up volume: $VOLUME to $BACKUP_DIR/$BACKUP_FILENAME"

    # Run a temporary container to archive the volume content
    docker run --rm \
      -v "$VOLUME":/volume_data \
      -v "$BACKUP_DIR":/backup \
      ubuntu:latest \
      tar czf /backup/"$BACKUP_FILENAME" -C /volume_data .

    if [ $? -eq 0 ]; then
        echo "   [SUCCESS] Backup complete: $BACKUP_FILENAME"
    else
        echo "   [ERROR] Backup failed for volume $VOLUME."
    fi
done

echo "Backup process finished. Files are located in: $BACKUP_DIR"