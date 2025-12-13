# Rule34 Web Scraper

A command-line tool for downloading images and metadata from Rule34 image board.

## Features

- **Tag-based search**: Search and download posts by tags
- **Three operational modes**:
  - `new`: Start a new download task
  - `resume`: Resume an interrupted task
  - `sync`: Sync with remote to get new posts
- **Automatic retry**: Network errors are automatically retried with exponential backoff
- **Proxy support**: HTTP/HTTPS/SOCKS5 proxy configuration
- **Task persistence**: Progress is saved and can be resumed at any time
- **Metadata extraction**: Saves tags in categorized format (Artist, Copyright, Character, General, Meta)

## Installation

Ensure you have Python 3.7+ and required dependencies:

```bash
pip install requests beautifulsoup4 PySocks
```

## Usage

### Starting a New Task

Download all posts matching specific tags:

```bash
python rule34_scraper.py --mode new --tags "hatsune_miku" --storage-path "./downloads"
```

Multiple tags:

```bash
python rule34_scraper.py --mode new --tags "hatsune_miku vocaloid" --storage-path "./downloads"
```

Tags with special characters:

```bash
python rule34_scraper.py --mode new --tags "anohana:_the_flower_we_saw_that_day" --storage-path "./downloads"
```

### Resuming an Interrupted Task

If a download was interrupted, resume it:

```bash
python rule34_scraper.py --mode resume --task-path "./downloads/hatsune_miku"
```

The resume mode will:
1. Load the existing task state
2. Download any incomplete posts
3. Automatically trigger a sync to check for new posts

### Syncing with Remote

Check for new posts and download them:

```bash
python rule34_scraper.py --mode sync --task-path "./downloads/hatsune_miku"
```

## Advanced Options

### Throttling

Control the delay between requests (default: 2.5 seconds):

```bash
python rule34_scraper.py --mode new --tags "tag" --storage-path "./downloads" --throttle 3.0
```

### Retry Configuration

Set maximum retry attempts (default: 3):

```bash
python rule34_scraper.py --mode new --tags "tag" --storage-path "./downloads" --max-retries 5
```

### Proxy Configuration

Use a proxy server:

```bash
# HTTP proxy
python rule34_scraper.py --mode new --tags "tag" --storage-path "./downloads" --proxy "http://proxy.example.com:8080"

# SOCKS5 proxy
python rule34_scraper.py --mode new --tags "tag" --storage-path "./downloads" --proxy "socks5://proxy.example.com:1080"

# Authenticated proxy
python rule34_scraper.py --mode new --tags "tag" --storage-path "./downloads" --proxy "http://proxy.example.com:8080" --proxy-auth "username:password"
```

## Task Folder Structure

Each task creates a folder with the following structure:

```
hatsune_miku/
├── task_metadata.json     # Task metadata and progress
├── post_list.json         # List of all posts with download status
└── posts/
    ├── 15795581.jpeg      # Downloaded image
    ├── 15795581_tags.json # Tag metadata
    ├── 15795880.png
    ├── 15795880_tags.json
    └── ...
```

### task_metadata.json

Contains task information:

```json
{
  "search_tags": "hatsune_miku",
  "storage_path": "./downloads",
  "task_folder": "./downloads/hatsune_miku",
  "created_at": "2025-12-12T14:00:00",
  "last_updated": "2025-12-12T15:30:00",
  "last_synced": "2025-12-12T15:30:00",
  "status": "COMPLETE",
  "total_posts": 120,
  "completed_posts": 118,
  "mode_history": ["new", "resume", "sync"]
}
```

### post_list.json

Tracks each post's download status:

```json
[
  {
    "post_id": 15795581,
    "status": "COMPLETE",
    "image_url": "https://wimg.rule34.xxx/images/...",
    "file_extension": "jpeg",
    "download_timestamp": "2025-12-12T14:05:23"
  },
  {
    "post_id": 15795582,
    "status": "FAIL",
    "image_url": null,
    "file_extension": null,
    "download_timestamp": null
  }
]
```

### Tag Metadata Format

Each post's tags are saved in a separate JSON file:

```json
{
  "post_id": 15795581,
  "artist": ["ge-b"],
  "copyright": ["vocaloid"],
  "character": ["hatsune_miku", "megurine_luka"],
  "general": ["2girls", "aqua_hair", "yuri"],
  "meta": ["highres"]
}
```

## Exit Codes

- `0` - Success
- `1` - Invalid arguments
- `2` - Task validation failed
- `3` - Network error
- `4` - Server refused (403/410)
- `5` - Storage error
- `6` - Proxy connection failed
- `7` - Proxy authentication failed

## Error Handling

### Server Refusal (403/410)

If the server refuses the request:

```
[ERROR] HTTP 403 - Server refused request
[ERROR] Task state saved. Resume with:
  python rule34_scraper.py --mode resume --task-path "./downloads/hatsune_miku"
```

The task state is saved and you can manually investigate before resuming.

### Network Errors

Transient network errors are automatically retried with exponential backoff:

```
[WARNING] Request failed: Connection timeout. Retrying in 5s... (Attempt 1/3)
[WARNING] Request failed: Connection timeout. Retrying in 10s... (Attempt 2/3)
[WARNING] Request failed: Connection timeout. Retrying in 20s... (Attempt 3/3)
```

## Testing

Run the test suite:

```bash
python test_scraper.py
```

The test suite validates:
- URL construction with various tag formats
- Pagination detection
- Post ID extraction
- Post detail parsing (image URL and tags)

## Differences from Danbooru Scraper

### URL Structure
- Rule34 uses query parameters (`?page=post&s=list&tags=...`)
- Tags are joined with `+` and URL-encoded
- Pagination uses `pid` parameter (pid = (page - 1) * 42)

### Pagination
- Rule34 doesn't show total pages directly
- Must follow "next" links or find the last page link
- 42 posts per page

### Image URL Extraction
- Finds anchor element containing text "Original image"
- No fallback to img element (throws exception if not found)

### Tag Structure
- Uses `#tag-sidebar` container
- Tags organized by category headers (h6 elements)
- Categories: Copyright, Character, Artist, General, Meta

## Notes

- Rule34 uses Cloudflare protection, the scraper includes proper User-Agent headers
- Respect the default 2.5-second throttle to avoid triggering anti-bot measures
- Large collections may take hours to download
- Always check the server's terms of service before scraping
