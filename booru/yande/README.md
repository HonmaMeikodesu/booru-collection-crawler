# Yande.re Scraper

A command-line tool for downloading high-resolution images and metadata from [Yande.re](https://yande.re), an image archiving website. The scraper supports tag-based searching, task resumption, synchronization, and proxy configuration.

## Features

- **Tag-Based Search**: Download posts matching specific tags
- **High-Resolution Downloads**: Automatically fetches the highest quality images available
- **Metadata Extraction**: Saves tags categorized by type (artist, copyright, character, general)
- **Task Resumption**: Resume interrupted downloads from the last checkpoint
- **Task Synchronization**: Update completed tasks with newly published posts
- **Proxy Support**: HTTP, HTTPS, and SOCKS5 proxy configuration
- **Rate Limiting**: Configurable throttling to avoid server blocks
- **Error Handling**: Automatic retry with exponential backoff for network errors

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r ../../requirements.txt
```

Required packages:
- `requests>=2.31.0` - HTTP client library
- `beautifulsoup4>=4.12.0` - HTML parsing
- `PySocks>=1.7.1` - SOCKS proxy support

## Usage

The scraper operates in three modes: **new**, **resume**, and **sync**.

### Mode 1: Create New Task

Download posts matching specific tags:

```bash
python yande_scraper.py --mode new --tags "honma_meiko" --storage-path "E:\downloads"
```

With multiple tags:

```bash
python yande_scraper.py --mode new --tags "honma_meiko dress" --storage-path "E:\downloads"
```

### Mode 2: Resume Interrupted Task

Continue an interrupted download from the last checkpoint:

```bash
python yande_scraper.py --mode resume --task-path "E:\downloads\honma_meiko"
```

After completing downloads, the scraper automatically triggers a sync operation to check for new posts.

### Mode 3: Sync Completed Task

Update a completed task with newly published posts:

```bash
python yande_scraper.py --mode sync --task-path "E:\downloads\honma_meiko"
```

## Command-Line Arguments

### Common Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--mode` | Yes | - | Execution mode: `new`, `resume`, or `sync` |
| `--throttle` | No | 2.5 | Seconds between requests |
| `--max-retries` | No | 3 | Maximum retry attempts for failed requests |
| `--proxy` | No | None | Proxy server URL |
| `--proxy-auth` | No | None | Proxy authentication (username:password) |

### Mode-Specific Arguments

#### new Mode

| Argument | Required | Description |
|----------|----------|-------------|
| `--tags` | Yes | Space-separated search tags |
| `--storage-path` | Yes | Directory to store downloaded content |

#### resume / sync Modes

| Argument | Required | Description |
|----------|----------|-------------|
| `--task-path` | Yes | Path to existing task folder |

## Proxy Configuration

The scraper supports HTTP, HTTPS, and SOCKS5 proxies:

### Method 1: Embedded Authentication

```bash
python yande_scraper.py --mode new --tags "landscape" --storage-path "E:\downloads" \
  --proxy "socks5://username:password@127.0.0.1:1080"
```

### Method 2: Separate Authentication

```bash
python yande_scraper.py --mode new --tags "landscape" --storage-path "E:\downloads" \
  --proxy "socks5://127.0.0.1:1080" --proxy-auth "username:password"
```

## Task Folder Structure

Each task creates a dedicated folder with the following structure:

```
{storage_path}/
└── {sanitized_tags}/
    ├── task_metadata.json      # Task information and status
    ├── post_list.json           # List of all posts with status
    └── posts/
        ├── {post_id}.{ext}      # Downloaded images
        ├── {post_id}_tags.json  # Tag metadata per post
        └── ...
```

### task_metadata.json

Contains high-level task information:

```json
{
  "search_tags": "honma_meiko dress",
  "storage_path": "E:\\downloads",
  "task_folder": "E:\\downloads\\honma_meiko_dress",
  "created_at": "2025-12-15T00:00:00",
  "last_updated": "2025-12-15T00:30:00",
  "last_synced": "2025-12-15T00:30:00",
  "status": "COMPLETE",
  "total_posts": 150,
  "completed_posts": 150,
  "mode_history": ["new"]
}
```

### post_list.json

Array of post metadata:

```json
[
  {
    "post_id": 1239787,
    "status": "COMPLETE",
    "image_url": "https://files.yande.re/image/...",
    "file_extension": "jpg",
    "download_timestamp": "2025-12-15T00:15:00"
  }
]
```

### {post_id}_tags.json

Tags categorized by type:

```json
{
  "post_id": 1239787,
  "artist": ["tanaka masayoshi"],
  "copyright": ["ano hi mita hana no namae wo bokutachi wa mada shiranai"],
  "character": ["anjou naruko", "honma meiko", "tsurumi chiriko"],
  "general": ["disc cover", "dress", "megane"]
}
```

## Error Handling

The scraper handles different error types appropriately:

### Server Refusal (403, 410)

- **Action**: Halt execution and save current state
- **User Action**: Wait, change IP, or use a proxy, then resume
- **Exit Code**: 4

### Resource Not Found (404)

- **Action**: Log warning, mark post as FAIL, continue
- **Exit Code**: 0 (if task completes)

### Network Errors (Timeout, Connection Reset)

- **Action**: Automatic retry with exponential backoff (5s, 10s, 20s)
- **Max Retries**: 3 (configurable)
- **Exit Code**: 3 (if all retries exhausted)

## Exit Codes

| Code | Meaning | User Action |
|------|---------|-------------|
| 0 | Success | None |
| 1 | Invalid arguments | Check command syntax |
| 2 | Task validation failed | Verify task folder integrity |
| 3 | Network error exhausted retries | Check network connectivity |
| 4 | Server refusal (403/410) | Wait, change IP, or use proxy |
| 5 | Storage path error | Verify path exists and is writable |
| 6 | Proxy connection failed | Check proxy availability |
| 7 | Proxy authentication failed | Verify credentials |

## Examples

See [EXAMPLES.md](EXAMPLES.md) for detailed usage examples and expected output.

## Technical Details

### Rate Limiting

- Default throttle: 2.5 seconds between requests
- Applies to all HTTP requests (pagination, post details, images)
- Configurable via `--throttle` argument

### Data Integrity

- Images downloaded completely to memory before disk write
- Atomic write operations to prevent partial files
- Content-length validation when available

### Tag Encoding

Multiple tags are URL-encoded and joined with `+`:

```
Input:  "honma_meiko ano_hi_mita_hana_no_namae_wo_bokutachi_wa_mada_shiranai"
Output: "honma_meiko+ano_hi_mita_hana_no_namae_wo_bokutachi_wa_mada_shiranai"
URL:    https://yande.re/post?tags=honma_meiko+ano_hi_mita_hana_no_namae_wo_bokutachi_wa_mada_shiranai
```

### Pagination

Yande.re does not display total page count. The scraper:

1. Starts from page 1
2. Extracts the next page link from `.next_page` anchor
3. Continues until no next page link is found
4. Accumulates all post IDs across pages

## Troubleshooting

### "Server refused request" Error

If you encounter HTTP 403 or 410 errors:

1. Wait for some time before resuming
2. Use a different IP address or proxy
3. Resume the task with: `python yande_scraper.py --mode resume --task-path "{task_folder}"`

### Slow Downloads

- Increase throttle time: `--throttle 5.0`
- Check network connectivity
- Verify proxy performance if used

### Missing Tags

If tags are not extracted correctly:

- Verify the post has tags on the website
- Check the tag categories match expected types
- Report issue with post ID for investigation

## Development

### Running Tests

```bash
python test_scraper.py
```

Tests verify:
- Pagination parsing from HTML
- Post ID extraction from search results
- Image URL and tag extraction from post pages
- Tag sanitization for folder names

### Code Structure

- `yande_scraper.py` - Main scraper implementation
- `index.py` - Entry point
- `test_scraper.py` - Test suite
- `docs/` - Sample HTML files for testing

## License

This tool is for personal use only. Respect Yande.re's terms of service and rate limits.

## Support

For issues or questions:

1. Check [EXAMPLES.md](EXAMPLES.md) for common usage patterns
2. Verify your command-line arguments are correct
3. Check exit codes for specific error types
4. Review server response in logs for debugging
