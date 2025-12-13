# Zerochan Scraper

A Python command-line tool for downloading images from Zerochan (https://www.zerochan.net) based on keyword searches.

## Features

- **Keyword-based Search**: Download all images matching your search keywords
- **Login Support**: Authenticate with Zerochan account to access full image data
- **Resumable Downloads**: Interrupted tasks can be resumed from where they left off
- **Auto-sync**: Automatically fetch new posts added to Zerochan
- **Proxy Support**: Configure HTTP/HTTPS/SOCKS5 proxies for restricted access
- **Rate Limiting**: Built-in throttling to avoid triggering anti-scraping measures
- **Metadata Tracking**: Complete task and download history preserved

## Requirements

- Python 3.x
- Dependencies listed in `requirements.txt`:
  - requests>=2.31.0
  - beautifulsoup4>=4.12.0
  - PySocks>=1.7.1

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Create a New Download Task

Download all images matching keywords "Honma Meiko":

```bash
python zerochan_scraper.py --mode new --keywords "Honma Meiko" --storage-path ./downloads
```

**With login (recommended for full image access):**

```bash
python zerochan_scraper.py --mode new \
  --keywords "Honma Meiko" \
  --storage-path ./downloads \
  --username "your_username" \
  --password "your_password"
```

This will:
1. Create a task folder in `./downloads/honma_meiko/`
2. Fetch all post IDs from all search result pages
3. Download each image with metadata
4. Save progress after each download

### Resume an Interrupted Task

If your download was interrupted, resume it:

```bash
python zerochan_scraper.py --mode resume \
  --task-path ./downloads/honma_meiko \
  --username "your_username" \
  --password "your_password"
```

Resume mode will:
1. Continue downloading incomplete posts
2. Automatically sync to fetch any new posts added since task creation

### Sync an Existing Task

Update a completed task with newly published posts:

```bash
python zerochan_scraper.py --mode sync \
  --task-path ./downloads/honma_meiko \
  --username "your_username" \
  --password "your_password"
```

## Command-Line Reference

### Required Arguments

- `--mode`: Operation mode
  - `new`: Create new download task
  - `resume`: Continue interrupted task
  - `sync`: Update completed task with new posts

### Mode-Specific Arguments

**New Mode**:
- `--keywords`: Search keywords (e.g., "Honma Meiko")
- `--storage-path`: Directory where task folder will be created

**Resume/Sync Modes**:
- `--task-path`: Path to existing task folder

### Optional Arguments

- `--throttle`: Seconds between requests (default: 2.5)
- `--max-retries`: Maximum retry attempts for failed requests (default: 3)
- `--proxy`: Proxy server URL (e.g., `http://proxy.example.com:8080`)
- `--proxy-auth`: Proxy authentication in `username:password` format
- `--username`: Zerochan account username for login
- `--password`: Zerochan account password for login

## Usage Examples

### Basic Download (with Login)

```bash
python zerochan_scraper.py --mode new \
  --keywords "Honma Meiko" \
  --storage-path ./my_collection \
  --username "your_username" \
  --password "your_password"
```

### Download without Login

```bash
python zerochan_scraper.py --mode new \
  --keywords "Honma Meiko" \
  --storage-path ./my_collection
```

**Note**: Login is recommended as Zerochan requires authentication to access full image data.

### Download with Proxy and Login

```bash
python zerochan_scraper.py --mode new \
  --keywords "Honma Meiko" \
  --storage-path ./my_collection \
  --proxy http://proxy.example.com:8080 \
  --proxy-auth myuser:mypass \
  --username "your_username" \
  --password "your_password"
```

### Download with Custom Throttle

```bash
python zerochan_scraper.py --mode new \
  --keywords "Honma Meiko" \
  --storage-path ./my_collection \
  --throttle 5.0
```

## Task Folder Structure

Each task creates a folder with the following structure:

```
honma_meiko/
├── task_metadata.json    # Task configuration and status
├── post_list.json        # List of all posts with download status
└── posts/                # Downloaded images
    ├── 2941468.jpg
    ├── 2941469.jpg
    └── ...
```

### task_metadata.json

Contains task configuration and progress:

```json
{
  "search_keywords": "Honma Meiko",
  "storage_path": "./my_collection",
  "task_folder": "./my_collection/honma_meiko",
  "created_at": "2025-12-09T01:00:00",
  "last_updated": "2025-12-09T01:30:00",
  "last_synced": null,
  "status": "COMPLETE",
  "total_posts": 150,
  "completed_posts": 150,
  "mode_history": ["new"]
}
```

### post_list.json

Tracks each post's download status:

```json
[
  {
    "post_id": 2941468,
    "status": "COMPLETE",
    "image_url": "https://static.zerochan.net/Honma.Meiko.full.2941468.jpg",
    "file_extension": "jpg",
    "download_timestamp": "2025-12-09T01:15:00"
  },
  ...
]
```

## Error Handling

The scraper handles various error scenarios:

### Network Errors
Automatically retries with exponential backoff (3 attempts by default)

### Server Refusal (403/410)
Halts execution and prompts for manual intervention

### Storage Errors
Validates storage path before task creation

### Proxy Errors
Tests proxy connection before starting download

## Exit Codes

- `0`: Success
- `1`: Invalid command-line arguments
- `2`: Task validation failed (missing/corrupted metadata)
- `3`: Network error after retries exhausted
- `4`: Server refused request (403/410)
- `5`: Storage path invalid or not writable
- `6`: Proxy connection failed
- `7`: Proxy authentication failed

## Differences from Danbooru Scraper

Zerochan scraper has some key differences:

1. **No Tag Categorization**: Zerochan doesn't categorize tags, so no tag metadata is stored
2. **JSON-LD Parsing**: Image URLs extracted from JSON-LD structured data instead of HTML elements
3. **Pagination Discovery**: Follows "next" links since total page count may not be displayed
4. **Keywords vs Tags**: Uses `--keywords` parameter instead of `--tags`

## Testing

Run the test suite to verify functionality:

```bash
python test_scraper.py
```

Tests include:
- URL construction from keywords
- Task folder sanitization
- Post ID extraction
- Post detail parsing

## Troubleshooting

### "Server refused request" Error

If you encounter HTTP 403 errors:
- Zerochan may be rate-limiting your IP
- Increase `--throttle` value (e.g., 5.0 seconds)
- Wait before resuming the task
- Consider using a proxy

### Proxy Connection Failed

If proxy validation fails:
- Verify proxy URL format: `http://host:port` or `socks5://host:port`
- Check proxy authentication credentials
- Test proxy connectivity outside the scraper

### No Posts Found

If search returns no posts:
- Verify keywords are spelled correctly
- Try searching on Zerochan website first
- Some keywords may have no results

## License

See project root for license information.
