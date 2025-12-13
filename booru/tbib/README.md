# TBIB Web Scraper

A robust command-line tool for downloading images and metadata from The Big ImageBoard (TBIB).

## Features

- **Three Operation Modes**:
  - `new`: Start a new download task
  - `resume`: Continue an incomplete task
  - `sync`: Update completed task with new posts

- **Robust Error Handling**:
  - Automatic retry with exponential backoff
  - Graceful degradation on individual post failures
  - Resumable downloads from any failure point

- **Proxy Support**:
  - HTTP, HTTPS, and SOCKS5 proxy support
  - Proxy authentication support

- **Rate Limiting**:
  - Configurable throttling to avoid triggering anti-crawling mechanisms

## Installation

Dependencies are already listed in the project's main `requirements.txt`:
- `requests>=2.31.0`
- `beautifulsoup4>=4.12.0`
- `PySocks>=1.7.1`

## Usage

### Start a New Task

```bash
python tbib_scraper.py --mode new --tags "honma_meiko" --storage-path "./downloads"
```

With multiple tags:
```bash
python tbib_scraper.py --mode new --tags "honma_meiko ano_hi_mita_hana_no_namae_wo_bokutachi_wa_mada_shiranai." --storage-path "./downloads"
```

### Resume an Incomplete Task

```bash
python tbib_scraper.py --mode resume --task-path "./downloads/honma_meiko"
```

### Sync a Completed Task

```bash
python tbib_scraper.py --mode sync --task-path "./downloads/honma_meiko"
```

### Using Proxy

```bash
# HTTP proxy
python tbib_scraper.py --mode new --tags "test" --storage-path "./downloads" --proxy "http://localhost:8080"

# SOCKS5 proxy with authentication
python tbib_scraper.py --mode new --tags "test" --storage-path "./downloads" --proxy "socks5://localhost:1080" --proxy-auth "username:password"
```

### Advanced Options

```bash
python tbib_scraper.py --mode new \
  --tags "honma_meiko" \
  --storage-path "./downloads" \
  --throttle 3.0 \
  --max-retries 5 \
  --proxy "socks5://localhost:1080"
```

## Command-Line Arguments

### Required Arguments (mode-specific)

| Argument | Required For | Description |
|----------|-------------|-------------|
| `--mode` | All modes | Operation mode: `new`, `resume`, or `sync` |
| `--tags` | `new` | Space-separated search tags |
| `--storage-path` | `new` | Directory where task folder will be created |
| `--task-path` | `resume`, `sync` | Path to existing task folder |

