# Gelbooru Web Scraper

A Python-based command-line tool for downloading images and metadata from [Gelbooru](https://gelbooru.com/).

## Features

- **Three Operation Modes:**
  - `new` - Create a new download task
  - `resume` - Resume an interrupted task
  - `sync` - Update completed tasks with new posts

- **Robust Error Handling:**
  - Automatic retry with exponential backoff
  - Server refusal detection (403/410)
  - Resumable downloads from breakpoints
  - Progress persistence

- **Proxy Support:**
  - HTTP/HTTPS/SOCKS5 proxies
  - Authentication support
  - Connection validation

- **Rate Limiting:**
  - Configurable request throttling
  - Prevents triggering anti-crawler mechanisms

## Installation

Ensure you have Python 3.7+ and the required dependencies:

```bash
pip install -r ../../requirements.txt
```

## Usage

### Create a New Task

Download posts matching specific tags:

```bash
python gelbooru_scraper.py --mode new --tags "honma_meiko" --storage-path "./downloads"
```

Multiple tags (space-separated):

```bash
python gelbooru_scraper.py --mode new --tags "honma_meiko ano_hi_mita_hana_no_namae_wo_bokutachi_wa_mada_shiranai." --storage-path "./downloads"
```

### Resume an Interrupted Task

If a task is interrupted (network error, server refusal, etc.), resume it:

```bash
python gelbooru_scraper.py --mode resume --task-path "./downloads/honma_meiko"
```

### Sync a Completed Task

Update an existing task with new posts from the server:

```bash
python gelbooru_scraper.py --mode sync --task-path "./downloads/honma_meiko"
```

### Using a Proxy

```bash
python gelbooru_scraper.py --mode new --tags "tag1 tag2" --storage-path "./downloads" \
  --proxy "http://proxy.example.com:8080" \
  --proxy-auth "username:password"
```

### Custom Throttling and Retries

```bash
python gelbooru_scraper.py --mode new --tags "tag" --storage-path "./downloads" \
  --throttle 3.0 \
  --max-retries 5
```

## Command-Line Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--mode` | Yes | Operation mode: `new`, `resume`, or `sync` |
| `--tags` | For `new` | Search tags (space-separated) |
| `--storage-path` | For `new` | Directory to store downloads |
| `--task-path` | For `resume`/`sync` | Path to existing task folder |
| `--throttle` | No | Seconds between requests (default: 2.5) |
| `--max-retries` | No | Maximum retry attempts (default: 3) |
| `--proxy` | No | Proxy server URL |
| `--proxy-auth` | No | Proxy authentication (username:password) |

## Task Folder Structure

```
{storage_path}/
└── {sanitized_tags}/
    ├── task_metadata.json     # Task configuration and progress
    ├── post_list.json         # List of all posts with status
    └── posts/
        ├── {post_id}.{ext}           # Downloaded image
        ├── {post_id}_tags.json       # Tag metadata
        └── ...
```

## Tag Categories

Gelbooru organizes tags into five categories:

- **Artist** - Content creators
- **Copyright** - Series/franchise
- **Character** - Character names
- **Metadata** - Technical information (resolution, file type)
- **Tag** - General descriptive tags

Each post's tags are saved with category information in `{post_id}_tags.json`.

## Error Codes

| Code | Name | Description |
|------|------|-------------|
| 0 | SUCCESS | Task completed successfully |
| 1 | INVALID_ARGS | Invalid command-line arguments |
| 2 | TASK_VALIDATION_FAILED | Task folder or metadata corrupted |
| 3 | NETWORK_ERROR | Network error after retries exhausted |
| 4 | SERVER_REFUSED | Server returned 403/410 (manual intervention needed) |
| 5 | STORAGE_ERROR | Storage path invalid or not writable |
| 6 | PROXY_CONNECTION_FAILED | Cannot connect through proxy |
| 7 | PROXY_AUTH_FAILED | Proxy authentication failed |

## How It Works

### New Task Workflow

1. Validates storage path and creates task folder
2. Fetches search results page by page (following "next" pagination links)
3. Extracts post IDs from each page
4. Creates a post list with PENDING status
5. For each post:
   - Fetches post details page
   - Locates "Original image" link
   - Downloads image to memory
   - Extracts and categorizes tags
   - Saves image and tags to disk
   - Marks post as COMPLETE

### Resume Workflow

1. Loads existing task metadata and post list
2. Identifies posts with status != COMPLETE
3. Continues downloading from breakpoints
4. Auto-triggers sync operation after completion

### Sync Workflow

1. Fetches current post list from server
2. Compares with local post list
3. Identifies new posts
4. Downloads only new posts
5. Updates metadata with sync timestamp

## Implementation Notes

### DOM Selectors

- **Post List Page:**
  - Container: `.thumbnail-container`
  - Post links: `article > a` (with `id="p{post_id}"`)
  - Next page: `#paginator a[alt="next"]`

- **Post Detail Page:**
  - Original image link: `li a` containing text "Original image"
  - Tag list: `#tag-list`
  - Tag categories: Detected by `<b>` headers (Artist, Character, Copyright, Metadata, Tag)
  - Tag items: `li` with class `tag-type-*`

### Pagination Strategy

Gelbooru uses `pid` parameter for pagination (e.g., `pid=42` for page 2). The scraper follows "next" links until no more pages exist, ensuring complete coverage.

### URL Encoding

Multiple tags are:
1. Split by spaces
2. URL-encoded individually
3. Joined with `+` signs

Example: `honma_meiko ano_hi_mita...` → `honma_meiko+ano_hi_mita...`

## Testing

Run the test suite:

```bash
python test_scraper.py
```

Tests verify:
- URL building and tag encoding
- Post ID extraction from HTML
- Tag sanitization for folder names
- Proxy configuration
- Tag category extraction

## Troubleshooting

### Server Returns 403/410

If the server refuses requests:
1. The scraper will halt and save state
2. Wait a few minutes
3. Resume with: `python gelbooru_scraper.py --mode resume --task-path "{path}"`

### Proxy Connection Issues

- Verify proxy URL format: `http://host:port` or `socks5://host:port`
- Check authentication credentials
- Test proxy manually with curl/wget

### Missing Original Image Link

If a post's original image link is not found:
- The post is marked as FAIL
- Check if the post exists on Gelbooru
- Some posts may have restricted access

## Best Practices

1. **Use Appropriate Throttling:** Default 2.5s is safe; reduce only if necessary
2. **Monitor Logs:** Watch for server refusal warnings
3. **Regular Syncing:** Run sync periodically to get new posts
4. **Backup Task Folders:** Preserve metadata for resume capability

## License

This tool is for personal use only. Respect Gelbooru's Terms of Service and rate limits.
