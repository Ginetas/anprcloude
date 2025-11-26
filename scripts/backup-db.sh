#!/bin/bash
# Database Backup Script
# Creates timestamped database backups with automatic cleanup of old backups

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-.backup}"
POSTGRES_USER="${POSTGRES_USER:-anpr}"
POSTGRES_DB="${POSTGRES_DB:-anpr_db}"
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-postgres}"
RETENTION_DAYS="${DB_BACKUP_RETENTION_DAYS:-7}"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
BACKUP_FILE="${BACKUP_DIR}/backup_${POSTGRES_DB}_${TIMESTAMP}.sql"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Create backup directory
mkdir -p "${BACKUP_DIR}"

echo -e "${GREEN}Starting database backup...${NC}"
echo "Database: ${POSTGRES_DB}"
echo "Backup file: ${BACKUP_FILE}"
echo "Retention: ${RETENTION_DAYS} days"

# Check if running in Docker or locally
if command -v docker &> /dev/null && docker ps | grep -q "${POSTGRES_CONTAINER}"; then
    echo -e "${YELLOW}Docker container found, using docker exec...${NC}"
    docker exec "${POSTGRES_CONTAINER}" pg_dump \
        -U "${POSTGRES_USER}" \
        -d "${POSTGRES_DB}" \
        --verbose \
        --format=plain \
        --no-password \
        > "${BACKUP_FILE}"
else
    echo -e "${YELLOW}Using local PostgreSQL connection...${NC}"
    pg_dump \
        -U "${POSTGRES_USER}" \
        -d "${POSTGRES_DB}" \
        --verbose \
        --format=plain \
        > "${BACKUP_FILE}"
fi

# Check if backup was successful
if [ -s "${BACKUP_FILE}" ]; then
    BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    echo -e "${GREEN}Backup successful!${NC}"
    echo "File size: ${BACKUP_SIZE}"

    # Compress backup
    echo -e "${YELLOW}Compressing backup...${NC}"
    gzip "${BACKUP_FILE}"
    COMPRESSED_FILE="${BACKUP_FILE}.gz"
    COMPRESSED_SIZE=$(du -h "${COMPRESSED_FILE}" | cut -f1)
    echo -e "${GREEN}Compression complete!${NC}"
    echo "Compressed size: ${COMPRESSED_SIZE}"

    # Create metadata file
    {
        echo "Timestamp: ${TIMESTAMP}"
        echo "Database: ${POSTGRES_DB}"
        echo "Uncompressed size: ${BACKUP_SIZE}"
        echo "Compressed size: ${COMPRESSED_SIZE}"
        echo "Original file: ${BACKUP_FILE}"
    } > "${COMPRESSED_FILE}.meta"
else
    echo -e "${RED}Backup failed! File is empty.${NC}"
    rm -f "${BACKUP_FILE}"
    exit 1
fi

# Clean up old backups
echo -e "${YELLOW}Cleaning up old backups (older than ${RETENTION_DAYS} days)...${NC}"
find "${BACKUP_DIR}" -name "backup_${POSTGRES_DB}_*.sql.gz" -mtime +${RETENTION_DAYS} -type f -exec rm -fv {} \;
find "${BACKUP_DIR}" -name "backup_${POSTGRES_DB}_*.sql.gz.meta" -mtime +${RETENTION_DAYS} -type f -exec rm -fv {} \;

# List available backups
echo -e "${GREEN}Available backups:${NC}"
ls -lh "${BACKUP_DIR}"/backup_${POSTGRES_DB}_*.sql.gz 2>/dev/null | awk '{print $9, "(" $5 ")"}'

echo -e "${GREEN}Backup and cleanup completed successfully!${NC}"
