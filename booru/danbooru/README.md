# Danbooru Scraper

A command-line tool for downloading high-resolution images and metadata from Danbooru.

## Features

- **Tag-based Search**: Download all posts matching specified tags
- **Resume Support**: Continue interrupted downloads from breakpoint
- **Auto-sync**: Automatically synchronize completed tasks with new posts
- **Proxy Support**: Access Danbooru through HTTP/HTTPS/SOCKS5 proxies
- **Rate Limiting**: Respectful throttling to avoid server overload
- **Metadata Extraction**: Save all tags categorized by type (Artist, Copyright, Character, General, Meta)

## Installation

1. Install Python 3.7 or higher

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Mode 1: Create New Task

Download all posts matching specified tags:

```bash
python danbooru_scraper.py --mode new --tags "honma_meiko" --storage-path "E:\danbooru_downloads"
```

With multiple tags:
```bash
python danbooru_scraper.py --mode new --tags "honma_meiko ano_hi_mita_hana_no_namae_wo_bokutachi_wa_mada_shiranai." --storage-path "E:\danbooru_downloads"
```

With proxy:
```bash
python danbooru_scraper.py --mode new --tags "honma_meiko" --storage-path "E:\danbooru_downloads" --proxy "http://proxy.example.com:8080"
```

### Mode 2: Resume Incomplete Task

Continue an interrupted download:

```bash
python danbooru_scraper.py --mode resume --task-path "E:\danbooru_downloads\honma_meiko_abc123"
```

**Note**: After completing all pending downloads, resume mode automatically triggers a sync operation to download any new posts added since the task was created.

### Mode 3: Sync Completed Task

Update a completed task with new posts from the server:

```bash
python danbooru_scraper.py --mode sync --task-path "E:\danbooru_downloads\honma_meiko_abc123"
```

## Command-Line Arguments

### Required Arguments

| Mode | Argument | Description |
|------|----------|-------------|
| new | `--mode new` | Create a new download task |
| new | `--tags "tag1 tag2"` | Search tags (space or comma separated) |
| new | `--storage-path "path"` | Directory where task folder will be created |
| resume | `--mode resume` | Resume an incomplete task |
| resume | `--task-path "path"` | Path to existing task folder |
| sync | `--mode sync` | Sync a completed task |
| sync | `--task-path "path"` | Path to existing task folder |

### Optional Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--throttle 2.5` | 2.5 | Seconds between requests |
| `--max-retries 3` | 3 | Maximum retry attempts per request |
| `--proxy "url"` | None | Proxy server URL (HTTP/HTTPS/SOCKS5) |
| `--proxy-auth "user:pass"` | None | Proxy authentication credentials |

## Proxy Configuration

The scraper supports proxy servers for regions where Danbooru is blocked.

### Proxy URL Formats

- HTTP: `http://proxy.example.com:8080`
- HTTPS: `https://proxy.example.com:8443`
- SOCKS5: `socks5://proxy.example.com:1080`

### Proxy Authentication

Two methods are supported:

1. **Embedded in URL**:
```bash
--proxy "http://username:password@proxy.example.com:8080"
```

2. **Separate argument**:
```bash
--proxy "http://proxy.example.com:8080" --proxy-auth "username:password"
```

## Task Folder Structure

Each task creates a folder with the following structure:

```
storage_path/
└── sanitized_tags_hash/
    ├── task_metadata.json      # Task metadata and status
    ├── post_list.json           # List of all posts with download status
    └── posts/
        ├── 10337509.png         # Downloaded image
        ├── 10337509_tags.json   # Image tags metadata
        ├── 10243316.jpg
        ├── 10243316_tags.json
        └── ...
```

### Task Metadata (task_metadata.json)

Contains task information:
- Search tags
- Creation and update timestamps
- Task status
- Total posts count
- Completed posts count
- Mode history

### Post List (post_list.json)

Array of posts with:
- Post ID
- Download status (PENDING/COMPLETE/FAIL)
- Image URL
- File extension
- Download timestamp

### Tags Metadata (*_tags.json)

Per-post tag information:
- Artist tags
- Copyright tags
- Character tags
- General tags
- Meta tags

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid arguments |
| 2 | Task validation failed |
| 3 | Network error exhausted retries |
| 4 | Server refusal (403/410) |
| 5 | Storage path error |
| 6 | Proxy connection failed |
| 7 | Proxy authentication failed |

## Error Handling

### Server Refusal (403/410)

When Danbooru refuses a request, the scraper:
1. Saves current task state
2. Displays error details
3. Exits with code 4
4. Shows resume command

Resume with:
```bash
python danbooru_scraper.py --mode resume --task-path "path/to/task"
```

### Network Errors

Transient network errors are automatically retried with exponential backoff:
- Retry 1: 5 seconds delay
- Retry 2: 10 seconds delay
- Retry 3: 20 seconds delay

After 3 failed attempts, the post is marked as FAIL and the scraper continues to the next post.

## Rate Limiting

The scraper enforces a 2.5-second delay between requests by default to avoid triggering Danbooru's anti-crawler mechanisms.

Adjust with `--throttle`:
```bash
python danbooru_scraper.py --mode new --tags "tag" --storage-path "path" --throttle 3.0
```

## Examples

### Basic Download
```bash
python danbooru_scraper.py --mode new --tags "landscape" --storage-path "E:\images"
```

### Download with Proxy
```bash
python danbooru_scraper.py --mode new --tags "landscape" --storage-path "E:\images" --proxy "socks5://127.0.0.1:1080"
```

### Resume After Interruption
```bash
python danbooru_scraper.py --mode resume --task-path "E:\images\landscape_abc123"
```

### Sync for New Posts
```bash
python danbooru_scraper.py --mode sync --task-path "E:\images\landscape_abc123"
```

### Custom Throttle and Retries
```bash
python danbooru_scraper.py --mode new --tags "tag" --storage-path "E:\images" --throttle 3.0 --max-retries 5
```

## License

This tool is for personal use only. Please respect Danbooru's terms of service and usage policies.
