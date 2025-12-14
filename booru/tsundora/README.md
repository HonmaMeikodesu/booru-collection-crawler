# Tsundora Scraper

A web scraper for downloading images from [tsundora.com](https://tsundora.com), a high-quality anime wallpaper site.

## Features

- Search by keyword and download all matching posts
- Automatic pagination handling
- Download high-resolution images (removes size suffixes)
- Resume from breakpoint on failure
- Sync mode to fetch new posts
- Proxy support (HTTP/HTTPS/SOCKS5)
- Rate limiting to avoid anti-bot detection
- Automatic retry on network errors

## Installation

Ensure you have Python 3.7+ and required dependencies:

```bash
pip install -r ../../requirements.txt
```

## Usage

### New Task

Start a new scraping task with a keyword:

```bash
python tsundora_scraper.py --mode new --keyword "本間芽衣子" --storage-path "./downloads"
```

This will:
1. Create a task folder in the storage path
2. Fetch all post IDs matching the keyword
3. Download images and save metadata

### Resume Task

Resume an interrupted task:

```bash
python tsundora_scraper.py --mode resume --task-path "./downloads/keyword_task"
```

After completing the resume, it automatically syncs to fetch any new posts.

### Sync Task

Update a completed task with new posts:

```bash
python tsundora_scraper.py --mode sync --task-path "./downloads/keyword_task"
```

## Advanced Options

### Rate Limiting

Adjust throttle time between requests (default: 2.5 seconds):

```bash
python tsundora_scraper.py --mode new --keyword "test" --storage-path "." --throttle 3.0
```

### Max Retries

Set maximum retry attempts for failed requests (default: 3):

```bash
python tsundora_scraper.py --mode new --keyword "test" --storage-path "." --max-retries 5
```

### Proxy Support

Use a proxy server:

```bash
# HTTP/HTTPS proxy
python tsundora_scraper.py --mode new --keyword "test" --storage-path "." --proxy "http://proxy.example.com:8080"

# SOCKS5 proxy
python tsundora_scraper.py --mode new --keyword "test" --storage-path "." --proxy "socks5://127.0.0.1:1080"

# Proxy with authentication
python tsundora_scraper.py --mode new --keyword "test" --storage-path "." --proxy "http://proxy.example.com:8080" --proxy-auth "username:password"
```

## Task Folder Structure

```
keyword_task/
├── task_metadata.json      # Task metadata and status
├── post_list.json          # List of all posts with status
└── posts/                  # Downloaded images
    ├── 165099.jpg
    ├── 165100.jpg
    └── ...
```

## Key Differences from Safebooru Scraper

- **Search method**: Uses keyword search instead of tag-based search
- **URL format**: `https://tsundora.com/?s={keyword}` vs tag-based URLs
- **Post ID extraction**: Extracts from `.article_content .article-box a` href
- **Pagination**: Uses `.next.page-numbers` selector
- **Image URL**: Automatically removes size suffix (e.g., `-960x1024.jpg` → `.jpg`)
- **No tags**: Tsundora doesn't provide tag categorization

## Notes

- The scraper respects rate limits with a 2.5-second default throttle
- Images are downloaded at full resolution by removing size suffixes
- Japanese keywords are automatically URL-encoded
- All metadata is saved in JSON format for easy parsing

## Testing

Run unit tests:

```bash
python test_scraper.py
```

## Exit Codes

- `0`: Success
- `1`: Invalid arguments
- `2`: Task validation failed
- `3`: Network error
- `4`: Server refused request (403/410)
- `5`: Storage error
- `6`: Proxy connection failed
- `7`: Proxy authentication failed
