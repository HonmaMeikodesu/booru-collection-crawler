# Danbooru Scraper - Quick Reference Card

## Installation
```bash
pip install -r requirements.txt
```

## Basic Commands

### New Task
```bash
python booru\danbooru\danbooru_scraper.py --mode new --tags "TAG" --storage-path "PATH"
```

### Resume Task
```bash
python booru\danbooru\danbooru_scraper.py --mode resume --task-path "TASK_PATH"
```

### Sync Task
```bash
python booru\danbooru\danbooru_scraper.py --mode sync --task-path "TASK_PATH"
```

## Common Options

| Option | Default | Description |
|--------|---------|-------------|
| `--throttle 2.5` | 2.5 | Delay between requests (seconds) |
| `--max-retries 3` | 3 | Maximum retry attempts |
| `--proxy "URL"` | None | Proxy server (HTTP/HTTPS/SOCKS5) |
| `--proxy-auth "user:pass"` | None | Proxy authentication |

## Quick Examples

**Basic download:**
```bash
python booru\danbooru\danbooru_scraper.py --mode new --tags "landscape" --storage-path "E:\images"
```

**With proxy:**
```bash
python booru\danbooru\danbooru_scraper.py --mode new --tags "landscape" --storage-path "E:\images" --proxy "socks5://127.0.0.1:1080"
```

**Multiple tags:**
```bash
python booru\danbooru\danbooru_scraper.py --mode new --tags "honma_meiko dress" --storage-path "E:\images"
```

**Custom settings:**
```bash
python booru\danbooru\danbooru_scraper.py --mode new --tags "landscape" --storage-path "E:\images" --throttle 5.0 --max-retries 5
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

## Task Status

| Status | Description |
|--------|-------------|
| PENDING | Not yet downloaded |
| IN_PROGRESS | Currently downloading |
| COMPLETE | Successfully downloaded |
| FAIL | Download failed |

## Folder Structure

```
{storage_path}/
└── {sanitized_tags}/
    ├── task_metadata.json
    ├── post_list.json
    └── posts/
        ├── {post_id}.{ext}
        └── {post_id}_tags.json
```

## Troubleshooting

**Server refused (403/410):**
- Wait a few hours
- Use proxy: `--proxy "socks5://127.0.0.1:1080"`
- Increase throttle: `--throttle 5.0`

**Network errors:**
- Increase retries: `--max-retries 5`
- Check internet connection
- Try with proxy

**Proxy errors:**
- Exit code 6: Check proxy URL and connection
- Exit code 7: Check proxy credentials

## Resume After Error

After any error, resume with:
```bash
python booru\danbooru\danbooru_scraper.py --mode resume --task-path "PATH_SHOWN_IN_ERROR"
```

## Features

✓ Tag-based search  
✓ Pagination auto-discovery  
✓ High-resolution images  
✓ Complete tag metadata  
✓ Resume from breakpoint  
✓ Auto-sync after resume  
✓ Manual sync mode  
✓ Proxy support (HTTP/HTTPS/SOCKS5)  
✓ Rate limiting (configurable)  
✓ Automatic retry (3x with backoff)  
✓ State preservation  
✓ Progress tracking  

## Documentation Files

- **README.md** - Complete documentation
- **EXAMPLES.md** - Practical examples
- **IMPLEMENTATION_SUMMARY.md** - Technical details
- **QUICK_REFERENCE.md** - This file

## Testing

Run tests:
```bash
python booru\danbooru\test_scraper.py
```

## Support

For detailed documentation, see:
- [README.md](README.md) - Full user guide
- [EXAMPLES.md](EXAMPLES.md) - Usage examples
