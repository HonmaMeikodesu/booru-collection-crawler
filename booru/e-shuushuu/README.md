# E-Shuushuu Scraper

A command-line tool for downloading images and metadata from E-Shuushuu (https://e-shuushuu.net), a kawaii/moe anime image board.

## Features

- **Three Operation Modes**:
  - `new`: Create a new scraping task from scratch
  - `resume`: Resume an interrupted task
  - `sync`: Synchronize with remote server to fetch new posts

- **Robust Error Handling**:
  - Automatic retry with exponential backoff for transient network errors
  - Graceful handling of server refusals (403/410)
  - State persistence after each post download for easy recovery

- **Rate Limiting**: Configurable throttle mechanism to avoid triggering anti-crawler defenses

- **Proxy Support**: Full support for HTTP, HTTPS, and SOCKS5 proxies with authentication

- **In-Memory Downloads**: Images are downloaded completely before writing to disk to ensure data integrity

## Installation

Ensure you have Python 3.6+ and the required dependencies:

```bash
pip install requests beautifulsoup4
```

For SOCKS proxy support:

```bash
pip install PySocks
```

## Usage

### Create a New Task

Download all images for a specific tag ID:

```bash
python eshuushuu_scraper.py --mode new --tag-id 76604 --storage-path ./downloads
```

### Resume an Interrupted Task

If a task was interrupted, resume from where it left off:

```bash
python eshuushuu_scraper.py --mode resume --task-path ./downloads/tag_76604
```

### Sync an Existing Task

Update an existing task with new posts from the server:

```bash
python eshuushuu_scraper.py --mode sync --task-path ./downloads/tag_76604
```

### Advanced Options

**Custom throttle rate** (default: 2.5 seconds):
```bash
python eshuushuu_scraper.py --mode new --tag-id 76604 --storage-path ./downloads --throttle 3.0
```

**Custom retry attempts** (default: 3):
```bash
python eshuushuu_scraper.py --mode new --tag-id 76604 --storage-path ./downloads --max-retries 5
```

**Using a proxy**:
```bash
python eshuushuu_scraper.py --mode new --tag-id 76604 --storage-path ./downloads --proxy socks5://127.0.0.1:1080
```

**Using a proxy with authentication**:
```bash
python eshuushuu_scraper.py --mode new --tag-id 76604 --storage-path ./downloads --proxy http://proxy.com:8080 --proxy-auth user:pass
```

## Task Folder Structure

Each task creates a folder with the following structure:

```
tag_76604/
├── task_metadata.json    # Task status and progress information
├── post_list.json        # List of all posts with download status
└── posts/
    ├── 1060480.jpeg      # Downloaded image
    ├── 1060480_tags.json # Tag metadata for the image
    ├── 1055234.jpeg
    ├── 1055234_tags.json
    └── ...
```

### Task Metadata

The `task_metadata.json` file contains:

- `search_tag_id`: Tag ID used for the search
- `storage_path`: Base storage directory
- `task_folder`: Full path to task folder
- `created_at`: Task creation timestamp
- `last_updated`: Last update timestamp
- `last_synced`: Last sync timestamp (null if never synced)
- `status`: Current task status (PENDING, IN_PROGRESS, COMPLETE, FAILED)
- `total_posts`: Total number of posts discovered
- `completed_posts`: Number of successfully downloaded posts
- `mode_history`: List of modes executed on this task

### Post List

The `post_list.json` file is an array of post records:

```json
[
  {
    "post_id": 1060480,
    "status": "COMPLETE",
    "image_url": "https://e-shuushuu.net/images/2021-07-11-1060480.jpeg",
    "file_extension": "jpeg",
    "download_timestamp": "2023-12-15T10:30:45.123456"
  },
  ...
]
```

### Tag Metadata

Each `{post_id}_tags.json` file contains:

```json
{
  "post_id": 1060480,
  "tag": ["dress", "green eyes", "grey hair", "long hair", "ribbon"],
  "source": ["Anohana: The Flower We Saw That Day"],
  "character": ["Honma Meiko"],
  "artist": ["Ixy"]
}
```

## How It Works

### Tag ID Discovery

To find a tag ID for a character or theme:

1. Visit https://e-shuushuu.net
2. Search for your desired character/theme
3. The tag ID appears in the URL: `https://e-shuushuu.net/search/results/?tags=76604`
4. Use `76604` as the `--tag-id` parameter

### Pagination Strategy

The scraper automatically traverses all pages:

1. Starts with the first search results page
2. Extracts all post IDs from the current page
3. Looks for the "Next" pagination link
4. Continues until no more pages are found

### Download Process

For each post:

1. Fetch the post detail page
2. Extract the full-resolution image URL
3. Extract tag metadata (tags, source, character, artist)
4. Download the image into memory
5. Validate content integrity
6. Save image and tags to disk
7. Update task status

### Error Recovery

The scraper saves progress after each successful download. If interrupted:

- All completed downloads are preserved
- Task metadata reflects current progress
- Resume mode continues from the last incomplete post

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - task completed |
| 1 | Invalid command-line arguments |
| 2 | Task validation failed (corrupted files) |
| 3 | Unrecoverable network error |
| 4 | Server refused request (403/410) - manual intervention required |
| 5 | Storage path validation failed |
| 6 | Proxy connection failed |
| 7 | Proxy authentication failed |

## Testing

Run the test suite to validate functionality:

```bash
python test_scraper.py
```

The test suite validates:
- Post ID extraction from HTML
- Pagination link detection
- Task folder name sanitization
- URL construction

## Implementation Notes

### DOM Parsing

The scraper uses BeautifulSoup with CSS selectors to extract data:

- **Post containers**: `.image_thread.display`
- **Post IDs**: Extracted from `id` attribute (format: `i{post_id}`)
- **Image URLs**: From `.thumb_image` anchor tag's `href` attribute
- **Pagination**: Next link via `.pagination .next a`

### Rate Limiting

Default throttle of 2.5 seconds between requests helps avoid:
- Server-side rate limiting
- IP bans
- Anti-crawler triggers

Adjust the throttle based on your network and server response.

### Memory Efficiency

Images are downloaded one at a time to minimize memory usage:
- Only one image is held in memory at any given time
- Immediate disk write after download
- No concurrent downloads

## Troubleshooting

### Server Refused (403/410)

If you encounter a 403 or 410 error:

1. The task state is automatically saved
2. Wait a few minutes before resuming
3. Consider increasing the throttle rate
4. Use the resume mode to continue

### Module Not Found

If you get import errors, ensure you're in the correct directory:

```bash
cd e:\booru-collection-crawler\booru\e-shuushuu
python eshuushuu_scraper.py --mode new --tag-id 76604 --storage-path ./downloads
```

### Proxy Issues

For SOCKS5 proxies, install PySocks:

```bash
pip install PySocks
```

Test your proxy separately to ensure it works before using with the scraper.

## License

This scraper is part of the booru-collection-crawler project.

## Disclaimer

This tool is for educational purposes. Please respect E-Shuushuu's terms of service and use reasonable rate limits.