### Optional Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--throttle` | float | 2.5 | Seconds between HTTP requests |
| `--max-retries` | int | 3 | Maximum retry attempts for failed requests |
| `--proxy` | string | None | Proxy server URL (http://, https://, socks5://) |
| `--proxy-auth` | string | None | Proxy credentials (username:password) |

## Task Folder Structure

When you create a new task, the following structure is created:

```
{sanitized_tags}/
├── task_metadata.json      # Task configuration and status
├── post_list.json          # List of all posts with download status
└── posts/                  # Downloaded content
    ├── {post_id}.{ext}     # Image files
    ├── {post_id}_tags.json # Tag metadata for each image
    └── ...
```

### Example: task_metadata.json

```json
{
  "search_tags": "honma_meiko",
  "storage_path": "./downloads",
  "task_folder": "./downloads/honma_meiko",
  "created_at": "2025-12-12T23:00:00.000000",
  "last_updated": "2025-12-12T23:30:00.000000",
  "last_synced": null,
  "status": "COMPLETE",
  "total_posts": 150,
  "completed_posts": 148,
  "mode_history": ["new"]
}
```

### Example: post_list.json

```json
[
  {
    "post_id": 26054136,
    "status": "COMPLETE",
    "image_url": "https://tbib.org//images/8987/370bb4b2300613c73511761f74075f979af5856b.png",
    "file_extension": "png",
    "download_timestamp": "2025-12-12T23:15:00.000000"
  },
  {
    "post_id": 26054137,
    "status": "FAIL",
    "image_url": null,
    "file_extension": null,
    "download_timestamp": null
  }
]
```

### Example: {post_id}_tags.json

```json
{
  "post_id": 26054136,
  "copyright": ["ano hi mita hana no namae wo bokutachi wa mada shiranai."],
  "character": ["honma meiko"],
  "artist": ["mizuki riyu"],
  "general": ["1girl", "blue eyes", "dress", "long hair", "smile"],
  "meta": ["absurdres", "highres"]
}
```

## Exit Codes

| Code | Name | Meaning |
|------|------|---------|
| 0 | EXIT_SUCCESS | Task completed successfully |
| 1 | EXIT_INVALID_ARGS | Invalid or missing arguments |
| 2 | EXIT_TASK_VALIDATION_FAILED | Task folder validation failed |
| 3 | EXIT_NETWORK_ERROR | Network error after retries |
| 4 | EXIT_SERVER_REFUSED | Server returned 403/410 |
| 5 | EXIT_STORAGE_ERROR | Storage path invalid or not writable |
| 6 | EXIT_PROXY_CONNECTION_FAILED | Proxy connection failed |
| 7 | EXIT_PROXY_AUTH_FAILED | Proxy authentication failed |

## Error Handling

### Automatic Retry

Network errors are automatically retried with exponential backoff:
- Base delay: 5 seconds
- Backoff multiplier: 2x
- Default max retries: 3

### Server Refusal

If the server returns HTTP 403 or 410, the scraper will:
1. Immediately halt execution
2. Save current task state
3. Display resume command
4. Exit with code 4

Example:
```
[ERROR] HTTP 403 - Server refused request
[ERROR] Task state saved. Resume with:
[ERROR]   python tbib_scraper.py --mode resume --task-path "./downloads/honma_meiko"
```

### Individual Post Failures

Posts that fail to download are marked with `FAIL` status and the scraper continues with remaining posts.

## Running Tests

```bash
cd booru/tbib
python -m unittest test_scraper.py -v
```

## Implementation Details

### Pagination Discovery

Unlike some booru sites, TBIB doesn't display total page count. The scraper:
1. Starts at page 1
2. Extracts the "next" link from `#paginator a[alt='next']`
3. Continues until no "next" link exists
4. Dynamically determines total pages

### Post ID Extraction

Post IDs are extracted from search result pages using:
- Selector: `#post-list .content div span > a`
- ID attribute format: `p{post_id}` (e.g., `p26054136`)

### Image URL Extraction

For each post detail page:
1. Finds anchor element containing text "Original image"
2. Extracts `href` attribute
3. Handles URLs starting with `//` by prepending `https:`
4. Raises error if original image link not found

### Tag Categorization

Tags are organized into five categories:
- **Copyright**: Series/franchise
- **Character**: Character names
- **Artist**: Creator attribution
- **General**: Descriptive content tags
- **Meta**: Technical metadata (resolution, rating)

Tags are extracted from `#tag-sidebar` using category headers (`<h6>`) and subsequent list items.

## Limitations

- No parallel downloads (sequential only)
- No sample image fallback if original unavailable
- Requires original image link to be present
- No authentication support for TBIB accounts

## Troubleshooting

### "Storage path is not writable"

Ensure the storage path exists and you have write permissions:
```bash
mkdir -p ./downloads
chmod +w ./downloads
```

### "Proxy connection failed"

Verify proxy server is running and accessible:
```bash
# Test proxy connection
curl -x http://localhost:8080 https://tbib.org
```

### "Server refused request"

If you see HTTP 403/410 errors:
1. Wait a few minutes before resuming
2. Increase throttle time: `--throttle 5.0`
3. Use a proxy if the site is blocking your IP

### Task appears stuck

Check the task metadata file to see progress:
```bash
cat ./downloads/honma_meiko/task_metadata.json
```

Resume if status is `FAILED`:
```bash
python tbib_scraper.py --mode resume --task-path "./downloads/honma_meiko"
```

## License

Part of the booru-collection-crawler project.
