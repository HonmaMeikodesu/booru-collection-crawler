# Yande Scraper - Usage Examples

This document provides practical examples of using the Yande scraper in various scenarios.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Advanced Usage](#advanced-usage)
- [Resume and Sync](#resume-and-sync)
- [Error Handling](#error-handling)
- [Expected Output](#expected-output)

## Basic Usage

### Example 1: Download Posts by Single Tag

Download all posts tagged with "honma_meiko":

```bash
python yande_scraper.py --mode new --tags "honma_meiko" --storage-path "E:\downloads"
```

**Expected Output:**

```
[INFO] Yande Scraper v1.0
[INFO] Mode: new
[INFO] Tags: honma_meiko
[INFO] Storage: E:\downloads
[INFO] Creating task folder: E:\downloads\honma_meiko
[INFO] Fetching page 1...
[INFO] Found 40 posts on page 1
[INFO] Fetching page 2...
[INFO] Found 40 posts on page 2
...
[INFO] Total pages traversed: 5
[INFO] Total posts found: 171
[INFO] Downloading post 1/171 (ID: 1239787)
[INFO] Image saved: 1239787.jpg (0.8 MB)
[INFO] Tags saved: 1239787_tags.json
...
[INFO] Task complete. Total posts: 171
```

**Folder Structure:**

```
E:\downloads\
└── honma_meiko\
    ├── task_metadata.json
    ├── post_list.json
    └── posts\
        ├── 1239787.jpg
        ├── 1239787_tags.json
        ├── 1098138.jpg
        ├── 1098138_tags.json
        └── ...
```

### Example 2: Download Posts by Multiple Tags

Download posts matching "honma_meiko" AND "dress":

```bash
python yande_scraper.py --mode new --tags "honma_meiko dress" --storage-path "E:\downloads"
```

**Expected Output:**

```
[INFO] Yande Scraper v1.0
[INFO] Mode: new
[INFO] Tags: honma_meiko dress
[INFO] Storage: E:\downloads
[INFO] Creating task folder: E:\downloads\honma_meiko_dress
[INFO] Fetching page 1...
[INFO] Found 32 posts on page 1
...
```

**Note:** Multiple tags narrow down the search results (AND operation).

## Advanced Usage

### Example 3: Custom Throttle Time

Use a longer delay between requests to avoid rate limiting:

```bash
python yande_scraper.py --mode new --tags "landscape" --storage-path "E:\downloads" --throttle 5.0
```

This sets a 5-second delay between each request.

### Example 4: Custom Retry Settings

Increase maximum retry attempts for unstable connections:

```bash
python yande_scraper.py --mode new --tags "sunset" --storage-path "E:\downloads" --max-retries 5
```

### Example 5: Using SOCKS5 Proxy

Download through a SOCKS5 proxy:

```bash
python yande_scraper.py --mode new --tags "anime" --storage-path "E:\downloads" \
  --proxy "socks5://127.0.0.1:1080"
```

With authentication:

```bash
python yande_scraper.py --mode new --tags "anime" --storage-path "E:\downloads" \
  --proxy "socks5://127.0.0.1:1080" --proxy-auth "username:password"
```

**Expected Output:**

```
[INFO] Yande Scraper v1.0
[INFO] Mode: new
[INFO] Tags: anime
[INFO] Storage: E:\downloads
[INFO] Proxy: socks5://127.0.0.1:1080 (authenticated)
[INFO] Testing proxy connection...
[INFO] Proxy connection successful
[INFO] Creating task folder: E:\downloads\anime
...
```

### Example 6: Using HTTP Proxy

Download through an HTTP proxy:

```bash
python yande_scraper.py --mode new --tags "character" --storage-path "E:\downloads" \
  --proxy "http://proxy.example.com:8080" --proxy-auth "user:pass"
```

## Resume and Sync

### Example 7: Resume Interrupted Download

If a download is interrupted, resume from the last checkpoint:

```bash
python yande_scraper.py --mode resume --task-path "E:\downloads\honma_meiko"
```

**Expected Output:**

```
[INFO] Yande Scraper v1.0
[INFO] Mode: resume
[INFO] Task path: E:\downloads\honma_meiko
[INFO] Tags: honma_meiko
[INFO] Resume info: 50 posts remaining
[INFO] Downloading post 122/171 (ID: 518707)
[INFO] Image saved: 518707.jpg (2.1 MB)
[INFO] Tags saved: 518707_tags.json
...
[INFO] Download phase complete: 171/171 posts
[INFO] Triggering automatic sync operation...
[INFO] Fetching current post list from server...
[INFO] Sync complete: No new posts found
[INFO] Task complete. Total posts: 171
```

**Note:** After completing downloads, resume mode automatically checks for new posts.

### Example 8: Sync Completed Task

Check for and download new posts added since last download:

```bash
python yande_scraper.py --mode sync --task-path "E:\downloads\honma_meiko"
```

**Expected Output (with new posts):**

```
[INFO] Yande Scraper v1.0
[INFO] Mode: sync
[INFO] Task path: E:\downloads\honma_meiko
[INFO] Tags: honma_meiko
[INFO] Fetching current post list from server...
[INFO] Total pages traversed: 5
[INFO] Total posts found: 175
[INFO] Found 4 new posts
[INFO] Downloading post 1/4 (ID: 1250000)
[INFO] Image saved: 1250000.jpg (1.2 MB)
[INFO] Tags saved: 1250000_tags.json
...
[INFO] Sync complete: 4 new posts downloaded
[INFO] Task complete. Total posts: 175
```

**Expected Output (no new posts):**

```
[INFO] Yande Scraper v1.0
[INFO] Mode: sync
[INFO] Task path: E:\downloads\honma_meiko
[INFO] Tags: honma_meiko
[INFO] Fetching current post list from server...
[INFO] Total pages traversed: 5
[INFO] Total posts found: 171
[INFO] Sync complete: No new posts found
[INFO] Task complete. Total posts: 171
```

## Error Handling

### Example 9: Network Error with Retry

When network errors occur, the scraper automatically retries:

```
[INFO] Downloading post 50/171 (ID: 681984)
[WARNING] Request failed: Connection reset by peer. Retrying in 5s... (Attempt 1/3)
[INFO] Image saved: 681984.jpg (2.4 MB)
[INFO] Tags saved: 681984_tags.json
```

### Example 10: Server Refusal (403/410)

If the server refuses requests:

```
[INFO] Downloading post 75/171 (ID: 546266)
[ERROR] HTTP 403 - Server refused request
[ERROR] URL: https://yande.re/post/show/546266
[ERROR] Headers: {...}
[ERROR] Server refused request: Server returned 403
[ERROR] Task state saved. Resume with:
[ERROR]   python yande_scraper.py --mode resume --task-path "E:\downloads\honma_meiko"
```

**User Action:**

1. Wait for some time (e.g., 30 minutes)
2. Optionally configure a proxy
3. Resume the task:

```bash
python yande_scraper.py --mode resume --task-path "E:\downloads\honma_meiko" \
  --proxy "socks5://127.0.0.1:1080"
```

### Example 11: Post Not Found (404)

If a specific post is deleted or unavailable:

```
[INFO] Downloading post 120/171 (ID: 123456)
[WARNING] Resource not found: https://yande.re/post/show/123456
[WARNING] Post 123456: No image URL found
[INFO] Downloading post 121/171 (ID: 465213)
[INFO] Image saved: 465213.jpg (3.2 MB)
...
```

The scraper continues with remaining posts.

### Example 12: Image Not Found Error

If the image download link is missing from a post page:

```
[INFO] Downloading post 85/171 (ID: 999999)
[ERROR] Post 999999: Original image link not found for post 999999
[INFO] Downloading post 86/171 (ID: 464887)
...
```

## Expected Output

### Task Metadata Example

**task_metadata.json:**

```json
{
  "search_tags": "honma_meiko dress",
  "storage_path": "E:\\downloads",
  "task_folder": "E:\\downloads\\honma_meiko_dress",
  "created_at": "2025-12-15T10:00:00.000000",
  "last_updated": "2025-12-15T10:45:30.000000",
  "last_synced": "2025-12-15T11:00:00.000000",
  "status": "COMPLETE",
  "total_posts": 120,
  "completed_posts": 120,
  "mode_history": ["new", "sync"]
}
```

### Post List Example

**post_list.json:**

```json
[
  {
    "post_id": 1239787,
    "status": "COMPLETE",
    "image_url": "https://files.yande.re/image/45763dbcea55cc0b3b55df5d9cb0df0a/yande.re%201239787%20anjou_naruko%20ano_hi_mita_hana_no_namae_wo_bokutachi_wa_mada_shiranai%20disc_cover%20dress%20honma_meiko%20megane%20tanaka_masayoshi%20tsurumi_chiriko.jpg",
    "file_extension": "jpg",
    "download_timestamp": "2025-12-15T10:15:22.000000"
  },
  {
    "post_id": 1098138,
    "status": "COMPLETE",
    "image_url": "https://files.yande.re/image/700503a01b3eafe4d6425d0cf9c03110/yande.re%201098138%20ano_hi_mita_hana_no_namae_wo_bokutachi_wa_mada_shiranai%20dress%20honma_meiko%20shiroraku%20skirt_lift%20summer_dress.jpg",
    "file_extension": "jpg",
    "download_timestamp": "2025-12-15T10:15:55.000000"
  }
]
```

### Tags Example

**1239787_tags.json:**

```json
{
  "post_id": 1239787,
  "artist": [
    "tanaka masayoshi"
  ],
  "copyright": [
    "ano hi mita hana no namae wo bokutachi wa mada shiranai"
  ],
  "character": [
    "anjou naruko",
    "honma meiko",
    "tsurumi chiriko"
  ],
  "general": [
    "disc cover",
    "dress",
    "megane"
  ]
}
```

## Tips and Best Practices

### 1. Start with Small Tag Searches

Test with specific tags that have fewer results:

```bash
python yande_scraper.py --mode new --tags "honma_meiko wedding_dress" --storage-path "E:\downloads"
```

### 2. Monitor First Few Downloads

Watch the first few downloads to ensure everything works correctly:

- Check image quality
- Verify tags are extracted
- Confirm folder structure

### 3. Use Appropriate Throttle

For large downloads, use a conservative throttle time:

```bash
python yande_scraper.py --mode new --tags "popular_tag" --storage-path "E:\downloads" --throttle 3.0
```

### 4. Regular Sync Operations

Run sync periodically to keep your collection up-to-date:

```bash
# Run weekly
python yande_scraper.py --mode sync --task-path "E:\downloads\my_collection"
```

### 5. Backup Task Metadata

Keep backups of `task_metadata.json` and `post_list.json`:

```bash
# Windows
copy "E:\downloads\honma_meiko\task_metadata.json" "E:\backups\"
copy "E:\downloads\honma_meiko\post_list.json" "E:\backups\"
```

### 6. Check Exit Codes

In scripts, check exit codes to handle errors:

```bash
python yande_scraper.py --mode new --tags "test" --storage-path "E:\downloads"
if %ERRORLEVEL% EQU 4 (
    echo Server refused, waiting 30 minutes...
    timeout /t 1800
    python yande_scraper.py --mode resume --task-path "E:\downloads\test"
)
```

### 7. Proxy Rotation

If using multiple proxies, rotate them on server refusal:

```bash
python yande_scraper.py --mode resume --task-path "E:\downloads\collection" --proxy "socks5://proxy1:1080"
# If fails, try:
python yande_scraper.py --mode resume --task-path "E:\downloads\collection" --proxy "socks5://proxy2:1080"
```

## Common Scenarios

### Scenario 1: Daily Collection Updates

```bash
# Initial download
python yande_scraper.py --mode new --tags "daily_favorites" --storage-path "E:\downloads"

# Daily sync (via scheduled task)
python yande_scraper.py --mode sync --task-path "E:\downloads\daily_favorites"
```

### Scenario 2: Large Archive Download

```bash
# Use longer throttle for large archives
python yande_scraper.py --mode new --tags "archive_tag" --storage-path "E:\archive" \
  --throttle 5.0 --max-retries 5
```

### Scenario 3: Multi-Tag Collection

```bash
# Create separate tasks for different tag combinations
python yande_scraper.py --mode new --tags "character1 dress" --storage-path "E:\collection"
python yande_scraper.py --mode new --tags "character2 landscape" --storage-path "E:\collection"
python yande_scraper.py --mode new --tags "artist_name" --storage-path "E:\collection"
```

Each creates a separate folder with its own metadata and images.
