#!/bin/bash

# Check if URL is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <download_url>"
    exit 1
fi

# Get the download URL
URL=$1

# Extract filename from URL
FILENAME=$(basename "$URL")

# Download the file
echo "Downloading $URL..."
wget "$URL" -O "$FILENAME"

# Decompress the .zst file
echo "Decompressing $FILENAME..."
zstd -d "$FILENAME"

# Extract the .tar file
TAR_FILENAME="${FILENAME%.zst}"
echo "Extracting $TAR_FILENAME..."
tar -xvf "$TAR_FILENAME"

# Decompress all .gz files in the current directory and subdirectories
echo "Decompressing all .gz files..."
find . -name "*.gz" -exec gunzip {} +

echo "Decompression completed."
