# CC-Share File Copy

Copy a file to the CC-Share network folder for cross-system access.

---

## Usage

```
/cc-share <file_path>
```

**Arguments:**
- `file_path` - Path to the file to copy (relative or absolute)

---

## Execution Steps

1. **Validate the file exists:**
   ```bash
   [ -f "$FILE_PATH" ] && echo "File found" || echo "ERROR: File not found"
   ```

2. **Check/create project directory on share:**
   ```bash
   SHARE_DIR=~/cc-share/HomeLab
   [ -d "$SHARE_DIR" ] || mkdir -p "$SHARE_DIR"
   ```

3. **Copy the file:**
   ```bash
   cp "$FILE_PATH" "$SHARE_DIR/"
   ```

4. **Verify and report:**
   ```bash
   ls -la "$SHARE_DIR/$(basename $FILE_PATH)"
   ```

---

## Share Details

| Parameter | Value |
|-----------|-------|
| **Local Path** | `~/cc-share` (symlink) |
| **Project Folder** | `~/cc-share/HomeLab` |
| **Full GVFS Path** | `/run/user/1000/gvfs/smb-share:server=ccpm-nas.local,share=cc-share/` |
| **NAS** | Synology DS1621 (10.0.1.251) |

---

## Example

```bash
# Copy a document
/cc-share docs/hardware-inventory.md

# Copy a script
/cc-share scripts/backup.sh
```

---

## Implementation

When this command is invoked with a file path argument:

```bash
#!/bin/bash
FILE_PATH="$1"
SHARE_DIR=~/cc-share/HomeLab

# Validate input
if [ -z "$FILE_PATH" ]; then
    echo "ERROR: No file path provided"
    echo "Usage: /cc-share <file_path>"
    exit 1
fi

# Check file exists
if [ ! -f "$FILE_PATH" ]; then
    echo "ERROR: File not found: $FILE_PATH"
    exit 1
fi

# Check share is mounted
if [ ! -d ~/cc-share ]; then
    echo "ERROR: CC-Share not mounted at ~/cc-share"
    echo "Mount via: Files > Other Locations > ccpm-nas.local"
    exit 1
fi

# Create project directory if needed
if [ ! -d "$SHARE_DIR" ]; then
    echo "Creating directory: $SHARE_DIR"
    mkdir -p "$SHARE_DIR"
fi

# Copy file
FILENAME=$(basename "$FILE_PATH")
cp "$FILE_PATH" "$SHARE_DIR/"

# Verify
if [ -f "$SHARE_DIR/$FILENAME" ]; then
    echo "SUCCESS: Copied to $SHARE_DIR/$FILENAME"
    ls -lh "$SHARE_DIR/$FILENAME"
else
    echo "ERROR: Copy failed"
    exit 1
fi
```

---

*HomeLab Agent - CC-Share file copy utility*
