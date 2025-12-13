# Zerochan Scraper - Quick Reference

## Installation

```bash
pip install -r requirements.txt
```

## Basic Usage

### New Task
```bash
python zerochan_scraper.py --mode new --keywords "Honma Meiko" --storage-path ./downloads
```

### Resume Task
```bash
python zerochan_scraper.py --mode resume --task-path ./downloads/honma_meiko
```

### Sync Task
```bash
python zerochan_scraper.py --mode sync --task-path ./downloads/honma_meiko
```

## Common Options

```bash
# With proxy
--proxy http://proxy.example.com:8080 --proxy-auth user:pass

# Custom throttle (slower requests)
--throttle 5.0

# More retries
--max-retries 5
```

## Task Folder Structure

```
honma_meiko/
├── task_metadata.json    # Task info and progress
├── post_list.json        # Post list with status
└── posts/                # Downloaded images
    ├── 2941468.jpg
    └── ...
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid arguments |
| 2 | Task validation failed |
| 3 | Network error |
| 4 | Server refused (403/410) |
| 5 | Storage error |
| 6 | Proxy connection failed |
| 7 | Proxy auth failed |

## Post Status Values

- `PENDING`: Not yet downloaded
- `IN_PROGRESS`: Currently downloading
- `COMPLETE`: Successfully downloaded
- `FAIL`: Download failed

## Testing

```bash
python test_scraper.py
```

## Tips

- Use longer `--throttle` values if encountering rate limiting
- Resume mode automatically triggers sync after download
- Proxy supports HTTP, HTTPS, and SOCKS5 protocols
- Folder names are auto-sanitized from keywords
